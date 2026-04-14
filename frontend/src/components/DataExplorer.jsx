import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Search, ChevronLeft, ChevronRight, Download } from 'lucide-react';

export default function DataExplorer() {
  const [data, setData] = useState({ records: [], columns: [], total: 0 });
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const limit = 50;

  const fetchData = async (p = 1, s = '') => {
    setLoading(true);
    try {
      const res = await axios.get('/api/data', { params: { page: p, limit, search: s } });
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page, search);
  }, [page]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchData(1, search);
  };

  const totalPages = Math.ceil(data.total / limit);

  return (
    <div style={{height: '100%', display: 'flex', flexDirection: 'column'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16}}>
        <h2>📑 Record Explorer</h2>
      </div>
      
      <form onSubmit={handleSearch} style={{marginBottom: 16, display: 'flex', gap: 12}}>
        <div style={{display: 'flex', flex: 1, background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: '8px 12px', alignItems: 'center', gap: 8}}>
          <Search size={18} color="#94a3b8" />
          <input 
            type="text" 
            placeholder="Search records across all columns..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{flex: 1, background: 'transparent', border: 'none', outline: 'none', color: '#fff'}}
          />
        </div>
        <button type="submit" className="primary">Search</button>
      </form>

      <div style={{flex: 1, overflow: 'auto', background: 'rgba(0,0,0,0.1)', borderRadius: 8, border: '1px solid rgba(255,255,255,0.05)'}}>
        {loading ? (
           <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%'}}>
              <div className="loading-spinner"></div>
           </div>
        ) : (
          <table style={{width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14}}>
            <thead style={{background: 'rgba(255,255,255,0.05)', position: 'sticky', top: 0}}>
              <tr>
                {data.columns.map(col => (
                  <th key={col} style={{padding: '12px 16px', fontWeight: 600, color: '#e2e8f0', whiteSpace: 'nowrap', borderBottom: '1px solid rgba(255,255,255,0.1)'}}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.records.length === 0 ? (
                <tr>
                  <td colSpan={data.columns.length} style={{padding: 32, textAlign: 'center', color: '#94a3b8'}}>
                    No records found.
                  </td>
                </tr>
              ) : (
                data.records.map((row, i) => (
                  <tr key={i} style={{borderBottom: '1px solid rgba(255,255,255,0.02)', transition: 'background 0.2s'}} onMouseOver={(e)=>e.currentTarget.style.background='rgba(255,255,255,0.02)'} onMouseOut={(e)=>e.currentTarget.style.background='transparent'}>
                    {data.columns.map(col => (
                      <td key={col} style={{padding: '12px 16px', color: '#cbd5e1', whiteSpace: 'nowrap'}}>
                        {String(row[col])}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16}}>
        <div style={{color: '#94a3b8', fontSize: 13}}>
          Showing {data.records.length} of {data.total} records
        </div>
        <div style={{display: 'flex', gap: 8, alignItems: 'center'}}>
           <button 
             onClick={() => setPage(p => Math.max(1, p - 1))} 
             disabled={page === 1}
             style={{padding: '6px', borderRadius: 4}}
           ><ChevronLeft size={16}/></button>
           <span style={{fontSize: 14}}>Page {page} of {totalPages || 1}</span>
           <button 
             onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
             disabled={page >= totalPages}
             style={{padding: '6px', borderRadius: 4}}
           ><ChevronRight size={16}/></button>
        </div>
      </div>
    </div>
  );
}
