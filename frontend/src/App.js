import React, { useState, useEffect } from 'react';
import EarthViewer from './components/EarthViewer';
import DataPanel from './components/DataPanel';
import './App.css';

function App() {
  const [mangroveData, setMangroveData] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchData();
    fetchStats();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/mapdata');
      const result = await response.json();
      setMangroveData(result.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/stats');
      const result = await response.json();
      setStats(result);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleRegionClick = async (region) => {
    try {
      const response = await fetch(`http://localhost:8000/insight/${region}`);
      const result = await response.json();
      setSelectedRegion(result);
    } catch (error) {
      console.error('Error fetching region insight:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <h2>Loading Gaia's Ark...</h2>
        <p>Initializing mangrove carbon analysis</p>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌍 Gaia's Ark</h1>
        <p>Mangrove Carbon Sequestration Intelligence</p>
        {stats && (
          <div className="header-stats">
            <span>{stats.total_regions} Regions</span>
            <span>{stats.total_area_hectares} Ha</span>
            <span>{stats.total_carbon_stock_tonnes} Tonnes C</span>
          </div>
        )}
      </header>

      <main className="app-main">
        <div className="earth-container">
          <EarthViewer 
            data={mangroveData}
            onRegionClick={handleRegionClick}
          />
        </div>
        
        <div className="panel-container">
          <DataPanel 
            selectedRegion={selectedRegion}
            stats={stats}
          />
        </div>
      </main>
    </div>
  );
}

export default App;