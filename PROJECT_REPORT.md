# 🤖 Smart Data Analyst Agent - Final Project Report

## 📌 Project Overview
The **Smart Data Analyst Agent** is a production-level AI application designed to transform raw CSV datasets into actionable business intelligence. It combines **Conversational AI (RAG)**, **Automated Statistical Analysis**, and **Interactive Visualizations** into a single, professional dashboard.

---

## 🚀 Key Features

### 🍱 1. Multi-Task Professional Dashboard
The application is organized into a modular, tab-based interface for a clean user experience:
- **📊 Executive Dashboard**: Instant high-level KPI metrics (Total Rows, Averages) and Automated AI Insights.
- **📈 Visual Intelligence**: Auto-generated Plotly trend charts and an interactive chart builder.
- **💬 AI Agent (Conversational RAG)**: A chat interface that understands user intent to perform row-level lookups or complex data reasoning.
- **📑 Record Explorer**: A searchable and filterable view of the full dataset with a CSV export feature.
- **📋 Professional PDF Export**: One-click generation of a comprehensive analytical report containing AI summaries, metrics, and high-resolution chart snapshots.

### 🧠 2. Intelligent Query Routing
The system uses an LLM-based **Query Router** to dynamically select the best processing pipeline:
- **Visualization Intent** → Triggers the Plotly Engine.
- **Analytical Intent** → Triggers the Pandas Statistical Pipeline.
- **Retrieval Intent** → Triggers the RAG (Retrieval-Augmented Generation) pipeline.

### 🌑 3. "Corporate Dark" UI/UX
- Custom CSS-injected theme for a premium, sleek aesthetic.
- Feature toggles in the sidebar for modular deployment.
- Pro-active loading states, toasts, and "Empty State" splash screens.

---

## 🛠️ Technology Stack
- **Frontend**: Streamlit
- **Intelligence**: Google Gemini-2.5-Flash (Free Tier Optimized)
- **Framework**: LangChain
- **Vector Store**: FAISS
- **Data Engine**: Pandas & Plotly

---

## 📥 How to Run
1. **Activate Environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. **Set API Key**:
   Ensure `GOOGLE_API_KEY` is set in your `.env` file.
3. **Launch Dashboard**:
   ```powershell
   streamlit run app.py
   ```

---

## ✅ Final Status
The project is **fully functional**, **free-tier optimized**, and **portfolio-ready**.
