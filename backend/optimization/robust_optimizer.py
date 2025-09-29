
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import numpy as np
from .optimizer import get_data

def get_realistic_probabilities():
    """
    Returns realistic scenario probabilities based on geopolitical analysis.
    """
    return {
        1: 0.20,  # Greece-Bulgaria Coalition (NATO internal, unlikely)
        2: 0.35,  # Armenia-Russia Coalition (regional tension, medium)
        3: 0.45   # Israel-US Coalition (Middle East dynamics, higher)
    }

def run_robust_optimization():
    """
    Runs probability-weighted robust optimization across all scenarios.
    Uses realistic probabilities based on conflict analysis.
    """
    # Load data
    sites, missiles, scenarios, targets, scenario_targets, distances = get_data()
    
    # SPECIAL CASE: For robust optimization, we need to handle Qatar sites
    # Qatar should be inactive in scenario 3 (US-Israel Coalition)
    # For robust optimization, we'll use a subset of sites that works for all scenarios
    # This means excluding Qatar sites since they're inactive in one scenario
    original_sites = sites.copy()
    active_sites = sites[~sites['name'].str.contains('Qatar', case=False, na=False)]
    print(f"Robust optimization: Qatar sites excluded for cross-scenario compatibility.")
    print(f"Active sites: {len(active_sites)} (was {len(original_sites)})")
    
    # Use active_sites for the rest of the optimization
    sites = active_sites
    
    # Get realistic probabilities
    probabilities = get_realistic_probabilities()
    
    print(f"--- Starting Robust Optimization ---")
    print(f"Realistic scenario probabilities:")
    for scenario_id, prob in probabilities.items():
        scenario_name = scenarios.loc[scenario_id]['name']
        print(f"  Scenario {scenario_id} ({scenario_name}): {prob:.2f}")

    # --- Create Gurobi Model ---
    m = gp.Model("StrategicShield_Robust")
    m.setParam('OutputFlag', 1)
    m.setParam('NonConvex', 2)

    # --- Decision Variables ---
    # x[i,m] = number of missiles of type m at site i (same allocation for all scenarios)
    x = m.addVars(sites.index, missiles.index, vtype=GRB.INTEGER, name="x")
    
    # Auxiliary variables for each scenario
    scenario_vars = {}
    for scenario_id in scenarios.index:
        # Get targets for this scenario
        target_ids = scenario_targets[scenario_targets['scenario_id'] == scenario_id]['target_id']
        scenario_target_data = targets.loc[target_ids]
        
        # Auxiliary variables for this scenario
        t_r = m.addVars(scenario_target_data.index, missiles.index, vtype=GRB.CONTINUOUS, 
                        lb=-GRB.INFINITY, name=f"t_r_{scenario_id}")
        y_r = m.addVars(scenario_target_data.index, missiles.index, vtype=GRB.CONTINUOUS, 
                        lb=0, name=f"y_r_{scenario_id}")
        t_d = m.addVars(sites.index, missiles.index, vtype=GRB.CONTINUOUS,
                        lb=-GRB.INFINITY, name=f"t_d_{scenario_id}")
        y_d = m.addVars(sites.index, missiles.index, vtype=GRB.CONTINUOUS,
                        lb=0, name=f"y_d_{scenario_id}")
        
        scenario_vars[scenario_id] = {
            'targets': scenario_target_data,
            't_r': t_r, 'y_r': y_r, 't_d': t_d, 'y_d': y_d
        }

    # Update model after adding variables
    m.update()
    print("Defined all decision variables for robust optimization.")

    # --- Parameters ---
    d = 1.0
    ln_09 = np.log(0.9)
    ln_08 = np.log(0.8)

    # --- Constraints ---
    
    # Site capacity constraint
    for i in sites.index:
        m.addConstr(gp.quicksum(x[i, m_type] for m_type in missiles.index) <= sites.loc[i, 'capacity'], 
                   name=f"SiteCapacity_{i}")

    # Missile stock constraint
    for m_type in missiles.index:
        m.addConstr(gp.quicksum(x[i, m_type] for i in sites.index) <= missiles.loc[m_type, 'total_stock'],
                   name=f"MissileStock_{m_type}")

    # Minimum deployment constraint
    for i in sites.index:
        m.addConstr(gp.quicksum(x[i, m_type] for m_type in missiles.index) >= 1,
                   name=f"MinDeployment_{i}")

    print("Added basic constraints.")

    # --- Scenario-specific constraints and objective ---
    total_objective = gp.LinExpr()
    
    for scenario_id in scenarios.index:
        prob = probabilities[scenario_id]
        vars_data = scenario_vars[scenario_id]
        scenario_target_data = vars_data['targets']
        t_r, y_r, t_d, y_d = vars_data['t_r'], vars_data['y_r'], vars_data['t_d'], vars_data['y_d']
        
        # Coverage constraints for this scenario
        for t in scenario_target_data.index:
            for m_type in missiles.index:
                hitting_sites = [i for i in sites.index 
                               if distances.loc[i, t] <= missiles.loc[m_type, 'range_km']]
                
                if hitting_sites:
                    N_tm = gp.quicksum(x[i, m_type] for i in hitting_sites)
                    m.addConstr(t_r[t, m_type] == ln_09 * N_tm, name=f"LogCoverage_{scenario_id}_{t}_{m_type}")
                else:
                    m.addConstr(t_r[t, m_type] == 0, name=f"LogCoverage_{scenario_id}_{t}_{m_type}")

        # Exponential constraints for coverage
        for t in scenario_target_data.index:
            for m_type in missiles.index:
                m.addGenConstrExp(t_r[t, m_type], y_r[t, m_type], name=f"ExpCoverage_{scenario_id}_{t}_{m_type}")

        # Defense constraints
        for i in sites.index:
            for m_type in missiles.index:
                m.addConstr(t_d[i, m_type] == ln_08 * x[i, m_type], name=f"LogDefense_{scenario_id}_{i}_{m_type}")
                m.addGenConstrExp(t_d[i, m_type], y_d[i, m_type], name=f"ExpDefense_{scenario_id}_{i}_{m_type}")

        # Objective for this scenario (weighted by probability)
        scenario_objective = gp.LinExpr()
        
        # Attack bonus
        for t in scenario_target_data.index:
            pi_t = scenario_target_data.loc[t, 'priority']
            target_coverage = gp.LinExpr()
            for m_type in missiles.index:
                w_m = missiles.loc[m_type, 'warhead_multiplier']
                a_m = missiles.loc[m_type, 'accuracy_multiplier']
                coverage_term = (1 - y_r[t, m_type]) / (1 - 0.9)
                target_coverage += w_m * a_m * coverage_term
            scenario_objective += pi_t * 10 * d * target_coverage

        # Defense bonus
        for i in sites.index:
            delta_i = sites.loc[i, 'priority']
            site_defense = gp.LinExpr()
            for m_type in missiles.index:
                w_m = missiles.loc[m_type, 'warhead_multiplier']
                a_m = missiles.loc[m_type, 'accuracy_multiplier']
                defense_term = (1 - y_d[i, m_type]) / (1 - 0.8)
                site_defense += w_m * a_m * defense_term
            scenario_objective += delta_i * 20 * d * site_defense

        # Add weighted scenario objective to total
        total_objective += prob * scenario_objective

    # Set the robust objective
    m.setObjective(total_objective, GRB.MAXIMIZE)
    print("Set robust objective function.")

    # --- Solve ---
    print("Starting robust optimization...")
    m.optimize()

    # --- Process Results ---
    if m.status == GRB.OPTIMAL:
        print(f"\n--- Robust Optimal Solution Found ---")
        print(f"Robust Objective Value: {m.objVal:.2f}")
        
        result_allocations = []
        total_missiles = 0
        
        print("\nRobust Allocation (optimized for all scenarios):")
        for i in sites.index:
            site_total = 0
            site_allocations = []
            for m_type in missiles.index:
                if x[i, m_type].X > 0.5:
                    allocated = int(round(x[i, m_type].X))
                    alloc = {
                        "scenario_id": 0,  # Special ID for robust solution
                        "site_id": i,
                        "type_id": m_type,
                        "allocated": allocated
                    }
                    result_allocations.append(alloc)
                    site_allocations.append(f"{allocated}×{missiles.loc[m_type,'name']}")
                    site_total += allocated
                    total_missiles += allocated
            
            if site_allocations:
                print(f"  {sites.loc[i,'name']}: {', '.join(site_allocations)} (Total: {site_total})")
        
        print(f"\nTotal robust missiles deployed: {total_missiles}")
        print("---------------------------\n")
        
        # Save to database
        save_robust_results(result_allocations)
        
        return result_allocations
    else:
        print(f"Robust optimization failed. Status: {m.status}")
        return None

def save_robust_results(results):
    """
    Saves robust optimization results to database.
    """
    import os
    from sqlalchemy import create_engine, text
    import pandas as pd
    
    print("Saving robust allocation results to the database...")
    results_df = pd.DataFrame(results)
    
    # Connect to the database
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
    DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # Clear old robust results and save new ones
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Allocation WHERE scenario_id = 0"))
        results_df.to_sql('Allocation', conn, if_exists='append', index=False)
    
    print("Successfully saved robust results.")