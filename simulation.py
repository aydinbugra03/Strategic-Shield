import json
import random
import simpy
import joblib
import pandas as pd
from predictive_model import train_model


def load_failure_model(model_path="models/predictive_model.pkl"):
    return joblib.load(model_path)


def simulate(schedule_json: str, model_path: str = "models/predictive_model.pkl"):
    with open(schedule_json) as f:
        sched = json.load(f)

    model = load_failure_model(model_path)

    env = simpy.Environment()
    results = {"utilization": {}, "unscheduled_downtime": {}, "cycle_time": 0}

    machines = {m: simpy.Resource(env, capacity=1) for m in range(1, 4)}
    downtime = {m: 0 for m in range(1, 4)}
    busy_time = {m: 0 for m in range(1, 4)}

    def run_task(machine_id, start, duration, task_id):
        yield env.timeout(max(0, start - env.now))
        with machines[machine_id].request() as req:
            yield req
            start_time = env.now
            for t in range(int(duration)):
                # evaluate failure probability using model
                data = pd.DataFrame([[machine_id, random.uniform(60, 80), random.uniform(0.45, 0.55)]],
                                    columns=["machine", "temperature", "vibration"])
                prob = model.predict_proba(data)[:, 1][0]
                if random.random() < prob * 0.1:  # scaled
                    downtime[machine_id] += 1
                    yield env.timeout(1)
                yield env.timeout(1)
            busy_time[machine_id] += env.now - start_time

    for j in sched["jobs"]:
        env.process(run_task(j["machine"], j["start"], j["finish"] - j["start"], j["id"]))
    for m in sched["maintenance"]:
        env.process(run_task(m["machine"], m["start"], m["finish"] - m["start"], f"M{m['machine']}"))

    env.run()
    results["cycle_time"] = env.now
    for m in machines:
        results["utilization"][m] = busy_time[m] / env.now if env.now else 0
        results["unscheduled_downtime"][m] = downtime[m]
    return results


def main():
    res = simulate("schedule.json")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
