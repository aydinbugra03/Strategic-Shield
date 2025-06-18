import React, { useState } from 'react';
import Heatmap from './components/Heatmap';
import GanttChart from './components/GanttChart';

function App() {
  const [schedule, setSchedule] = useState([]);
  const [risk, setRisk] = useState(null);
  const [report, setReport] = useState(null);

  const api = async (endpoint, data={}) => {
    const res = await fetch(`http://localhost:5000/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  };

  const generate = async () => {
    await api('generate');
    alert('Data generated');
  };

  const train = async () => {
    await api('predict'); // just to load model if needed
  };

  const scheduleRun = async () => {
    const res = await api('schedule');
    setSchedule(res);
  };

  const simulate = async () => {
    const res = await api('simulate');
    setReport(res);
  };

  return (
    <div className="App">
      <h1>AI-Driven Predictive Maintenance Scheduler</h1>
      <button onClick={generate}>Generate Data</button>
      <button onClick={scheduleRun}>Run Scheduler</button>
      <button onClick={simulate}>Run Simulation</button>
      <Heatmap data={risk} />
      <GanttChart schedule={schedule} />
      {report && <pre>{JSON.stringify(report, null, 2)}</pre>}
    </div>
  );
}

export default App;
