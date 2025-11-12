# company_policy_chatbot
A RAG chatbot that can answer questions related to company policies


# Step -1
- Creage virtual environment
    python -m venv chatbot_env 
    source chatbot_env/bin/activate # activate for mac
- Setup the setup.py for creating packages
- Add necessary libraries and tools in requirements.txt
- Intall the libraries and create folder as local packages 


# Step -2
- Define the logging and exception 
- set the Openai LLM key in .env file 
- set the necessary confiquration in config file


# Step -3 
- Collect the data from google, a company policy manual pdf file
- Manually create it, leave, remoreto work policy data file as .txt format


# Step -4
- implement the multiple documents loader method
- implemented splitter and embeddings functionality
- Implement faiss vector store operations-> creat_index, add_documents, search, save_index, load_index

# Step -5 
- Retrieve the data from vectorstore 
- generate response 
- Store the concersation history in memory_manager.py

# Step -6
- generate fastapi endpoints
