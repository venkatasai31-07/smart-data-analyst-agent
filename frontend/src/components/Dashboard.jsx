import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { Activity, Brain, Server, ShieldCheck, HeartPulse, BookOpen, AlertCircle } from 'lucide-react';

export default function Dashboard({ metrics }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let interval;
    async function fetchInsights() {
      try {
        const res = await axios.get('/api/insights');
        setData(res.data);
        
        // If insights are still generating (returns string), poll again.
        if (typeof res.data.insights_text === "string" && 
           (res.data.insights_text.includes("Generating") || res.data.insights_text.includes("progress"))) {
            if (!interval) interval = setInterval(fetchInsights, 3000);
        } else {
            if (interval) clearInterval(interval);
        }
      } catch (e) {
        console.error("Failed to load insights", e);
        if (interval) clearInterval(interval);
      } finally {
        setLoading(false);
      }
    }
    fetchInsights();
    
    return () => { if (interval) clearInterval(interval); }
  }, []);

  if (loading) {
    return (
      <div style={{display:'flex', justifyContent:'center', alignItems:'center', height:'100%'}}>
         <div className="spinner-large"></div>
      </div>
    );
  }

  const isGenerating = typeof data?.insights_text === "string" && data?.insights_text.includes("progress");
  
  // Extract JSON payload
  const brainContent = !isGenerating && typeof data?.insights_text === "object" ? data.insights_text.dataset_brain : null;
  const storyContent = !isGenerating && typeof data?.insights_text === "object" ? data.insights_text.story_mode : null;

  // Evaluate risk level for UI color
  const riskColor = metrics?.health_score >= 80 ? '#10b981' : (metrics?.health_score >= 50 ? '#f59e0b' : '#ef4444');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: '100%', overflowY: 'auto', paddingRight: '8px' }}>
      
      {/* Top Banner: Health Score & Basics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(250px, 1fr) 2fr', gap: '24px' }}>
         
         {/* Viral Health Score Widget */}
         <div className="sub-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '32px' }}>
            <h3 style={{ display:'flex', alignItems:'center', gap:8, color: '#94a3b8', fontSize: 16, marginBottom: 16 }}>
               <HeartPulse size={20}/> Data Health Score
            </h3>
            
            <div style={{ position: 'relative', width: 120, height: 120, borderRadius: '50%', background: `conic-gradient(${riskColor} ${metrics?.health_score}%, rgba(255,255,255,0.05) 0)`, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(0,0,0,0.4)' }}>
               <div style={{ position: 'absolute', width: 100, height: 100, background: 'var(--panel-bg)', borderRadius: '50%' }}></div>
               <div style={{ position: 'relative', fontSize: 32, fontWeight: 700, color: '#fff' }}>{metrics?.health_score}%</div>
            </div>
            
            <div style={{ marginTop: 24, width: '100%' }}>
               <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 8 }}>
                  <span style={{ color: '#94a3b8' }}>Missing Cells</span>
                  <span style={{ color: metrics?.missing_cells > 0 ? '#f59e0b' : '#10b981' }}>{metrics?.missing_cells}</span>
               </div>
               <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                  <span style={{ color: '#94a3b8' }}>Duplicate Rows</span>
                  <span style={{ color: metrics?.duplicate_rows > 0 ? '#f59e0b' : '#10b981' }}>{metrics?.duplicate_rows}</span>
               </div>
            </div>
         </div>

         {/* Dataset Brain */}
         <div className="sub-panel" style={{ padding: '32px', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: -50, right: -50, opacity: 0.1, color: 'var(--accent-purple)' }}>
               <Brain size={200} />
            </div>
            
            <h3 style={{ display:'flex', alignItems:'center', gap:8, fontSize: 20, marginBottom: 24 }}>
               <Brain size={24} color="var(--accent-purple)"/> Dataset Brain Intel
            </h3>

            {isGenerating ? (
               <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--accent-blue)' }}>
                  <div className="loading-spinner"></div>
                  <span>Analyzing Dataset Architecture...</span>
               </div>
            ) : brainContent ? (
               <div style={{ display: 'flex', flexDirection: 'column', gap: 16, position: 'relative', zIndex: 10 }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                     <div style={{ background: 'rgba(255,255,255,0.03)', padding: 16, borderRadius: 12, border: '1px solid var(--panel-border)' }}>
                        <div style={{ fontSize: 12, color: '#94a3b8', textTransform: 'uppercase', marginBottom: 4 }}>Problem Type</div>
                        <div style={{ fontSize: 16, fontWeight: 600 }}>{brainContent.problem_type}</div>
                     </div>
                     <div style={{ background: 'rgba(255,255,255,0.03)', padding: 16, borderRadius: 12, border: '1px solid var(--panel-border)' }}>
                        <div style={{ fontSize: 12, color: '#94a3b8', textTransform: 'uppercase', marginBottom: 4 }}>Predicted Target Column</div>
                        <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--accent-blue)' }}>{brainContent.target_prediction}</div>
                     </div>
                  </div>
                  
                  <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: 16, borderRadius: 12, border: '1px solid rgba(139, 92, 246, 0.2)' }}>
                     <div style={{ fontSize: 12, color: '#c4b5fd', textTransform: 'uppercase', marginBottom: 4 }}>Suggested Machine Learning Model</div>
                     <div style={{ fontSize: 16, fontWeight: 600, color: '#ddd6fe' }}>{brainContent.ml_suggested}</div>
                  </div>

                  {brainContent.warnings?.length > 0 && (
                     <div style={{ background: 'rgba(239, 68, 68, 0.05)', padding: 12, borderRadius: 12, border: '1px solid rgba(239, 68, 68, 0.2)', display: 'flex', gap: 8 }}>
                        <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: 2 }}/>
                        <div style={{ fontSize: 14, color: '#fca5a5' }}>
                           {brainContent.warnings.map((w, i) => <div key={i}>{w}</div>)}
                        </div>
                     </div>
                  )}
               </div>
            ) : (
               <div style={{ color: '#ef4444' }}>Failed to parse generic AI response into Dataset Brain object.</div>
            )}
         </div>
      </div>

      {/* Story Mode */}
      <div className="sub-panel" style={{ padding: '32px' }}>
         <h3 style={{ display:'flex', alignItems:'center', gap:8, fontSize: 20, marginBottom: 16 }}>
            <BookOpen size={24} color="var(--accent-blue)"/> Story Mode
         </h3>
         
         {isGenerating ? (
             <div style={{ color: '#94a3b8' }}>Writing the story...</div>
         ) : storyContent ? (
             <div style={{ fontSize: 16, lineHeight: 1.8, color: '#e2e8f0', background: 'rgba(255,255,255,0.02)', padding: 24, borderRadius: 16, borderLeft: '4px solid var(--accent-blue)' }}>
               {storyContent.split('\n').map((para, i) => (
                  <p key={i} style={{ marginBottom: para ? 16 : 0 }}>{para}</p>
               ))}
             </div>
         ) : (
             <div style={{ color: '#94a3b8' }}>{typeof data?.insights_text === "string" ? data.insights_text : "Story not found."}</div>
         )}
      </div>

      {/* Visual Intelligence */}
      <div className="sub-panel">
         <h3 style={{ display:'flex', alignItems:'center', gap:8, marginBottom:24 }}>
            <Activity size={20} /> Visual Intelligence
         </h3>
         
         <div className="charts-grid">
         {data?.charts && data.charts.length > 0 ? (
            data.charts.map((chartObj, idx) => (
              <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding:'16px', borderRadius:'12px', border: '1px solid var(--panel-border)' }}>
                <h4 style={{marginBottom:16, fontSize:15, color:'#e2e8f0'}}>{chartObj.name}</h4>
                <div style={{width:'100%', height:'350px'}}>
                  <Plot
                    data={chartObj.figure.data}
                    layout={{
                      ...chartObj.figure.layout,
                      autosize: true,
                      paper_bgcolor: 'transparent',
                      plot_bgcolor: 'transparent',
                      font: {color: '#f8fafc'}
                    }}
                    useResizeHandler={true}
                    style={{width: '100%', height: '100%'}}
                  />
                </div>
              </div>
            ))
          ) : (
            <p style={{color:'#94a3b8'}}>Loading visualizations...</p>
          )}
          </div>
      </div>

    </div>
  );
}
