import json
import os
from typing import Dict, List

import joblib
import numpy as np
import simpy


class Machine:
    def __init__(self, env: simpy.Environment, machine_id: int):
        self.env = env
        self.id = machine_id
        self.resource = simpy.Resource(env, capacity=1)
        self.prod_time = 0.0
        self.down_time = 0.0


class Simulator:
    def __init__(self, schedule_path: str, model_path: str):
        with open(schedule_path) as f:
            self.schedule = sorted(json.load(f), key=lambda x: x["start"])
        self.model = joblib.load(model_path)
        self.env = simpy.Environment()
        self.machines = {i: Machine(self.env, i) for i in {t["machine"] for t in self.schedule}}

    def run(self):
        for task in self.schedule:
            self.env.process(self.handle_task(task))
        self.env.run()
        cycle_time = self.env.now
        util = {
            m_id: mach.prod_time / cycle_time for m_id, mach in self.machines.items()
        }
        return {
            "cycle_time": cycle_time,
            "utilization": util,
            "unscheduled_downtime": {
                m_id: mach.down_time for m_id, mach in self.machines.items()
            },
        }

    def handle_task(self, task: Dict):
        machine = self.machines[task["machine"]]
        with machine.resource.request() as req:
            yield req
            # wait until scheduled start
            if self.env.now < task["start"]:
                yield self.env.timeout(task["start"] - self.env.now)
            duration = task["end"] - task["start"]
            if task["type"] == "job":
                # generate random features for this job
                temp = np.random.normal(70, 5)
                vib = np.random.normal(0.5, 0.1)
                prob = self.model.predict_proba([[temp, vib, task["machine"]]])[0, 1]
                if np.random.rand() < prob:
                    repair = 2.0
                    machine.down_time += repair
                    yield self.env.timeout(repair)
            machine.prod_time += duration
            yield self.env.timeout(duration)


def simulate(schedule_path: str = "schedules/schedule.json", model_path: str = "models/predictive_model.joblib") -> Dict:
    sim = Simulator(schedule_path, model_path)
    result = sim.run()
    report_path = os.path.join("schedules", "simulation_report.json")
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Simulation report saved to {report_path}")
    return result


if __name__ == "__main__":
    simulate()
