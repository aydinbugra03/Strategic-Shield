import React, { useState } from 'react';
import Plot from 'react-plotly.js';

function App() {
  const [heatData, setHeatData] = useState([]);
  const [schedule, setSchedule] = useState([]);
  const [report, setReport] = useState(null);

  const api = async (endpoint, payload) => {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload ? JSON.stringify(payload) : null,
    });
    return res.json();
  };

  const generate = async () => {
    await api('/generate');
  };

  const predict = async () => {
    const samples = Array.from({ length: 10 }).map((_, i) => ({
      temperature: 70 + Math.random() * 10,
      vibration: 0.5 + Math.random() * 0.2,
      machine_id: (i % 3) + 1,
    }));
    const res = await api('/predict', samples);
    setHeatData(res.predictions);
  };

  const scheduleFn = async () => {
    const res = await api('/schedule');
    setSchedule(JSON.parse(res.schedule));
  };

  const simulate = async () => {
    const res = await api('/simulate');
    setReport(res);
  };

  const heatmap = (
    <Plot
      data={[{
        z: [heatData],
        type: 'heatmap',
      }]}
      layout={{ title: 'Failure Risk Heatmap' }}
    />
  );

  const gantt = (
    <Plot
      data={schedule.map(item => ({
        x: [item.start, item.end],
        y: [item.machine, item.machine],
        mode: 'lines',
        line: { width: 20 },
        name: item.id,
      }))}
      layout={{ title: 'Schedule', yaxis: { autorange: 'reversed' } }}
    />
  );

  return (
    <div>
      <h1>AI-Driven Predictive Maintenance</h1>
      <button onClick={generate}>Generate Data</button>
      <button onClick={predict}>Predict</button>
      <button onClick={scheduleFn}>Schedule</button>
      <button onClick={simulate}>Simulate</button>
      {heatData.length > 0 && heatmap}
      {schedule.length > 0 && gantt}
      {report && <pre>{JSON.stringify(report, null, 2)}</pre>}
    </div>
  );
}

export default App;
