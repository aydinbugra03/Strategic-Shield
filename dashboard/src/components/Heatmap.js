import React from 'react';
import Plot from 'react-plotly.js';

function Heatmap({ data }) {
  if (!data) return null;
  const z = data.map(row => row.values);
  const x = data.map(row => row.timestamp);
  const y = data.map(row => row.machine);
  return (
    <Plot
      data={[{ x, y, z, type: 'heatmap' }]}
      layout={{ title: 'Failure Risk Heatmap' }}
    />
  );
}

export default Heatmap;
