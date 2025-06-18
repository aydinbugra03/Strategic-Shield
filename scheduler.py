import json
import os
from typing import List, Dict

from gurobipy import Model, GRB


class Job:
    def __init__(self, jid: int, machine: int, duration: int, due: int):
        self.jid = jid
        self.machine = machine
        self.duration = duration
        self.due = due


class Maintenance:
    def __init__(self, machine: int, duration: int):
        self.machine = machine
        self.duration = duration


def build_schedule(jobs: List[Job], maints: List[Maintenance], output_path: str = "schedules/schedule.json") -> str:
    m = Model("scheduler")
    m.setParam("OutputFlag", 0)

    big_m = 1000

    # Variables for job start times and tardiness
    start = {j.jid: m.addVar(lb=0, name=f"start_j{j.jid}") for j in jobs}
    tardiness = {
        j.jid: m.addVar(lb=0, name=f"late_j{j.jid}") for j in jobs
    }

    # Maintenance start times
    mstart = {
        (mt.machine): m.addVar(lb=0, name=f"start_m{mt.machine}") for mt in maints
    }

    m.update()

    # Completion times
    completion = {j.jid: start[j.jid] + j.duration for j in jobs}
    mcompletion = {mt.machine: mstart[mt.machine] + mt.duration for mt in maints}

    # Tardiness constraints
    for j in jobs:
        m.addConstr(tardiness[j.jid] >= completion[j.jid] - j.due)
        m.addConstr(tardiness[j.jid] >= 0)

    # Non-overlap constraints per machine
    for mach in {j.machine for j in jobs}:
        machine_jobs = [j for j in jobs if j.machine == mach]
        maint = [mt for mt in maints if mt.machine == mach][0]
        tasks = machine_jobs + [maint]
        for i in range(len(tasks)):
            for k in range(i + 1, len(tasks)):
                ti = tasks[i]
                tk = tasks[k]
                y = m.addVar(vtype=GRB.BINARY, name=f"y_{ti}_{tk}")
                si = start[ti.jid] if isinstance(ti, Job) else mstart[ti.machine]
                di = ti.duration
                sk = start[tk.jid] if isinstance(tk, Job) else mstart[tk.machine]
                dk = tk.duration
                m.addConstr(si + di <= sk + big_m * (1 - y))
                m.addConstr(sk + dk <= si + big_m * y)

    # Objective: minimize downtime (maintenance durations) + late penalties
    downtime = sum(mt.duration for mt in maints)
    penalty = sum(tardiness[j.jid] for j in jobs)
    m.setObjective(downtime + 10 * penalty, GRB.MINIMIZE)

    m.optimize()

    schedule: List[Dict] = []
    for j in jobs:
        schedule.append(
            {
                "id": f"job{j.jid}",
                "machine": j.machine,
                "type": "job",
                "start": start[j.jid].X,
                "end": completion[j.jid].getValue(),
            }
        )
    for mt in maints:
        schedule.append(
            {
                "id": f"maint{mt.machine}",
                "machine": mt.machine,
                "type": "maintenance",
                "start": mstart[mt.machine].X,
                "end": mcompletion[mt.machine].getValue(),
            }
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(schedule, f, indent=2)
    print(f"Schedule saved to {output_path}")
    return output_path


def demo_schedule() -> str:
    jobs = [
        Job(1, 1, 4, 20),
        Job(2, 2, 6, 30),
        Job(3, 3, 3, 25),
        Job(4, 1, 5, 40),
        Job(5, 2, 2, 12),
        Job(6, 3, 7, 35),
    ]
    maints = [Maintenance(1, 3), Maintenance(2, 4), Maintenance(3, 5)]
    return build_schedule(jobs, maints)


if __name__ == "__main__":
    demo_schedule()
