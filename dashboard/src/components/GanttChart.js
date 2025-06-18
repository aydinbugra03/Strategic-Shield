import React from 'react';
import Plot from 'react-plotly.js';

function GanttChart({ schedule }) {
  if (!schedule || schedule.length === 0) return null;

  const tasks = [];
  schedule.forEach(m => {
    m.jobs.forEach(job => {
      tasks.push({
        x: [job.start, job.end],
        y: [m.machine, m.machine],
        mode: 'lines',
        line: { width: 20 },
        name: job.job
      });
    });
  });

  return (
    <Plot
      data={tasks}
      layout={{ title: 'Schedule Gantt Chart', yaxis: { autorange: 'reversed' } }}
    />
  );
}

export default GanttChart;
