import React from 'react';

const DataPanel = ({ selectedRegion, stats }) => {
  return (
    <div className="data-panel">
      <h2>📊 Analysis Dashboard</h2>
      
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="value">{stats.total_regions}</span>
            <span className="label">Total Regions</span>
          </div>
          <div className="stat-card">
            <span className="value">{stats.total_area_hectares}</span>
            <span className="label">Hectares</span>
          </div>
          <div className="stat-card">
            <span className="value">{stats.total_carbon_stock_tonnes}</span>
            <span className="label">Tonnes Carbon</span>
          </div>
          <div className="stat-card">
            <span className="value">{stats.average_biomass_density}</span>
            <span className="label">Avg Biomass</span>
          </div>
        </div>
      )}
      
      {selectedRegion ? (
        <>
          <div className="region-details">
            <h3>🌿 Region Details</h3>
            <div className="detail-row">
              <span className="detail-label">Region:</span>
              <span className="detail-value">{selectedRegion.region}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Location:</span>
              <span className="detail-value">
                {selectedRegion.location.latitude.toFixed(3)}, {selectedRegion.location.longitude.toFixed(3)}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Area:</span>
              <span className="detail-value">{selectedRegion.mangrove_characteristics.area_hectares} ha</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Biomass Density:</span>
              <span className="detail-value">{selectedRegion.mangrove_characteristics.biomass_density} kg/m²</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Soil Carbon:</span>
              <span className="detail-value">{selectedRegion.mangrove_characteristics.soil_carbon} t/ha</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Species:</span>
              <span className="detail-value">{selectedRegion.mangrove_characteristics.species}</span>
            </div>
          </div>
          
          <div className="carbon-analysis">
            <h3>🔥 Carbon Analysis</h3>
            <div className="detail-row">
              <span className="detail-label">Predicted Carbon Stock:</span>
              <span className="detail-value">{selectedRegion.carbon_analysis.predicted_carbon_stock} tonnes</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Confidence Score:</span>
              <span className="detail-value">{(selectedRegion.carbon_analysis.confidence_score * 100).toFixed(1)}%</span>
            </div>
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ width: `${selectedRegion.carbon_analysis.confidence_score * 100}%` }}
              ></div>
            </div>
            <div className="detail-row">
              <span className="detail-label">Change Rate:</span>
              <span className="detail-value" style={{ 
                color: selectedRegion.carbon_analysis.change_rate > 0 ? '#00ff88' : '#ff4444' 
              }}>
                {selectedRegion.carbon_analysis.change_rate > 0 ? '+' : ''}{selectedRegion.carbon_analysis.change_rate}% /year
              </span>
            </div>
          </div>
          
          <div className="recommendations">
            <h3>💡 Recommendations</h3>
            <ul>
              {selectedRegion.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        </>
      ) : (
        <div style={{ 
          textAlign: 'center', 
          padding: '3rem 1rem', 
          color: '#b0b0b0',
          fontSize: '1.1rem'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🌍</div>
          <p>Click on a mangrove region on the globe to view detailed carbon analysis</p>
          <div style={{ marginTop: '2rem', fontSize: '0.9rem' }}>
            <p>🟢 High carbon sequestration potential</p>
            <p>🟡 Medium carbon sequestration potential</p>
            <p>🔴 Low carbon sequestration potential</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataPanel;