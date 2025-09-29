import React, { useState } from 'react';
import './App.css';
import MapView from './components/MapView/MapView';
import ScenarioSelector from './components/ScenarioSelector/ScenarioSelector';
import OptimizationPanel from './components/OptimizationPanel/OptimizationPanel';
import ResultsTable from './components/ResultsTable/ResultsTable';

export interface AllocationResult {
  site_id: number;
  site_name: string;
  type_id: number;
  missile_name: string;
  allocated: number;
}

export interface Site {
  site_id: number;
  name: string;
  x_coord: number;
  y_coord: number;
  is_qatar: boolean;
}

export interface Target {
  target_id: number;
  name: string;
  x_coord: number;
  y_coord: number;
}

export type ScenarioType = 1 | 2 | 3 | 'robust';

function App() {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioType>(1);
  const [optimizationResults, setOptimizationResults] = useState<AllocationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛡️ Strategic Shield</h1>
        <p>Multi-Scenario Missile Deployment Optimizer</p>
      </header>

      <div className="app-content">
        <div className="control-panel">
          <ScenarioSelector 
            selectedScenario={selectedScenario}
            onScenarioChange={setSelectedScenario}
          />
          <OptimizationPanel 
            selectedScenario={selectedScenario}
            onOptimizationComplete={setOptimizationResults}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        </div>

        <div className="main-content">
          <div className="map-section">
            <MapView 
              selectedScenario={selectedScenario}
            />
          </div>
          
          <div className="results-section">
            <ResultsTable 
              results={optimizationResults}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 