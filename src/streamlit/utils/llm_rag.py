import os
import yaml
import glob
import re
import shutil
import json
import faiss
from dotenv import load_dotenv
import logging
import streamlit as st
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from news_scraper import NewsScraper

# Set resource paths
cwd = os.path.dirname(os.path.abspath(__file__))
cfg_path = os.path.join(cwd, '..', '..', '..', 'cfg', 'oai.yaml')
cfg_news_path = os.path.join(cwd, '..', '..', '..', 'cfg', 'newsapi.yaml')
data_tmp = os.path.join(cwd, '..', 'data', 'tmp')

# Define LLM RAG Class Object
class LLMRag():
    '''Class object to pull data, process text articles, build a vector database,
        query the database, and interact with the LLM model.

    '''
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._openai_api_key = st.secrets['oapi_key']
        #self._openai_api_key = self._load_api_key()
        self._faiss_index_path = os.path.join(data_tmp, "faiss_index")
        self._db = None


    def _load_api_key(self):
        try:
            with open(cfg_path, 'rb') as file:
                return yaml.full_load(file)['key']
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {cfg_path}.")
        except KeyError:
            raise KeyError("The configuration file is missing the 'key' field.")


    def _most_recent_data(self) -> str:
        '''Load the most recent data file
        '''

        avail_data = glob.glob(r'covid_hosp*.json', root_dir = data_tmp)
        data_dates = [re.search(r'\d{4}-\d{2}-\d{2}', x).group() for x in avail_data]
        max_date = max(data_dates)
        ind = data_dates.index(max_date)
        most_recent = avail_data[ind]

        if not most_recent:
            raise FileNotFoundError("No COVID hospitalization data files found.")
        
        self._most_recent = most_recent
        self.logger.info(f"Most recent file: {most_recent}")
        return most_recent
    

    def _initialize_embeddings(self):
        return OpenAIEmbeddings(api_key=self._openai_api_key, model="text-embedding-3-small")


    def _initialize_faiss(self):
        embeddings = self._initialize_embeddings()
        embedding_dim = len(embeddings.embed_query("dummy text"))
        index = faiss.IndexFlatL2(embedding_dim)
        return FAISS(embedding_function = embeddings, 
                     index = index,
                     docstore = InMemoryDocstore(),
                     index_to_docstore_id = {}
                     )


    def _create_vectordb(self):
        '''Use the most recent news stories and meta-data to build a vector database
        '''

        # Load most recent data file
        most_recent = self._most_recent_data()
        with open(os.path.join(data_tmp, most_recent), 'r', encoding='utf-8') as f:
            documents = json.load(f)

        # Initialize the vectorstore
        db = self._initialize_faiss()

        # Initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Maximum characters per chunk
            chunk_overlap=200  # Overlap between chunks for better context preservation
        )

        # Process each document, split into chunks, embed, and store in FAISS
        vs_docs = []
        ids = []
        id_counter = 0  # Unique ID counter for all chunks

        for doc in documents:
            text = doc["content"]  # Assuming 'content' holds the main text
            metadata = {"title": doc["title"], "url": doc["url"]}

            # Split the document into chunks
            chunks = text_splitter.split_text(text)

            # Create Document objects for each chunk with metadata
            for chunk_index, chunk in enumerate(chunks):
                vs_doc = Document(
                    page_content=chunk,
                    metadata={**metadata, "chunk_index": chunk_index}
                )
                vs_docs.append(vs_doc)
                ids.append(id_counter)
                id_counter += 1

        # Add all chunked documents to the FAISS vector store
        db.add_documents(vs_docs, ids=ids)

        # Save the updated FAISS index
        if os.path.exists(self._faiss_index_path):
            # Remove if it already exists
            shutil.rmtree(self._faiss_index_path)

        # Save
        db.save_local(self._faiss_index_path)
        self._db = db


    def update_vectordb(self):
        '''Scrape news articles to update the VectorDB
        '''

        # Scrape new data
        ns = NewsScraper(config_path=cfg_news_path, data_tmp= data_tmp)
        ns.fetch_and_save_articles()

        # Update the vector db
        self._create_vectordb()


    def _load_vectordb(self):
        ''' If vectordb was not updated, load the existing
        '''

        if self._db:
            pass
        elif os.path.exists(self._faiss_index_path):
            embeddings = self._initialize_embeddings()
            self._db = FAISS.load_local(self._faiss_index_path, embeddings, allow_dangerous_deserialization=True)


    def prep_retrieval(self):
        '''Load VectorDB and build retrieval pipeline chain
        '''

        # Will load data if it wasn't already updated and loaded
        self._load_vectordb()

        # Build retrieval chain
        retriever = self._db.as_retriever()
        llm = ChatOpenAI(api_key = self._openai_api_key, model_name='gpt-3.5-turbo', temperature=0.5)
        self.retrieval_qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)


    def run_query(self, query : str) -> dict:
        """Runs the given query using the provided retrieval QA chain."""
        result = self.retrieval_qa_chain.invoke(query)

        return result


if __name__ == '__main__':

    test = LLMRag()
    test.update_vectordb() # Optional
    test.prep_retrieval()
    output = test.run_query('is covid getting better in the USA?')
    print(output)