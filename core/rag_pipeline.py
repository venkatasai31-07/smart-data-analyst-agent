import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

class RAGPipeline:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # We try modern embedding 004, but we will catch errors and fallback natively
        self.embeddings = GoogleGenerativeAIEmbeddings(api_key=api_key, model="models/text-embedding-004")
        self.llm = ChatGoogleGenerativeAI(temperature=0, api_key=api_key, model="gemini-2.5-flash")
        self.vector_store = None
        self.fallback_docs = []
        
    def build_index(self, df: pd.DataFrame, page_content_column: str = None):
        """
        Transforms dataframe into documents and builds FAISS index.
        If page_content_column is None, we combine all columns into a text representation.
        """
        # --- SPEED OPTIMIZATION ---
        if len(df) > 150:
            process_df = df.sample(150, random_state=42).copy()
        else:
            process_df = df.copy()

        if page_content_column is None:
            combined_df = process_df.copy()
            combined_df['text_repr'] = combined_df.apply(lambda row: ' | '.join([f"{col}: {val}" for col, val in row.items()]), axis=1)
            loader = DataFrameLoader(combined_df, page_content_column="text_repr")
        else:
            loader = DataFrameLoader(process_df, page_content_column=page_content_column)

        documents = loader.load()
        self.fallback_docs = documents[:20]  # Store top 20 rows for fallback
        
        # Build FAISS vector store, Catch 404 API restrictions
        try:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            return self.vector_store
        except Exception as e:
            logging.error(f"Embedding failed (likely API free-tier restriction). Falling back to direct context: {e}")
            self.vector_store = None
            return None

    def query(self, question: str, top_k: int = 5):
        """
        Executes a RAG query and returns response with explanations.
        """
        retrieved_docs = []
        if self.vector_store:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
            retrieved_docs = retriever.invoke(question)
        else:
            # Fallback direct ingestion 
            retrieved_docs = self.fallback_docs
            
        context = "\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        
        # Explainable AI Prompt
        template = """
        You are a helpful AI Data Analyst. You have retrieved data from a dataset to answer the user's question.
        
        Question: {question}
        
        Retrieved Context:
        {context}
        
        Provide a detailed answer based ONLY on the provided context. If the context does not contain the answer, say you don't know based on the current data.
        
        In your response, format it as follows:
        **Answer**: <your answer>
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({"question": question, "context": context})
        except Exception as e:
            response = f"LLM Generation Error: {str(e)}"
            
        return {
            "answer": response,
            "explanations": [doc.page_content for doc in retrieved_docs]
        }
