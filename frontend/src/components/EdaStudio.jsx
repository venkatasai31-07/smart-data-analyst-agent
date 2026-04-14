import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { Download, Search, AlertTriangle, Cpu, TrendingUp, Scissors, HelpCircle } from 'lucide-react';

const LearnTooltip = ({ text }) => {
  const [show, setShow] = useState(false);
  return (
    <div style={{ position: 'relative', display: 'inline-block', marginLeft: 8, cursor: 'pointer' }}
         onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      <HelpCircle size={16} color="var(--accent-blue)" />
      {show && (
        <div style={{
          position: 'absolute', bottom: '120%', left: '50%', transform: 'translateX(-50%)',
          width: 280, background: 'var(--bg-dark)', padding: 12, borderRadius: 8,
          border: '1px solid var(--accent-blue)', color: '#e2e8f0', fontSize: 13,
          boxShadow: '0 10px 25px rgba(0,0,0,0.5)', zIndex: 50, lineHeight: 1.5,
          fontWeight: 400
        }}>
          <strong style={{ color: 'var(--accent-blue)', display: 'block', marginBottom: 4 }}>💡 Learn Mode</strong>
          {text}
        </div>
      )}
    </div>
  );
};

export default function EdaStudio() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // States for actions
  const [cleanAction, setCleanAction] = useState('Drop Duplicates');
  const [cleanCol, setCleanCol] = useState('');
  
  const [chartType, setChartType] = useState('histogram');
  const [xCol, setXCol] = useState('');
  const [yCol, setYCol] = useState('');
  const [plotFig, setPlotFig] = useState(null);
  
  const [outlierCol, setOutlierCol] = useState('');
  const [engineerCol, setEngineerCol] = useState('');
  const [engineerAction, setEngineerAction] = useState('Encode');

  const fetchDatasetInfo = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/dataset/info');
      setInfo(res.data);
      if (res.data.columns.length > 0) {
        setCleanCol(res.data.columns[0]);
        setXCol(res.data.columns[0]);
        setYCol(res.data.columns[0]);
        setOutlierCol(res.data.columns[0]);
        setEngineerCol(res.data.columns[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasetInfo();
  }, []);

  const handleClean = async () => {
    try {
      await axios.post('/api/eda/clean', { action: cleanAction, column: cleanCol });
      alert(`Applied ${cleanAction}`);
      fetchDatasetInfo(); // refresh
    } catch (e) { alert("Failed to apply cleaning"); }
  };

  const handleVisualize = async () => {
    try {
      const res = await axios.post('/api/eda/visualize', { type: chartType, x_col: xCol, y_col: yCol });
      setPlotFig(res.data.chart);
    } catch (e) { alert("Visualization Failed: Make sure columns format matches chart constraints."); }
  };

  const handleOutliers = async () => {
    try {
      const res = await axios.post('/api/eda/outliers', { column: outlierCol });
      alert(res.data.message);
      fetchDatasetInfo();
    } catch (e) { alert("Failed identifying outliers. Is column numeric?"); }
  };

  const handleEngineer = async () => {
    try {
      const res = await axios.post('/api/eda/engineer', { action: engineerAction, column: engineerCol });
      alert(res.data.message);
      fetchDatasetInfo();
    } catch (e) { alert("Feature Engineering Failed."); }
  };

  if (loading || !info) return <div className="loading-spinner" style={{margin:'auto'}} />;

  return (
    <div style={{display:'flex', flexDirection:'column', gap:24, height:'100%', overflowY:'auto'}}>
      
      {/* 1. Header & Downloads */}
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h2>💻 EDA Studio Workspace</h2>
        <div style={{display:'flex', gap:12}}>
           <a href="/api/download/csv" target="_blank" rel="noreferrer" className="btn-primary" style={{textDecoration:'none', background:'#10b981'}}>
             <Download size={16}/> Download Processed CSV
           </a>
           <a href="/api/download/pdf" target="_blank" rel="noreferrer" className="btn-primary" style={{textDecoration:'none', background:'#8b5cf6'}}>
             <Download size={16}/> Download PDF Report
           </a>
        </div>
      </div>

      {/* 2. Understanding Data */}
      <div className="sub-panel">
        <h3 style={{display:'flex', alignItems:'center', gap:8, marginBottom:16}}><Search size={18}/> 1. Understanding Data</h3>
        
        <div style={{display:'flex', gap:32, marginBottom:16}}>
          <div><strong>Rows:</strong> {info.shape.rows}</div>
          <div><strong>Columns:</strong> {info.shape.columns}</div>
        </div>
        
        <div style={{maxHeight:'200px', overflowY:'auto', border:'1px solid rgba(255,255,255,0.1)', borderRadius:8}}>
          <table style={{width:'100%', textAlign:'left', borderCollapse:'collapse', fontSize:14}}>
            <thead style={{background:'rgba(255,255,255,0.05)', position:'sticky', top:0}}>
               <tr><th style={{padding:8}}>Column name</th><th style={{padding:8}}>Type</th><th style={{padding:8}}>Missing (NaN)</th></tr>
            </thead>
            <tbody>
              {info.columns.map(c => (
                <tr key={c} style={{borderTop:'1px solid rgba(255,255,255,0.05)'}}>
                   <td style={{padding:8}}>{c}</td>
                   <td style={{padding:8, color:'#94a3b8'}}>{info.dtypes[c]}</td>
                   <td style={{padding:8, color: info.missing[c] > 0 ? '#ef4444' : '#10b981'}}>{info.missing[c]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:24}}>
        {/* 3. Data Cleaning */}
        <div className="sub-panel" style={{display:'flex', flexDirection:'column', gap:16}}>
           <h3 style={{display:'flex', alignItems:'center', gap:8}}>
              <Scissors size={18}/> 2. Data Cleaning
              <LearnTooltip text="Missing data or duplicates can ruin your machine learning model. Dropping them removes the bad rows entirely. Filling them with 'Mean' (the average) mathematically saves the row without biasing numeric trends."/>
           </h3>
           <p style={{fontSize:13, color:'#94a3b8'}}>Handle duplicates and missing values.</p>
           
           <div style={{display:'flex', gap:12}}>
              <select value={cleanAction} onChange={(e) => setCleanAction(e.target.value)} className="btn-secondary" style={{flex:1}}>
                 <option value="Drop Duplicates">Drop Duplicates</option>
                 <option value="Drop Missing Rows">Drop Missing Rows</option>
                 <option value="Fill Mean">Fill Mean (Numeric only)</option>
                 <option value="Fill Mode">Fill Mode</option>
                 <option value="Drop Column">Drop Entire Column</option>
              </select>
           </div>
           {cleanAction !== 'Drop Duplicates' && (
             <div style={{display:'flex', gap:12}}>
               <select value={cleanCol} onChange={(e) => setCleanCol(e.target.value)} className="btn-secondary" style={{flex:1}}>
                  <option value="">-- Apply to All / Select Column --</option>
                  {info.columns.map(c => <option key={c} value={c}>{c}</option>)}
               </select>
             </div>
           )}
           <button onClick={handleClean} className="btn-primary" style={{alignSelf:'flex-start'}}>Execute Clean</button>
        </div>

        {/* 4. Outliers & Engineering */}
        <div className="sub-panel" style={{display:'flex', flexDirection:'column', gap:16}}>
           <h3 style={{display:'flex', alignItems:'center', gap:8}}>
              <Cpu size={18}/> 3. Outliers & Engineering
              <LearnTooltip text="Feature Engineering transforms raw data so ML models understand it better. 'Label Encoding' turns text like 'Yes/No' into '1/0'. 'MinMax Scaling' shrinks massive numbers down between 0 and 1 so they don't overpower smaller but important numbers."/>
           </h3>
           <p style={{fontSize:13, color:'#94a3b8'}}>IQR outlier removal and feature scaling/encoding.</p>
           
           {/* Outliers */}
           <div style={{display:'flex', gap:12, alignItems:'center', background:'rgba(0,0,0,0.2)', padding:8, borderRadius:8}}>
              <span style={{fontSize:14, fontWeight:500}}>Outliers (IQR):</span>
              <select value={outlierCol} onChange={(e) => setOutlierCol(e.target.value)} className="btn-secondary" style={{flex:1}}>
                 {info.columns.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <button onClick={handleOutliers} className="btn-primary" style={{padding:'6px 12px', fontSize:13}}>Clean</button>
           </div>

           {/* Engineering */}
           <div style={{display:'flex', gap:12, alignItems:'center', background:'rgba(0,0,0,0.2)', padding:8, borderRadius:8}}>
              <select value={engineerAction} onChange={(e) => setEngineerAction(e.target.value)} className="btn-secondary" style={{width: 120}}>
                 <option value="Encode">Encode Label</option>
                 <option value="Scale MinMax">MinMax Scale</option>
                 <option value="Scale Standard">Std Scale</option>
              </select>
              <select value={engineerCol} onChange={(e) => setEngineerCol(e.target.value)} className="btn-secondary" style={{flex:1}}>
                 {info.columns.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <button onClick={handleEngineer} className="btn-primary" style={{padding:'6px 12px', fontSize:13}}>Apply</button>
           </div>
        </div>
      </div>

      {/* 5. Custom Visualization Builder */}
      <div className="sub-panel">
         <h3 style={{display:'flex', alignItems:'center', gap:8, marginBottom:16}}>
            <TrendingUp size={18}/> 4. Manual Visualizer
            <LearnTooltip text="Use Histograms to see the distribution of ONE column (like ages). Use Scatter plots to see the relationship between TWO numeric columns. Use Boxplots to spot extreme outliers (dots far from the box)."/>
         </h3>
         
         <div style={{display:'flex', gap:16, marginBottom:16}}>
           <label style={{flex:1}}>
             <div style={{marginBottom:4, fontSize:13}}>Chart Type</div>
             <select value={chartType} onChange={(e) => setChartType(e.target.value)} className="btn-secondary" style={{width:'100%'}}>
               <option value="histogram">Histogram (Univariate)</option>
               <option value="bar">Bar Chart (Categorical counts)</option>
               <option value="scatter">Scatter Plot (Bivariate)</option>
               <option value="boxplot">Boxplot (Distribution)</option>
             </select>
           </label>

           <label style={{flex:1}}>
             <div style={{marginBottom:4, fontSize:13}}>X Axis Column</div>
             <select value={xCol} onChange={(e) => setXCol(e.target.value)} className="btn-secondary" style={{width:'100%'}}>
               {info.columns.map(c => <option key={c} value={c}>{c}</option>)}
             </select>
           </label>

           {(chartType === 'scatter' || chartType === 'boxplot') && (
             <label style={{flex:1}}>
               <div style={{marginBottom:4, fontSize:13}}>Y Axis Column</div>
               <select value={yCol} onChange={(e) => setYCol(e.target.value)} className="btn-secondary" style={{width:'100%'}}>
                 {info.columns.map(c => <option key={c} value={c}>{c}</option>)}
               </select>
             </label>
           )}
           
           <div style={{display:'flex', alignItems:'flex-end'}}>
             <button onClick={handleVisualize} className="btn-primary" style={{height: 36}}>Generate Chart</button>
           </div>
         </div>

         {plotFig && (
           <div style={{marginTop: 16, background: 'rgba(0,0,0,0.3)', borderRadius: 12, padding: 16}}>
             <Plot
                data={plotFig.data}
                layout={{...plotFig.layout, autosize: true, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: {color: '#f8fafc'}}}
                useResizeHandler={true}
                style={{width: '100%', height: '400px'}}
              />
           </div>
         )}
      </div>

    </div>
  );
}
