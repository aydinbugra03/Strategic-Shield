import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

function App() {
  const [riskData, setRiskData] = useState([]);
  const [schedule, setSchedule] = useState(null);
  const [simReport, setSimReport] = useState(null);

  const callEndpoint = async (path) => {
    const res = await axios.post(`http://localhost:5000${path}`);
    return res.data;
  };

  const generate = async () => {
    await callEndpoint('/generate');
  };
  const predict = async () => {
    const data = await callEndpoint('/predict');
    setRiskData(JSON.parse(data));
  };
  const scheduleRun = async () => {
    const data = await callEndpoint('/schedule');
    setSchedule(data);
  };
  const simulate = async () => {
    const data = await callEndpoint('/simulate');
    setSimReport(data);
  };

  const heatmap = riskData.length > 0 && (
    <Plot
      data={[{
        x: riskData.map(d => d.timestamp),
        y: riskData.map(d => `Machine ${d.machine}`),
        z: riskData.map(d => d.failure_risk),
        type: 'heatmap',
        colorscale: 'Reds'
      }]}
      layout={{ title: 'Failure Risk Heatmap' }}
    />
  );

  const gantt = schedule && (
    <Plot
      data={schedule.jobs.map(j => ({
        x: [j.start, j.finish],
        y: [`Machine ${j.machine}`],
        type: 'bar',
        orientation: 'h',
        name: j.id
      }))}
      layout={{ barmode: 'stack', title: 'Schedule' }}
    />
  );

  return (
    <div className="App">
      <h1>AI-Driven Predictive Maintenance</h1>
      <button onClick={generate}>Generate Data</button>
      <button onClick={predict}>Predict Failure</button>
      <button onClick={scheduleRun}>Schedule</button>
      <button onClick={simulate}>Simulate</button>
      {heatmap}
      {gantt}
      {simReport && <pre>{JSON.stringify(simReport, null, 2)}</pre>}
    </div>
  );
}

export default App;
