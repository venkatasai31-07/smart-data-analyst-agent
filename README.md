# Smart Data Analyst Agent

An intelligent, context-aware AI agent that transforms datasets into actionable insights. This project moves beyond a basic chatbot by combining Retrieval-Augmented Generation (RAG), LLM reasoning, and modular pipelines to execute complex data analysis tasks. 

## Features

- **Intelligent Query Routing**: Dynamically classifies user intent. Keywords trigger specific operational pipelines (e.g., Visualization vs. EDA vs. Advanced RAG Retrieval).
- **Automated Insight Generation**: Post-upload LLM-based reasoning automatically unpacks top trends, outliers, and key observations right away.
- **Explainable AI Responses**: Displays step-by-step transparency layers to explain how retrieved subsets contribute to answers.
- **Conversational Memory**: Retains the chat history in LangChain memory for context-aware multi-turn follow-ups.
- **Advanced RAG Enhancements**: Top-K similarity matching, optimized semantic chunking, and precise context filtering tailored for tabular data constraints.

## Architecture & End-to-End Workflow

1. User uploads dataset (`.csv`).
2. Data is cleaned and transformed into text representations.
3. Embeddings are generated and stored in a FAISS vector index.
4. User query is classified using intelligent query routing.
5. Relevant data is retrieved using top-K similarity search or directed to visualization/EDA pipelines.
6. The LLM generates a contextual response, optionally triggering visualization engines.
7. Explanations, insights, and interactive visualizations are displayed.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory and add your Google API Key:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
