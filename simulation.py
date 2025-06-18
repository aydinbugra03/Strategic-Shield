import json
import random
from collections import defaultdict

import pandas as pd
import simpy
import joblib

MODEL_PATH = 'failure_model.joblib'


class Machine(object):
    def __init__(self, env, name, fail_model):
        self.env = env
        self.name = name
        self.fail_model = fail_model
        self.total_down = 0
        self.running = True

    def run_job(self, job, duration):
        start = self.env.now
        while self.env.now - start < duration:
            # Evaluate failure at each hour
            temp = 70 + random.random() * 10
            vib = 5 + random.random()
            prob = self.fail_model.predict_proba([[temp, vib]])[0, 1]
            if random.random() < prob * 0.05:  # scale down probability
                # Failure occurs, repair for 2 hours
                self.running = False
                self.total_down += 2
                yield self.env.timeout(2)
                self.running = True
            yield self.env.timeout(1)


def simulate(schedule_json, model_path=MODEL_PATH):
    model = joblib.load(model_path)
    env = simpy.Environment()
    machines = {m['machine']: Machine(env, m['machine'], model) for m in schedule_json}

    def process_machine(mdata):
        machine = machines[mdata['machine']]
        # Maintenance
        yield env.timeout(mdata['maintenance_start'])
        machine.running = False
        yield env.timeout(mdata['maintenance_end'] - mdata['maintenance_start'])
        machine.running = True
        for job in sorted(mdata['jobs'], key=lambda x: x['start']):
            yield env.timeout(max(0, job['start'] - env.now))
            yield env.process(machine.run_job(job['job'], job['end'] - job['start']))

    for mdata in schedule_json:
        env.process(process_machine(mdata))

    env.run()

    stats = {
        m.name: {
            'unscheduled_downtime': m.total_down
        } for m in machines.values()
    }
    return stats


def main():
    with open('schedule.json') as f:
        sched = json.load(f)
    stats = simulate(sched)
    with open('simulation_report.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print('Simulation saved to simulation_report.json')


if __name__ == '__main__':
    main()
