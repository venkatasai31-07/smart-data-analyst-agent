import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

class DataProcessor:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(temperature=0, api_key=api_key, model="gemini-2.5-flash")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Performs basic data cleaning: null imputation and basic coercion."""
        # Create a copy so we don't modify the original during processing unintentionally
        cleaned_df = df.copy()
        
        # Fill numeric nulls with mean
        numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
            
        # Fill categorical nulls with mode
        cat_cols = cleaned_df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            if not cleaned_df[col].mode().empty:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
            else:
                cleaned_df[col] = cleaned_df[col].fillna("Unknown")
                
        return cleaned_df

    def generate_automated_insights(self, df: pd.DataFrame) -> str:
        """Uses LLM to generate automated insights like trends and outliers."""
        # Get basic stats to feed to LLM
        summary_stats = df.describe(include='all').to_string()
        head_data = df.head(3).to_string()
        columns_info = list(df.columns)
        
        prompt = PromptTemplate(
            input_variables=["columns", "head", "summary"],
            template="""
            You are an expert AI Data Analyst. I have uploaded a dataset.
            Here are the columns: {columns}
            
            First 3 rows:
            {head}
            
            Summary statistics:
            {summary}
            
            Please provide a brief, professional summary of the automated insights. 
            Highlight any potential top trends, outliers, or key observations. 
            Keep it under 3 paragraphs and use bullet points for clarity.
            """
        )
        
        chain = prompt | self.llm
        response = chain.invoke({"columns": columns_info, "head": head_data, "summary": summary_stats})
        return response.content

    def analyze_query(self, df: pd.DataFrame, query: str) -> str:
        """Answers statistical/analytical queries using pandas summary stats."""
        summary_stats = df.describe(include='all').to_string()
        
        prompt = PromptTemplate(
            input_variables=["summary", "query"],
            template="""
            You are an expert AI Data Analyst.
            The user has asked an analytical question: "{query}"
            
            Here are the summary statistics of the dataset computed using Pandas:
            {summary}
            
            Based ONLY on the provided pandas statistics, answer the user's question.
            Provide the answer clearly and concisely.
            """
        )
        chain = prompt | self.llm
        response = chain.invoke({"summary": summary_stats, "query": query})
        return response.content
