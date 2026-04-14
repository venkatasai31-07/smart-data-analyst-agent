from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import io
import json
from dotenv import load_dotenv

from core.data_processor import DataProcessor
from core.visualization import VisualizationEngine
from core.rag_pipeline import RAGPipeline
from core.router import QueryRouter
from core.report_generator import generate_pdf_report

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global store for demo purposes 
global_store = {
    "df": None,
    "processor": None,
    "rag": None,
    "insights": None,
}

def run_ai_pipelines(df: pd.DataFrame, enable_rag: bool):
    try:
        if global_store.get("processor"):
            global_store["insights"] = "Generating AI insights, this may take a few moments..."
            insights = global_store["processor"].generate_automated_insights(df)
            global_store["insights"] = insights
    except Exception as e:
        global_store["insights"] = f"Failed to generate insights: {e}"
        
    if enable_rag:
        try:
            rag = RAGPipeline(api_key=API_KEY)
            rag.build_index(df)
            global_store["rag"] = rag
        except Exception as e:
            print(f"RAG Error: {e}")

@app.post("/api/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_cleaning: bool = Form(True),
    enable_rag: bool = Form(True)
):
    try:
        contents = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        processor = DataProcessor(api_key=API_KEY)
        
        if enable_cleaning:
            df = processor.clean_data(df)
            
        global_store["df"] = df
        global_store["processor"] = processor
        global_store["insights"] = "Analysis in progress..."
        
        # Fire AI pipelines in the background to unblock UI instantly
        background_tasks.add_task(run_ai_pipelines, df, enable_rag)
            
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()
        
        missing_penalty = (missing_cells / total_cells) * 100 if total_cells else 0
        duplicate_penalty = (duplicate_rows / len(df)) * 50 if len(df) else 0
        health_score = max(0, 100 - missing_penalty - duplicate_penalty)
        
        return {
            "status": "success",
            "metrics": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "health_score": round(health_score),
                "missing_cells": int(missing_cells),
                "duplicate_rows": int(duplicate_rows)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
def get_insights():
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded yet.")
    try:
        overview_charts_raw = VisualizationEngine.generate_overview_charts(df)
        charts = [{"name": n, "figure": json.loads(f.to_json())} for n, f in overview_charts_raw]
            
        return {
            "insights_text": global_store.get("insights", "No insights generated."),
            "charts": charts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(prompt: str = Form(...)):
    df = global_store["df"]
    processor = global_store["processor"]
    if df is None or processor is None: raise HTTPException(status_code=400, detail="No data uploaded yet.")
    try:
        router = QueryRouter(api_key=API_KEY)
        intent_data = router.classify_intent(prompt, list(df.columns))
        intent = intent_data.get("intent", "RAG Retrieval")
        response_data = {"intent": intent, "answer": "", "chart": None}
        
        if intent == "Visualization":
            fig = VisualizationEngine.generate_chart(
                df, intent_data.get("chart_type"), intent_data.get("x_col"), intent_data.get("y_col"), title=prompt
            )
            response_data["answer"] = f"Visualized query: {prompt}"
            if fig: response_data["chart"] = json.loads(fig.to_json())
        elif intent == "Analytical":
            response_data["answer"] = processor.analyze_query(df, prompt)
        else:
            rag = global_store.get("rag")
            response_data["answer"] = rag.query(prompt).get('answer', 'Got an error') if rag else "RAG is disabled."
                
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data")
def get_data(page: int = 1, limit: int = 50, search: str = ""):
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    filtered_df = df
    if search:
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
    start = (page - 1) * limit
    export_df = filtered_df.iloc[start:start+limit].copy().fillna("")
    return {
        "total": len(filtered_df), "page": page, "limit": limit,
        "columns": list(df.columns), "records": export_df.to_dict(orient="records")
    }

# ==========================================
# EDA & DATA EXPORT ENDPOINTS
# ==========================================

@app.get("/api/dataset/info")
def get_dataset_info():
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    
    # Missing values
    missing = df.isnull().sum().to_dict()
    # Dtypes
    dtypes = df.dtypes.astype(str).to_dict()
    # Head
    head = df.head(5).fillna("").to_dict(orient="records")
    
    return {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "missing": missing,
        "dtypes": dtypes,
        "head": head,
        "columns": list(df.columns)
    }

class CleanRequest(BaseModel):
    action: str
    column: str = None

@app.post("/api/eda/clean")
def clean_data(req: CleanRequest):
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    
    try:
        if req.action == "Drop Duplicates":
            global_store["df"] = df.drop_duplicates()
        elif req.action == "Drop Missing Rows":
            if req.column:
                global_store["df"] = df.dropna(subset=[req.column])
            else:
                global_store["df"] = df.dropna()
        elif req.action == "Fill Mean" and req.column:
            if pd.api.types.is_numeric_dtype(df[req.column]):
                global_store["df"][req.column] = df[req.column].fillna(df[req.column].mean())
        elif req.action == "Fill Mode" and req.column:
            if not df[req.column].mode().empty:
                global_store["df"][req.column] = df[req.column].fillna(df[req.column].mode()[0])
        elif req.action == "Drop Column" and req.column:
            global_store["df"] = df.drop(columns=[req.column])
        
        return {"status": "success", "message": f"Applied {req.action}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PlotRequest(BaseModel):
    type: str # histogram, boxplot, scatter
    x_col: str
    y_col: str = None

@app.post("/api/eda/visualize")
def visualize_data(req: PlotRequest):
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    import plotly.express as px
    try:
        if req.type == "histogram":
            fig = px.histogram(df, x=req.x_col, title=f"Histogram of {req.x_col}")
        elif req.type == "boxplot":
            fig = px.box(df, x=req.x_col, y=req.y_col, title=f"Boxplot")
        elif req.type == "scatter":
            fig = px.scatter(df, x=req.x_col, y=req.y_col, title=f"Scatter {req.x_col} vs {req.y_col}")
        elif req.type == "bar":
            val_counts = df[req.x_col].value_counts().reset_index()
            val_counts.columns = [req.x_col, 'count']
            fig = px.bar(val_counts, x=req.x_col, y='count', title=f"Bar Chart of {req.x_col}")
        else:
            raise ValueError("Unsupported Chart Type")
            
        return {"chart": json.loads(fig.to_json())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/csv")
def download_csv():
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=processed_dataset.csv"
    return response

@app.get("/api/download/pdf")
def download_pdf():
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    try:
        all_overview_charts = VisualizationEngine.generate_overview_charts(df)
        pdf_bytes = generate_pdf_report(df, global_store.get("insights", ""), all_overview_charts)
        response = Response(content=pdf_bytes, media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=analytical_report.pdf"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class OutlierRequest(BaseModel):
    column: str

@app.post("/api/eda/outliers")
def remove_outliers(req: OutlierRequest):
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    
    col = req.column
    if not pd.api.types.is_numeric_dtype(df[col]):
        raise HTTPException(status_code=400, detail="Column must be numeric for IQR.")
        
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    before = len(df)
    global_store["df"] = df[(df[col] >= lower) & (df[col] <= upper)]
    after = len(global_store["df"])
    
    return {"status": "success", "message": f"Removed {before - after} outliers from {col}."}

class EngineerRequest(BaseModel):
    action: str # Encode, Scale
    column: str

@app.post("/api/eda/engineer")
def feature_engineer(req: EngineerRequest):
    df = global_store["df"]
    if df is None: raise HTTPException(status_code=400, detail="No data uploaded.")
    
    try:
        if req.action == "Encode":
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            global_store["df"][f"{req.column}_encoded"] = le.fit_transform(df[req.column].astype(str))
        elif req.action == "Scale MinMax":
            if pd.api.types.is_numeric_dtype(df[req.column]):
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
                global_store["df"][f"{req.column}_scaled"] = scaler.fit_transform(df[[req.column]])
        elif req.action == "Scale Standard":
            if pd.api.types.is_numeric_dtype(df[req.column]):
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                global_store["df"][f"{req.column}_standardized"] = scaler.fit_transform(df[[req.column]])
        
        return {"status": "success", "message": f"Applied {req.action} to {req.column}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

