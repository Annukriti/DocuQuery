DocuQuery : Smart Document Assistant                                                                                                                                                      

Docker image:

Admin side                                                                                                                              
docker build -t pdf-reader-admin .                                                                                                                                                      
docker run -e BUCKET_NAME=annu-chat-bot-demo -v C:\Users\annuk\.aws:/root/.aws -p 8083:8083 -it pdf-reader-admin                                                                                                                              

User side                                                                                                                              
docker build -t pdf-reader-client .                                                                                                                              
docker run -e BUCKET_NAME=annu-chat-bot-demo -v C:\Users\annuk\.aws:/root/.aws -p 8084:8084 -it pdf-reader-client                                                                                                                             

--------

Configure AWS:
1. Install AWS CLI                                                                                                                              
2. Create IAM user                                                                                                                              
3. Run below commands                                                                                                                              
   - aws --version                                                                                                                              
   - aws configure (put access key and secret access key)                                                                                                                              
4. Specify IAM Policy for the IAM User                                                                                                                              

----------

Tech used:                                                                                                                              
Streamlit – Used to build the interactive web app interface                                                                                                                                                                               
AWS Bedrock - Used to access foundational models (LLMs and embedding models)                                                                                                                                                                 
AWS S3 - Used to download the FAISS index and metadata from cloud storage                                                                                                                                                                 
LangChain - Framework for combining LLMs with external data sources, prompts, chains, etc.                                                                                                                                                   
       - Bedrock (LLM): Interface to invoke Claude model.                                                                                                                                                                 
       - BedrockEmbeddings: To embed text using Amazon Titan model.                                                                                                                                                                 
       - PromptTemplate: To define the format of the prompt.                                                                                                                                                                 
       - RetrievalQA: To combine the LLM with a vector store for RAG.                                                                                                                                                                 
       - RecursiveCharacterTextSplitter: For breaking long documents into chunks.                                                                                                                                                            
       - FAISS: Open-source vector database used for storing and retrieving text embeddings.                                                                                                                                                  
       - PyPDFLoader: Utility for loading and parsing PDFs.                                                                                                                                                                 

Models used:                                                                                                                                                      
Amazon Titan Embeddings - Used to convert PDF text chunks into dense vector representations for similarity search                                                                                                                            
Anthropic Claude - Used as the main LLM to answer questions based on retrieved document context

----------

Architecture / Flow (RAG):

PDFs → Text (via loader, assumed external)                                                                                                                                                                                 
Text → Embeddings (Titan) → Stored in FAISS                                                                                                                                                                                 
User Question → Embed + Search Similar Chunks (FAISS)                                                                                                                                                                                 
Relevant Context + Prompt → Claude LLM (via Bedrock)                                                                                                                                                                                 
Claude LLM → Final Answer                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                                                                                  
[PDF] → (Embeddings via Titan) → [FAISS Index] → (Stored in S3)                                                                                                                                                                               

[User Question]                                                                                                                                                                                 
    ↓                                                                                                                                                                                 
Embedding + Similarity Search (FAISS)                                                                                                                                                                                 
    ↓                                                                                                                                                                                 
Top-K Relevant Chunks (Context)                                                                                                                                                                                 
    ↓                                                                                                                                                                                 
Prompt Construction (LangChain)                                                                                                                                                                                 
    ↓                                                                                                                                                                                 
LLM Query (Claude v2.1 via Bedrock)                                                                                                                                                                                                                                                                                                                                                                  
    ↓                                                                                                                                                                                 
Final Answer → Display via Streamlit                                                                                                                                                                                 


Why user interacts with embeddings ?
Embeddings allow you to convert the text from the PDF into numerical representations that capture the meaning of the content in a way that is machine-readable.
These embeddings are essentially high-dimensional vectors, where each document or text chunk is mapped into a vector space.
For example, words like “dog” and “puppy” will have similar embeddings because they are related in meaning.

The embeddings in the FAISS index allow you to quickly retrieve the most relevant documents (or chunks of text) that are semantically similar to a given query.

“What is the capital of France?” and your document contains the answer “Paris is the capital of France,”
the embeddings of these two will be similar enough that FAISS can retrieve the relevant chunk.

----------
RAG 
- It's an AI architecture that combines information retrieval with text generation to improve the quality and accuracy of responses from large language models (LLMs).
  
How RAG Works:                                                                                   
Query Input: A user asks a question.                                                                                   
Retrieval: The system searches a knowledge base (e.g., documents, PDFs, databases) to find the most relevant text chunks or passages.                                                                                   
Augmentation: These retrieved texts are then passed along with the user query to the LLM.                                                                                   
Generation: The LLM uses both the query and the retrieved content to generate a response.                                                                                   

Tools Used in RAG Pipelines:                                                                                   
Embedding Models (like OpenAI, Cohere, AWS Bedrock) for vectorizing text.                                                                                   
Vector Stores (like FAISS, Pinecone) for similarity search.                                                                                   
LLMs (like GPT, Claude) for generating responses.                                                                                   

----------

Demo of my work - https://www.youtube.com/watch?v=SANz64vQ72Y                                                 
Reference - https://www.youtube.com/watch?v=KFibP7KnDVM
