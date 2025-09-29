import React from 'react';
import { ScenarioType, AllocationResult } from '../../App';
import './OptimizationPanel.css';
import { runOptimization } from '../../services/api';

interface OptimizationPanelProps {
  selectedScenario: ScenarioType;
  onOptimizationComplete: (results: AllocationResult[]) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const OptimizationPanel: React.FC<OptimizationPanelProps> = ({ 
  selectedScenario, 
  onOptimizationComplete, 
  isLoading, 
  setIsLoading 
}) => {
  const handleRunOptimization = async () => {
    setIsLoading(true);
    try {
      const result = await runOptimization(selectedScenario);
      if (result) {
        onOptimizationComplete(result);
      } else {
        onOptimizationComplete([]);
      }
    } catch (error) {
      console.error("Optimization failed:", error);
      alert("Optimization failed. Please check the console for details.");
      onOptimizationComplete([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="optimization-panel">
      <button 
        className="run-button"
        onClick={handleRunOptimization} 
        disabled={isLoading}
      >
        {isLoading ? (
          <div className="loading-spinner" />
        ) : (
          '🚀 Run Optimization'
        )}
      </button>
    </div>
  );
};

export default OptimizationPanel; 