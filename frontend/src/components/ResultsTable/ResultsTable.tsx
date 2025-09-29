import React from 'react';
import { AllocationResult } from '../../App';
import './ResultsTable.css';

interface ResultsTableProps {
  results: AllocationResult[];
  isLoading: boolean;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="results-table-container">
        <h2>Optimization Results</h2>
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Running optimization...</p>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="results-table-container">
        <h2>Optimization Results</h2>
        <p className="no-results">No results to display. Run an optimization to see the allocation.</p>
      </div>
    );
  }

  return (
    <div className="results-table-container">
      <h2>Optimization Results</h2>
      <table className="results-table">
        <thead>
          <tr>
            <th>Deployment Site</th>
            <th>Missile Type</th>
            <th>Allocated</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => (
            <tr key={index}>
              <td>{result.site_name}</td>
              <td>{result.missile_name}</td>
              <td>{result.allocated}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable; 