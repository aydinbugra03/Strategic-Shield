import json
from datetime import timedelta

import pandas as pd
import gurobipy as gp
from gurobipy import GRB


MACHINES = ['M1', 'M2', 'M3']
JOBS = [
    {'id': 'J1', 'duration': 8, 'deadline': 24},
    {'id': 'J2', 'duration': 6, 'deadline': 30},
    {'id': 'J3', 'duration': 10, 'deadline': 40},
    {'id': 'J4', 'duration': 4, 'deadline': 20},
    {'id': 'J5', 'duration': 7, 'deadline': 36},
]
MAINTENANCE = {
    'M1': {'duration': 6},
    'M2': {'duration': 6},
    'M3': {'duration': 6},
}


def schedule():
    m = gp.Model('schedule')
    horizon = 48  # hours

    # Decision variables
    start = m.addVars([j['id'] for j in JOBS], MACHINES, vtype=GRB.CONTINUOUS, lb=0)
    assign = m.addVars([j['id'] for j in JOBS], MACHINES, vtype=GRB.BINARY)
    maint_start = m.addVars(MACHINES, vtype=GRB.CONTINUOUS, lb=0)

    bigM = horizon

    # Each job assigned to exactly one machine
    for j in JOBS:
        m.addConstr(sum(assign[j['id'], mach] for mach in MACHINES) == 1)

    # Start time only valid if assigned
    for j in JOBS:
        for mach in MACHINES:
            m.addConstr(start[j['id'], mach] <= bigM * assign[j['id'], mach])

    # Job finish before horizon
    for j in JOBS:
        dur = j['duration']
        for mach in MACHINES:
            m.addConstr(start[j['id'], mach] + dur <= horizon + bigM * (1 - assign[j['id'], mach]))

    # Maintenance window after jobs
    for mach in MACHINES:
        m.addConstr(maint_start[mach] >= 0)
        m.addConstr(maint_start[mach] + MAINTENANCE[mach]['duration'] <= horizon)

    # No overlap on same machine (jobs and maintenance)
    for mach in MACHINES:
        for i, ji in enumerate(JOBS):
            for j, jj in enumerate(JOBS):
                if i >= j:
                    continue
                dur_i = ji['duration']
                dur_j = jj['duration']
                m.addConstr(start[ji['id'], mach] + dur_i <= start[jj['id'], mach] + bigM * (2 - assign[ji['id'], mach] - assign[jj['id'], mach]))
                m.addConstr(start[jj['id'], mach] + dur_j <= start[ji['id'], mach] + bigM * (2 - assign[ji['id'], mach] - assign[jj['id'], mach]))
            # Job vs maintenance
            m.addConstr(start[ji['id'], mach] + ji['duration'] <= maint_start[mach] + bigM * (1 - assign[ji['id'], mach]))
            m.addConstr(maint_start[mach] + MAINTENANCE[mach]['duration'] <= start[ji['id'], mach] + bigM * (1 - assign[ji['id'], mach]))

    # Objective: minimize late delivery + downtime (maintenance start time)
    late_penalties = []
    for j in JOBS:
        deadline = j['deadline']
        late = m.addVar(vtype=GRB.CONTINUOUS, lb=0)
        finish = gp.quicksum((start[j['id'], mach] + j['duration']) * assign[j['id'], mach] for mach in MACHINES)
        m.addConstr(late >= finish - deadline)
        late_penalties.append(late)
    downtime = m.addVar(vtype=GRB.CONTINUOUS)
    m.addConstr(downtime == gp.quicksum(MAINTENANCE[m]['duration'] for m in MACHINES))
    m.setObjective(gp.quicksum(late_penalties) + downtime, GRB.MINIMIZE)

    m.optimize()

    schedule = []
    if m.status == GRB.OPTIMAL:
        for mach in MACHINES:
            schedule.append({
                'machine': mach,
                'maintenance_start': maint_start[mach].X,
                'maintenance_end': maint_start[mach].X + MAINTENANCE[mach]['duration'],
                'jobs': []
            })
        for j in JOBS:
            for mach in MACHINES:
                if assign[j['id'], mach].X > 0.5:
                    start_time = start[j['id'], mach].X
                    schedule[MACHINES.index(mach)]['jobs'].append({
                        'job': j['id'],
                        'start': start_time,
                        'end': start_time + j['duration']
                    })

    return schedule


def main():
    sched = schedule()
    with open('schedule.json', 'w') as f:
        json.dump(sched, f, indent=2)
    print('Schedule saved to schedule.json')


if __name__ == '__main__':
    main()
