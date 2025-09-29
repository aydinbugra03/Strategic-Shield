from fastapi import FastAPI, HTTPException
import uvicorn
import pandas as pd
from sqlalchemy import create_engine, text
from optimization.optimizer import run_optimization_for_scenario, get_data
from optimization.robust_optimizer import run_robust_optimization
import os

app = FastAPI(
    title="Strategic Shield API",
    description="API for managing and running missile allocation optimization.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """
    Root endpoint to welcome users.
    """
    return {"message": "Welcome to the Strategic Shield API"}

@app.post("/optimization/run/robust")
def run_robust_optimization_endpoint():
    """
    Triggers the robust optimization model that considers all scenarios with realistic probabilities.
    
    This creates a single allocation that performs well across all potential conflicts.
    Uses probabilities: Greece-Bulgaria (0.20), Armenia-Russia (0.35), Israel-US (0.45)
    """
    try:
        # Run the robust optimization
        results = run_robust_optimization()

        if results:
            return {
                "status": "success", 
                "message": "Robust optimization completed successfully.", 
                "allocations_found": len(results),
                "note": "This allocation is optimized for all scenarios with realistic probabilities",
                "probabilities": {
                    "Greece-Bulgaria Coalition": 0.20,
                    "Armenia-Russia Coalition": 0.35, 
                    "Israel-US Coalition": 0.45
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Robust optimization failed to find a solution.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/optimization/results/robust")
def get_robust_optimization_results():
    """
    Retrieves the stored robust optimization results.
    
    Returns the single allocation that works best across all scenarios.
    """
    try:
        # --- Database Connection ---
        OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(OPTIMIZER_DIR)
        DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
        
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("Database file not found. Please run the ETL script first.")

        engine = create_engine(f"sqlite:///{DB_PATH}")

        # --- Query Data ---
        query = """
            SELECT
                a.site_id,
                ds.name AS site_name,
                a.type_id,
                mt.name AS missile_name,
                a.allocated
            FROM Allocation a
            JOIN DeploymentSite ds ON a.site_id = ds.site_id
            JOIN MissileType mt ON a.type_id = mt.type_id
            WHERE a.scenario_id = 0
            ORDER BY ds.name, mt.name
        """
        results_df = pd.read_sql(query, engine)

        if results_df.empty:
            raise HTTPException(status_code=404, detail="No robust optimization results found. Please run the robust optimization first.")

        # Convert numpy types to native Python types for JSON serialization
        results_list = []
        for _, row in results_df.iterrows():
            results_list.append({
                "site_id": int(row['site_id']),
                "site_name": str(row['site_name']),
                "type_id": int(row['type_id']),
                "missile_name": str(row['missile_name']),
                "allocated": int(row['allocated'])
            })

        return {
            "results": results_list,
            "total_allocations": len(results_list),
            "total_missiles": int(results_df['allocated'].sum()),
            "note": "This is the robust allocation optimized for all scenarios with realistic probabilities"
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/optimization/run/{scenario_id}")
def run_optimization(scenario_id: int):
    """
    Triggers the optimization model for a given scenario ID.
    
    This will execute the Gurobi solver and save the results to the database.
    """
    try:
        # Load the latest data from the database
        sites, missiles, scenarios, targets, scenario_targets, distances = get_data()

        # Check if the scenario exists
        if scenario_id not in scenarios.index:
            raise HTTPException(status_code=404, detail=f"Scenario with ID {scenario_id} not found.")

        # Run the optimization
        results = run_optimization_for_scenario(scenario_id, sites, missiles, scenarios, targets, scenario_targets, distances)

        if results:
            # --- Save results to the database ---
            print("Saving allocation results to the database...")
            results_df = pd.DataFrame(results)
            
            # Connect to the database
            OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
            PROJECT_ROOT = os.path.dirname(OPTIMIZER_DIR)
            DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
            engine = create_engine(f"sqlite:///{DB_PATH}")

            # Clear old results for this scenario and save new ones
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM Allocation WHERE scenario_id = {scenario_id}"))
                results_df.to_sql('Allocation', conn, if_exists='append', index=False)
            
            print("Successfully saved results.")
            
            return {"status": "success", "message": f"Optimization for scenario {scenario_id} completed successfully.", "allocations_found": len(results)}
        else:
            raise HTTPException(status_code=500, detail="Optimization failed to find a solution.")

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/optimization/results/{scenario_id}")
def get_optimization_results(scenario_id: int):
    """
    Retrieves the stored optimization results for a given scenario ID.
    
    The results are joined with site and missile names for clarity.
    """
    try:
        # --- Database Connection ---
        OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(OPTIMIZER_DIR)
        DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
        
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("Database file not found. Please run the ETL script first.")

        engine = create_engine(f"sqlite:///{DB_PATH}")

        # --- Query Data ---
        query = f"""
            SELECT
                a.site_id,
                ds.name AS site_name,
                a.type_id,
                mt.name AS missile_name,
                a.allocated
            FROM Allocation a
            JOIN DeploymentSite ds ON a.site_id = ds.site_id
            JOIN MissileType mt ON a.type_id = mt.type_id
            WHERE a.scenario_id = {scenario_id}
        """
        results_df = pd.read_sql(query, engine)

        if results_df.empty:
            raise HTTPException(status_code=404, detail=f"No allocation results found for scenario ID {scenario_id}. Please run the optimization first.")

        return results_df.to_dict(orient="records")

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/map/deployment-sites")
def get_deployment_sites():
    """
    Returns a list of all deployment sites with their coordinates for map visualization.
    """
    try:
        OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(OPTIMIZER_DIR)
        DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
        
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("Database file not found. Please run the ETL script first.")

        engine = create_engine(f"sqlite:///{DB_PATH}")
        query = "SELECT site_id, name, x_coord, y_coord, priority, capacity FROM DeploymentSite"
        df = pd.read_sql(query, engine)
        
        # Convert Decimal types to float for JSON serialization
        df['x_coord'] = df['x_coord'].astype(float)
        df['y_coord'] = df['y_coord'].astype(float)
        
        # Add Qatar status for frontend visualization
        df['is_qatar'] = df['name'].str.contains('Qatar', case=False, na=False)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/map/targets/all")
def get_all_targets():
    """
    Returns a list of ALL targets from ALL scenarios for robust optimization map visualization.
    """
    try:
        OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(OPTIMIZER_DIR)
        DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
        
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("Database file not found. Please run the ETL script first.")

        engine = create_engine(f"sqlite:///{DB_PATH}")
        query = """
            SELECT DISTINCT
                t.target_id,
                t.name,
                t.x_coord,
                t.y_coord,
                t.priority
            FROM Target t
        """
        df = pd.read_sql(query, engine)
        if df.empty:
            return []
            
        # Convert Decimal types to float for JSON serialization
        df['x_coord'] = df['x_coord'].astype(float)
        df['y_coord'] = df['y_coord'].astype(float)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/map/targets/{scenario_id}")
def get_scenario_targets(scenario_id: int):
    """
    Returns a list of targets for a specific scenario with their coordinates for map visualization.
    """
    try:
        OPTIMIZER_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(OPTIMIZER_DIR)
        DB_PATH = os.path.join(PROJECT_ROOT, 'strategic_shield.db')
        
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("Database file not found. Please run the ETL script first.")

        engine = create_engine(f"sqlite:///{DB_PATH}")
        query = f"""
            SELECT
                t.target_id,
                t.name,
                t.x_coord,
                t.y_coord,
                t.priority
            FROM Target t
            JOIN ScenarioTarget st ON t.target_id = st.target_id
            WHERE st.scenario_id = {scenario_id}
        """
        df = pd.read_sql(query, engine)
        if df.empty:
            return []
            
        # Convert Decimal types to float for JSON serialization
        df['x_coord'] = df['x_coord'].astype(float)
        df['y_coord'] = df['y_coord'].astype(float)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


# To run this API, use the command:
# uvicorn main:app --reload
# from the SHIELD/SHIELD-REPO/Strategic-Shield/backend/ directory.

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 