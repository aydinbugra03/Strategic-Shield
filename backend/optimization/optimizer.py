import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from sqlalchemy import create_engine, text
import os
import numpy as np

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers
    
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def get_data():
    """
    Connects to the SQLite database and loads all necessary tables into pandas DataFrames.
    """
    # --- Database Connection ---
    # Calculate the path to the database file relative to this script
    OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(OPTIMIZER_DIR))
    DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
    
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at {DB_PATH}. Please run the ETL script first.")

    engine = create_engine(f"sqlite:///{DB_PATH}")

    # --- Load Data ---
    print("Loading data from database...")
    sites = pd.read_sql("SELECT * FROM DeploymentSite", engine, index_col='site_id')
    missiles = pd.read_sql("SELECT * FROM MissileType", engine, index_col='type_id')
    inventory = pd.read_sql("SELECT * FROM MissileInventory", engine, index_col='type_id')
    scenarios = pd.read_sql("SELECT * FROM Scenario", engine, index_col='scenario_id')
    targets = pd.read_sql("SELECT * FROM Target", engine, index_col='target_id')
    scenario_targets = pd.read_sql("SELECT * FROM ScenarioTarget", engine)
    print("Data loaded successfully.")

    # --- Combine Missile Data ---
    # For convenience, merge the missile properties and inventory into a single DataFrame
    missiles = missiles.join(inventory)

    # Calculate distance between all sites and targets
    distances = pd.DataFrame(index=sites.index, columns=targets.index)
    for s_id, site in sites.iterrows():
        for t_id, target in targets.iterrows():
            distances.loc[s_id, t_id] = haversine_distance(site['y_coord'], site['x_coord'], target['y_coord'], target['x_coord'])
    
    return sites, missiles, scenarios, targets, scenario_targets, distances

def run_optimization_for_scenario(scenario_id, sites, missiles, scenarios, targets, scenario_targets, distances):
    """
    Builds and solves the optimization model according to the exact mathematical formulation.
    Uses logarithmic and exponential constraints for exact power calculations.
    """
    # --- Filter Data for the Current Scenario ---
    scenario_name = scenarios.loc[scenario_id]['name']
    print(f"--- Starting Optimization for Scenario {scenario_id}: {scenario_name} ---")

    # SPECIAL CASE: For US-Israel Coalition (scenario 3), exclude Qatar sites
    # Qatar is closer to US, so it should be inactive in this scenario
    if scenario_id == 3:
        # Filter out Qatar sites (containing "Qatar" in the name)
        active_sites = sites[~sites['name'].str.contains('Qatar', case=False, na=False)]
        print(f"US-Israel Coalition: Qatar sites excluded. Active sites: {len(active_sites)} (was {len(sites)})")
    else:
        active_sites = sites
        print(f"All sites active: {len(active_sites)}")

    # Get the specific targets for this scenario
    target_ids_for_scenario = scenario_targets[scenario_targets['scenario_id'] == scenario_id]['target_id']
    scenario_target_data = targets.loc[target_ids_for_scenario]

    # --- Create Gurobi Model ---
    m = gp.Model(f"StrategicShield_{scenario_id}")
    m.setParam('OutputFlag', 1)
    m.setParam('NonConvex', 2)  # Enable nonconvex optimization for exp/log constraints

    print(f"Scenario has {len(scenario_target_data)} targets")
    print(f"Available sites: {len(active_sites)}")
    print(f"Available missile types: {len(missiles)}")

    # --- Decision Variables ---
    
    # Primary decision variables: x[i,m] = number of missiles of type m at site i
    x = m.addVars(active_sites.index, missiles.index, vtype=GRB.INTEGER, name="x")
    
    # Auxiliary variables for attack (coverage) calculations
    t_r = m.addVars(scenario_target_data.index, missiles.index, vtype=GRB.CONTINUOUS, 
                    lb=-GRB.INFINITY, name="t_r")  # log-scaled coverage count
    y_r = m.addVars(scenario_target_data.index, missiles.index, vtype=GRB.CONTINUOUS, 
                    lb=0, name="y_r")  # 0.9^N_{t,m}
    
    # Auxiliary variables for defense calculations  
    t_d = m.addVars(active_sites.index, missiles.index, vtype=GRB.CONTINUOUS,
                    lb=-GRB.INFINITY, name="t_d")  # log-scaled defense count
    y_d = m.addVars(active_sites.index, missiles.index, vtype=GRB.CONTINUOUS,
                    lb=0, name="y_d")  # 0.8^x_{i,m}

    # Update model after adding variables
    m.update()
    print("Defined all decision variables and updated model.")

    # --- Parameters ---
    d = 1.0  # Global scaling coefficient
    ln_09 = np.log(0.9)  # ln(0.9)
    ln_08 = np.log(0.8)  # ln(0.8)

    # --- Constraints ---
    
    # (1) Site capacity constraint: ∑_{m∈M} x_{i,m} ≤ capacity_i ∀i∈S
    for i in active_sites.index:
        m.addConstr(gp.quicksum(x[i, m_type] for m_type in missiles.index) <= active_sites.loc[i, 'capacity'], 
                   name=f"SiteCapacity_{i}")
    print("Added site capacity constraints.")

    # (2) Missile stock constraint: ∑_{i∈S} x_{i,m} ≤ stock_m ∀m∈M
    for m_type in missiles.index:
        m.addConstr(gp.quicksum(x[i, m_type] for i in active_sites.index) <= missiles.loc[m_type, 'total_stock'],
                   name=f"MissileStock_{m_type}")
    print("Added missile stock constraints.")

    # (3) Minimum deployment constraint: ∑_{m∈M} x_{i,m} ≥ 1 ∀i∈S
    for i in active_sites.index:
        m.addConstr(gp.quicksum(x[i, m_type] for m_type in missiles.index) >= 1,
                   name=f"MinDeployment_{i}")
    print("Added minimum deployment constraints.")

    # (4) Log-scaled coverage count: t^{(r)}_{t,m} = ln(0.9) * ∑_{i:d_{i,t}≤range_m} x_{i,m}
    for t in scenario_target_data.index:
        for m_type in missiles.index:
            # Find sites that can hit target t with missile type m
            hitting_sites = [i for i in active_sites.index 
                           if distances.loc[i, t] <= missiles.loc[m_type, 'range_km']]
            
            if hitting_sites:
                N_tm = gp.quicksum(x[i, m_type] for i in hitting_sites)
                m.addConstr(t_r[t, m_type] == ln_09 * N_tm, name=f"LogCoverage_{t}_{m_type}")
            else:
                # No sites can hit this target with this missile type
                m.addConstr(t_r[t, m_type] == 0, name=f"LogCoverage_{t}_{m_type}")

    # (5) Exponential constraint: y^{(r)}_{t,m} = exp(t^{(r)}_{t,m}) = 0.9^{N_{t,m}}
    for t in scenario_target_data.index:
        for m_type in missiles.index:
            m.addGenConstrExp(t_r[t, m_type], y_r[t, m_type], name=f"ExpCoverage_{t}_{m_type}")

    print("Added coverage (attack) constraints with exact exponential calculations.")

    # (6) Log-scaled defense count: t^{(d)}_{i,m} = ln(0.8) * x_{i,m}
    for i in active_sites.index:
        for m_type in missiles.index:
            m.addConstr(t_d[i, m_type] == ln_08 * x[i, m_type], name=f"LogDefense_{i}_{m_type}")

    # (7) Exponential constraint: y^{(d)}_{i,m} = exp(t^{(d)}_{i,m}) = 0.8^{x_{i,m}}
    for i in active_sites.index:
        for m_type in missiles.index:
            m.addGenConstrExp(t_d[i, m_type], y_d[i, m_type], name=f"ExpDefense_{i}_{m_type}")

    print("Added defense constraints with exact exponential calculations.")

    # Update model after adding all constraints
    m.update()
    
    # --- Objective Function ---
    
    # Attack-weighted coverage: ∑_{t∈T} π_t * 10d * ∑_{m∈M} w_m * a_m * (1 - y^{(r)}_{t,m})/(1 - 0.9)
    attack_bonus = gp.LinExpr()
    for t in scenario_target_data.index:
        pi_t = scenario_target_data.loc[t, 'priority']  # π_t
        
        target_coverage = gp.LinExpr()
        for m_type in missiles.index:
            w_m = missiles.loc[m_type, 'warhead_multiplier']  # w_m
            a_m = missiles.loc[m_type, 'accuracy_multiplier']  # a_m
            
            # (1 - y^{(r)}_{t,m}) / (1 - 0.9)
            coverage_term = (1 - y_r[t, m_type]) / (1 - 0.9)
            target_coverage += w_m * a_m * coverage_term
        
        attack_bonus += pi_t * 10 * d * target_coverage
    
    # Defense-weighted fortification: ∑_{i∈S} δ_i * 20d * ∑_{m∈M} w_m * a_m * (1 - y^{(d)}_{i,m})/(1 - 0.8)
    defense_bonus = gp.LinExpr()
    for i in active_sites.index:
        delta_i = active_sites.loc[i, 'priority']  # δ_i
        
        site_defense = gp.LinExpr()
        for m_type in missiles.index:
            w_m = missiles.loc[m_type, 'warhead_multiplier']  # w_m
            a_m = missiles.loc[m_type, 'accuracy_multiplier']  # a_m
            
            # (1 - y^{(d)}_{i,m}) / (1 - 0.8)
            defense_term = (1 - y_d[i, m_type]) / (1 - 0.8)
            site_defense += w_m * a_m * defense_term
        
        defense_bonus += delta_i * 20 * d * site_defense

    # Total objective
    objective = attack_bonus + defense_bonus
    m.setObjective(objective, GRB.MAXIMIZE)
    print("Set objective function with exact exponential formulation.")

    # --- Solve ---
    print("Starting optimization...")
    m.optimize()

    # --- Process Results ---
    if m.status == GRB.OPTIMAL:
        print(f"\n--- Optimal Solution Found ---")
        print(f"Objective Value: {m.objVal:.2f}")
        
        result_allocations = []
        total_missiles = 0
        
        print("\nDetailed Allocation:")
        for i in active_sites.index:
            site_total = 0
            site_allocations = []
            for m_type in missiles.index:
                if x[i, m_type].X > 0.5:  # If allocation > 0
                    allocated = int(round(x[i, m_type].X))
                    alloc = {
                        "scenario_id": scenario_id,
                        "site_id": i,
                        "type_id": m_type,
                        "allocated": allocated
                    }
                    result_allocations.append(alloc)
                    site_allocations.append(f"{allocated}×{missiles.loc[m_type,'name']}")
                    site_total += allocated
                    total_missiles += allocated
            
            if site_allocations:
                print(f"  {active_sites.loc[i,'name']}: {', '.join(site_allocations)} (Total: {site_total})")
        
        print(f"\nTotal missiles deployed: {total_missiles}")
        print("---------------------------\n")
        return result_allocations
    else:
        print(f"Optimization failed. Status: {m.status}")
        if m.status == GRB.INFEASIBLE:
            print("Model is infeasible. Computing IIS...")
            m.computeIIS()
            m.write("model.ilp")
            print("IIS written to model.ilp")
        return None


def main():
    """
    Main function to run the optimization.
    """
    # Load all data from the database
    sites, missiles, scenarios, targets, scenario_targets, distances = get_data()

    # --- Placeholder for the next step ---
    print("\n--- Input Data Summary ---")
    print(f"Loaded {len(sites)} deployment sites.")
    print(f"Loaded {len(missiles)} missile types.")
    print(f"Loaded {len(scenarios)} scenarios.")
    print(f"Loaded {len(targets)} unique targets.")
    print("--------------------------\n")

    # --- Run for a single scenario for now ---
    TEST_SCENARIO_ID = 1
    results = run_optimization_for_scenario(TEST_SCENARIO_ID, sites, missiles, scenarios, targets, scenario_targets, distances)

    if results:
        # --- Save results to the database ---
        print("Saving allocation results to the database...")
        results_df = pd.DataFrame(results)
        
        # Connect to the database
        OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(os.path.dirname(OPTIMIZER_DIR))
        DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
        engine = create_engine(f"sqlite:///{DB_PATH}")

        # Clear old results for this scenario and save new ones
        with engine.begin() as conn:
            conn.execute(text(f"DELETE FROM Allocation WHERE scenario_id = {TEST_SCENARIO_ID}"))
            results_df.to_sql('Allocation', conn, if_exists='append', index=False)
        
        print("Successfully saved results.")

if __name__ == "__main__":
    main() 