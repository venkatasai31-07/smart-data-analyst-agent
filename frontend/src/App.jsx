import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Activity, MessageSquare, Database, FileSpreadsheet, Settings, Sparkles, ChevronRight, Cpu } from 'lucide-react';
import Dashboard from './components/Dashboard';
import ChatAgent from './components/ChatAgent';
import DataExplorer from './components/DataExplorer';
import EdaStudio from './components/EdaStudio';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isUploading, setIsUploading] = useState(false);
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const [enableCleaning, setEnableCleaning] = useState(true);
  const [enableRag, setEnableRag] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState("");

  const handleFileProcess = async (file) => {
    if (!file) return;
    setFileName(file.name);
    setIsUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('enable_cleaning', enableCleaning);
    formData.append('enable_rag', enableRag);

    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMetrics(res.data.metrics);
      setIsDataLoaded(true);
    } catch (error) {
      console.error('Upload Error:', error);
      alert('Failed to process dataset.');
      setFileName("");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileProcess(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileProcess(e.target.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  if (!isDataLoaded) {
    return (
      <div className="landing-container">
        <div className="landing-content">
          <div className="badge"><Sparkles size={14} /> AI-Powered Data Analyst Engine</div>
          <h1 className="hero-title">Unlock Insights from Your Data in <span>Seconds</span></h1>
          <p className="hero-subtitle">
            Upload your CSV or Excel dataset to generate automated insights, beautiful visualizations, and interact with a context-aware AI analyst.
          </p>

          <div 
            className={`upload-zone-centered ${dragActive ? "drag-active" : ""} ${isUploading ? "uploading" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {isUploading ? (
              <div className="upload-state">
                <div className="spinner-large"></div>
                <h3>Processing {fileName}...</h3>
                <p>Running LLM pipelines & computing metrics</p>
              </div>
            ) : (
              <>
                <FileSpreadsheet size={48} className="upload-icon" />
                <h3>Drop your dataset here</h3>
                <p>Support for .CSV, .XLS, .XLSX files up to 50MB</p>
                <label className="btn-primary mt-4">
                  Browse Files
                  <input type="file" accept=".csv, .xls, .xlsx" onChange={handleChange} className="hidden-input" />
                </label>
              </>
            )}
            {dragActive && <div className="drag-overlay">Drop to ingest data</div>}
          </div>

          <div className="config-panel">
            <h4 style={{display: 'flex', alignItems: 'center', gap: 6}}><Settings size={16}/> Analysis Settings</h4>
            <div className="config-grid">
              <label className="config-card">
                <span>Auto-Clean Missing Data</span>
                <input type="checkbox" checked={enableCleaning} onChange={(e) => setEnableCleaning(e.target.checked)} className="toggle" />
              </label>
              <label className="config-card">
                <span>Enable RAG (Ask questions to data)</span>
                <input type="checkbox" checked={enableRag} onChange={(e) => setEnableRag(e.target.checked)} className="toggle" />
              </label>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Dashboard layout once data is loaded
  return (
    <div className="dashboard-layout">
      {/* Top Navigation */}
      <nav className="top-nav">
        <div className="nav-brand">
          <Sparkles color="#3b82f6" size={20} />
          <h2>Smart Analyst</h2>
        </div>
        
        <div className="nav-links">
          <button className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <Activity size={18} /> Dashboard
          </button>
          <button className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
            <MessageSquare size={18} /> AI Agent
          </button>
          <button className={`nav-btn ${activeTab === 'eda' ? 'active' : ''}`} onClick={() => setActiveTab('eda')}>
            <Cpu size={18} /> EDA Studio
          </button>
          <button className={`nav-btn ${activeTab === 'explorer' ? 'active' : ''}`} onClick={() => setActiveTab('explorer')}>
            <Database size={18} /> Records
          </button>
        </div>

        <div className="nav-actions">
           <button className="btn-secondary" onClick={() => window.location.reload()}>
              New Dataset
           </button>
        </div>
      </nav>

      <main className="dashboard-main">
         <div className="dashboard-content-wrapper">
            {activeTab === 'dashboard' && <Dashboard metrics={metrics} />}
            {activeTab === 'chat' && <ChatAgent />}
            {activeTab === 'eda' && <EdaStudio />}
            {activeTab === 'explorer' && <DataExplorer />}
         </div>
      </main>
    </div>
  );
}

export default App;
