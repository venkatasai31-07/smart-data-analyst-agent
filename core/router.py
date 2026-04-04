from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

class QueryRouter:
    def __init__(self, api_key: str):
        # Gemini does not natively enforce JSON mode like GPT-3.5 with response_format in the same way kwargs,
        # but the prompt handles it well. Removing the model_kwargs.
        self.llm = ChatGoogleGenerativeAI(temperature=0, api_key=api_key, model="gemini-2.5-flash")
        
    def classify_intent(self, question: str, columns: list) -> dict:
        """
        Classifies the user's question into one of three categories:
        1. Analytical (math/aggregation bounds)
        2. Visualization (plots/charts)
        3. RAG Retrieval (contextual text lookup)
        
        Returns a JSON with 'intent', 'chart_type' (if Visualization), 'x_col', 'y_col'.
        """
        template = """
        You are an intelligent routing agent for a data analysis system.
        The dataset has the following columns: {columns}
        
        Classify the user's query into one of three intents:
        1. 'Visualization': The user wants a chart, plot, or graph.
        2. 'Analytical': The user is asking for math, aggregations, max, min, average, or specific calculated metrics over the entire data.
        3. 'RAG Retrieval': The user is asking for specific row lookups, contextual text details, or general questions about specific entities (e.g., "what is the salary of E001").
        
        Respond with ONLY a JSON object with the following keys:
        - "intent": "Visualization" | "Analytical" | "RAG Retrieval"
        - "chart_type": For Visualization only. e.g., "bar", "scatter", "line", "pie", "histogram", "box". Otherwise null.
        - "x_col": Best guess for X axis column if Visualization. Must be exactly one of the columns or null.
        - "y_col": Best guess for Y axis column if Visualization. Must be exactly one of the columns or null.
        
        User Query: {question}
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({"question": question, "columns": columns})
        try:
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_response)
        except Exception as e:
            # Fallback
            return {"intent": "RAG Retrieval", "chart_type": None, "x_col": None, "y_col": None}

