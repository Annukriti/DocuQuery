import boto3 # AWS SDK for python
import streamlit as st # Web App Framework for UI
import os
import uuid


# Check if AWS credentials are configured
try:
    sts = boto3.client('sts') # Security Token Service Client to verify identity
    response = sts.get_caller_identity()
    print("AWS Credentials are correctly configured:", response)
except Exception as e:
    print("Error accessing AWS:", e)

# s3_client
s3_client = boto3.client("s3") # S3 Client to interact with aws s3
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Bedrock embeddings via langchain - used to turn text into numerical vectors
from langchain_community.embeddings import BedrockEmbeddings

# Text Splitter to chunk document into smaller parts
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Pdf Loader
from langchain_community.document_loaders import PyPDFLoader

# Import FAISS - vector db - store vector and use to do similarity search
# FAISS (Facebook AI Similarity Search)
from langchain_community.vectorstores import FAISS

# Client to access AWS Bedrock endpoint
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

# Instantiate Titan Model of Bedrock
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

def get_unique_id():
    return str(uuid.uuid4())


# Split the pages / text into chunks
def split_text(pages, chunk_size, chunk_overlap):
    # to ensure each chunk  overlap next chunk with few characters for context continuity
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # split pages into documents
    docs = text_splitter.split_documents(pages)
    return docs

# create vector store and save it based on requestid
def create_vector_store(request_id, documents):
    # convert document into embedding and create FAISS index
    vectorstore_faiss=FAISS.from_documents(documents, bedrock_embeddings)
    file_name=f"{request_id}.bin"
    folder_path="/tmp/"
    # saves the FAISS index as .faiss and .pkl files locally
    vectorstore_faiss.save_local(index_name=file_name, folder_path=folder_path)

    # upload to S3
    s3_client.upload_file(Filename=folder_path + "/" + file_name + ".faiss", Bucket=BUCKET_NAME, Key="my_faiss.faiss")
    s3_client.upload_file(Filename=folder_path + "/" + file_name + ".pkl", Bucket=BUCKET_NAME, Key="my_faiss.pkl")

    return True

# main method
def main():
    st.header("Upload the document for querying.")
    uploaded_file = st.file_uploader("Choose a file", "pdf")
    if uploaded_file is not None:
        request_id = get_unique_id()
        # display request id for tracking
        st.write(f"Request Id: {request_id}")

        # save uploaded pdf to disk
        saved_file_name = f"{request_id}.pdf"
        with open(saved_file_name, mode="wb") as w:
            w.write(uploaded_file.getvalue())

        # load pdf and split into pages
        loader = PyPDFLoader(saved_file_name)
        pages = loader.load_and_split()

        st.write(f"Total Pages: {len(pages)}")

        # Split pages into documents
        splitted_docs = split_text(pages, 1000, 200)
        # st.write(f"Splitted Docs length: {len(splitted_docs)}")
        # st.write("===================")
        # st.write(splitted_docs[0])
        # st.write("===================")
        # st.write(splitted_docs[1])

        st.write("Creating the Vector Store")
        result = create_vector_store(request_id, splitted_docs)

        if result:
            st.write("Hurray!! PDF processed successfully")
        else:
            st.write("Error!! Please check logs.")



if __name__ == "__main__":
    main()