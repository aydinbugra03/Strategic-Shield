import React from 'react';
import { ScenarioType } from '../../App';
import './ScenarioSelector.css';

interface ScenarioSelectorProps {
  selectedScenario: ScenarioType;
  onScenarioChange: (scenario: ScenarioType) => void;
}

const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({ selectedScenario, onScenarioChange }) => {
  return (
    <div className="scenario-selector">
      <label htmlFor="scenario-select">Select Scenario:</label>
      <select 
        id="scenario-select"
        value={selectedScenario} 
        onChange={(e) => {
          const value = e.target.value;
          if (value === 'robust') {
            onScenarioChange('robust');
          } else {
            onScenarioChange(parseInt(value) as ScenarioType);
          }
        }}
      >
        <option value={1}>Scenario 1: Greece-Bulgaria Coalition</option>
        <option value={2}>Scenario 2: Armenia-Russia Coalition</option>
        <option value={3}>Scenario 3: Israel-US Coalition</option>
        <option value="robust">Robust Optimization</option>
      </select>
    </div>
  );
};

export default ScenarioSelector; 