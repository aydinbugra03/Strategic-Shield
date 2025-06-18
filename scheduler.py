import json
from typing import List, Dict

try:
    import gurobipy as gp
    from gurobipy import GRB
except Exception as e:  # if gurobipy not installed
    gp = None
    GRB = None


Job = Dict[str, any]


def build_jobs() -> List[Job]:
    """Return a list of jobs with durations and deadlines assigned to machines."""
    jobs = [
        {"id": "J1", "machine": 1, "duration": 3, "deadline": 10},
        {"id": "J2", "machine": 2, "duration": 4, "deadline": 12},
        {"id": "J3", "machine": 3, "duration": 2, "deadline": 8},
        {"id": "J4", "machine": 1, "duration": 5, "deadline": 15},
        {"id": "J5", "machine": 2, "duration": 3, "deadline": 9},
    ]
    return jobs


def schedule(jobs: List[Job], maint_duration: int = 2) -> Dict:
    if gp is None:
        raise ImportError("gurobipy is required to run the scheduler")

    machines = sorted(set(job["machine"] for job in jobs))
    model = gp.Model("scheduler")

    # variables
    start = {j["id"]: model.addVar(lb=0, name=f"start_{j['id']}") for j in jobs}
    maintenance = {m: model.addVar(lb=0, name=f"maint_{m}") for m in machines}

    # completion times
    completion = {j["id"]: start[j["id"]] + j["duration"] for j in jobs}
    maint_comp = {m: maintenance[m] + maint_duration for m in machines}

    bigM = 1000
    # ordering constraints for jobs on same machine
    for j1 in jobs:
        for j2 in jobs:
            if j1 == j2:
                continue
            if j1["machine"] == j2["machine"]:
                y = model.addVar(vtype=GRB.BINARY, name=f"y_{j1['id']}_{j2['id']}")
                model.addConstr(start[j2["id"]] >= completion[j1["id"]] - bigM * (1 - y))
                model.addConstr(start[j1["id"]] >= completion[j2["id"]] - bigM * y)

    # maintenance must happen before or after jobs on same machine
    for j in jobs:
        m = j["machine"]
        z = model.addVar(vtype=GRB.BINARY, name=f"z_{j['id']}")
        model.addConstr(start[j["id"]] >= maint_comp[m] - bigM * (1 - z))
        model.addConstr(maintenance[m] >= completion[j["id"]] - bigM * z)

    # objective: minimize late penalties and downtime (maintenance duration)
    late = {j["id"]: model.addVar(lb=0, name=f"late_{j['id']}") for j in jobs}
    for j in jobs:
        model.addConstr(late[j["id"]] >= completion[j["id"]] - j["deadline"])

    downtime = sum(maint_duration for _ in machines)
    model.setObjective(gp.quicksum(late.values()) + downtime, GRB.MINIMIZE)

    model.optimize()

    schedule = {
        "jobs": [
            {
                "id": j["id"],
                "machine": j["machine"],
                "start": start[j["id"]].X,
                "finish": completion[j["id"]].X,
            }
            for j in jobs
        ],
        "maintenance": [
            {"machine": m, "start": maintenance[m].X, "finish": maint_comp[m].X}
            for m in machines
        ],
    }
    return schedule


def main():
    jobs = build_jobs()
    sched = schedule(jobs)
    path = "schedule.json"
    with open(path, "w") as f:
        json.dump(sched, f, indent=2)
    print(f"Schedule saved to {path}")


if __name__ == "__main__":
    main()
