import boto3
import streamlit as st
import os
import uuid

# s3_client
s3_client = boto3.client("s3")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Bedrock
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

# Import prompt template and RetrievalQA chain from Langchain
# PromptTemplate - use to define and structure prompts that are sent to lang models like GPT/Anthropic Claude
from langchain.prompts import PromptTemplate
# RetrievalQA - combines retriever(vector db) with lang model to answer ques based on retrieved docs
from langchain.chains import RetrievalQA

# import FAISS
from langchain_community.vectorstores import FAISS

bedrock_client = boto3.client(service_name="bedrock-runtime")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

folder_path="/tmp/"

# load index - download FAISS index and metadata files from S3
def load_index():
    s3_client.download_file(Bucket=BUCKET_NAME, Key="my_faiss.faiss", Filename=f"{folder_path}my_faiss.faiss")
    s3_client.download_file(Bucket=BUCKET_NAME, Key="my_faiss.pkl", Filename=f"{folder_path}my_faiss.pkl")

#  Return a Bedrock language model (Claude-v2) for generating answers
def get_llm():
    llm=Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client,
                model_kwargs={'max_tokens_to_sample': 512})
    return llm

# get_response()
def get_response(llm,vectorstore, question ):
    #  Define the prompt template with context and question
    prompt_template = """

    Human: Please use the given context to provide concise answer to the question
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    <context>
    {context}
    </context>

    Question: {question}

    Assistant:"""

    # Initialize a Langchain prompt template
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Create a RetrievalQA chain with the LLM, retriever(vector db), and prompt
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    # Query the chain and return the result part of the response
    answer=qa({"query":question})
    return answer['result']


# main method
def main():
    st.header("Query you document.")

    load_index()

    # List the contents of the temporary folder for debugging
    # dir_list = os.listdir(folder_path)
    # st.write(f"Files and Directories in {folder_path}")
    # st.write(dir_list)

    # Load the FAISS index with the downloaded files
    faiss_index = FAISS.load_local(
        index_name="my_faiss",
        folder_path = folder_path,
        embeddings=bedrock_embeddings,
        allow_dangerous_deserialization=True
    )

    # st.write("INDEX IS READY")
    question = st.text_input("Please ask your question.")
    if st.button("Ask Question"):
        with st.spinner("Querying..."):

            # Get an instance of the language model
            llm = get_llm()

            # get_response
            st.write(get_response(llm, faiss_index, question))
            st.success("Done")

if __name__ == "__main__":
    main()