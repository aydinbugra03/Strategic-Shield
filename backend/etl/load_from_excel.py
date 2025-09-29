#!/usr/bin/env python3
"""
etl/load_from_excel.py

Reads data from SHIELD/data.xlsx and upserts into the database schema.
"""

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.dialects.sqlite import insert
import os

# ─── CONFIG ────────────────────────────────────────────────────────────────────
# Correctly calculate paths from this script's location
ETL_DIR = os.path.dirname(os.path.abspath(__file__))
# The DB is located in the inner 'Strategic-Shield' project directory
INNER_PROJECT_DIR = os.path.abspath(os.path.join(ETL_DIR, '..', '..'))
# The excel file is in the 'SHIELD' directory
SHIELD_DIR = os.path.abspath(os.path.join(ETL_DIR, '..', '..', '..', '..'))

DATABASE_URL = f"sqlite:///{os.path.join(INNER_PROJECT_DIR, 'strategic_shield.db')}"
EXCEL_PATH = os.path.join(SHIELD_DIR, 'data.xlsx')

# Correct sheet names from user's Excel file
SITES_SHEET = 'DEPLOYMENT SITE'
MISSILES_SHEET = 'MISSILE TYPES'
SCENARIOS_SHEET = 'TARGET SITE'
# ────────────────────────────────────────────────────────────────────────────────

def get_engine():
    return create_engine(DATABASE_URL, future=True)

def upsert_dataframe(df: pd.DataFrame, table_name: str, key_cols: list, engine=None):
    """
    Upsert a DataFrame into table_name using key_cols for ON CONFLICT.
    (SQLite-only dialect shown)
    """
    if engine is None:
        engine = get_engine()
    
    records = df.to_dict(orient="records")
    if not records:
        print(f"Skipping upsert for {table_name} as no data was provided.")
        return

    metadata = MetaData()
    metadata.reflect(bind=engine, only=[table_name])
    table = Table(table_name, metadata, autoload_with=engine)

    stmt = insert(table).values(records)

    update_cols = {
        col.name: getattr(stmt.excluded, col.name)
        for col in table.c
        if col.name not in key_cols
    }
    
    stmt = stmt.on_conflict_do_update(
        index_elements=key_cols,
        set_=update_cols
    )
    with engine.begin() as conn:
        conn.execute(stmt)

def load_sites(engine):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=SITES_SHEET, dtype={'x_coord': float, 'y_coord': float})
        # Convert coordinates to XX.XXXX format if they are large numbers
        df['x_coord'] = df['x_coord'].apply(lambda x: x / 10000.0 if x > 1000 else x)
        df['y_coord'] = df['y_coord'].apply(lambda y: y / 10000.0 if y > 1000 else y)
        upsert_dataframe(df, table_name="DeploymentSite", key_cols=["site_id"], engine=engine)
    except FileNotFoundError:
        print(f"ERROR: Could not find the Excel file at {EXCEL_PATH}")
        raise
    except ValueError as e:
        print(f"ERROR: Sheet '{SITES_SHEET}' not found in {EXCEL_PATH}. Please check the sheet name.")
        raise e


def load_missile_types(engine):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=MISSILES_SHEET)
        
        missile_types_df = df[['type_id', 'name', 'range_km', 'warhead_multiplier', 'accuracy_multiplier']]
        inventory_df = df[['type_id', 'stock_amount']].rename(columns={'stock_amount': 'total_stock'})
        
        upsert_dataframe(missile_types_df, table_name="MissileType", key_cols=["type_id"], engine=engine)
        upsert_dataframe(inventory_df, table_name="MissileInventory", key_cols=["type_id"], engine=engine)
    except ValueError as e:
        print(f"ERROR: Sheet '{MISSILES_SHEET}' not found in {EXCEL_PATH}. Please check the sheet name.")
        raise e

def load_scenarios_and_targets(engine):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=SCENARIOS_SHEET, dtype={'x_coord': float, 'y_coord': float})

        # Print columns to debug
        print(f"Columns in '{SCENARIOS_SHEET}': {df.columns.tolist()}")

        # Clean up column names (remove leading/trailing spaces)
        df.columns = df.columns.str.strip()

        # Check for 'target_name' and rename if necessary
        if 'target_name' not in df.columns:
            if 'name' in df.columns:
                df.rename(columns={'name': 'target_name'}, inplace=True)
            elif 'target' in df.columns:
                df.rename(columns={'target': 'target_name'}, inplace=True)
            else:
                raise KeyError(f"'target_name' column not found in '{SCENARIOS_SHEET}'. Please check the Excel file.")
                
        # Scenarios
        scenarios_df = df[['scenario_id', 'scenario_name']].drop_duplicates().rename(columns={'scenario_name': 'name'})
        upsert_dataframe(scenarios_df, table_name="Scenario", key_cols=["scenario_id"], engine=engine)

        # Targets - Create a unique set of targets
                # Convert coordinates to XX.XXXX format if they are large numbers
        df['x_coord'] = df['x_coord'].apply(lambda x: x / 10000.0 if x > 1000 else x)
        df['y_coord'] = df['y_coord'].apply(lambda y: y / 10000.0 if y > 1000 else y)
        targets_df = df[['target_name', 'x_coord', 'y_coord', 'priority']].drop_duplicates(subset=['x_coord', 'y_coord'])
        targets_df = targets_df.reset_index(drop=True)
        targets_df['target_id'] = targets_df.index + 1
        targets_df = targets_df.rename(columns={'target_name': 'name'})

        # Create a mapping from coordinates to target_id for the join table
        coord_to_id = targets_df.set_index(['x_coord', 'y_coord'])['target_id'].to_dict()
        
        targets_to_insert_df = targets_df[['target_id', 'name', 'x_coord', 'y_coord', 'priority']]
        upsert_dataframe(targets_to_insert_df, table_name="Target", key_cols=["target_id"], engine=engine)

        # ScenarioTarget mapping
        df['target_id'] = df.set_index(['x_coord', 'y_coord']).index.map(lambda x: coord_to_id.get(x))

        scenario_target_df = df[['scenario_id', 'target_id']].drop_duplicates().dropna()
        scenario_target_df['target_id'] = scenario_target_df['target_id'].astype(int)

        with engine.begin() as conn:
            conn.execute(text("DELETE FROM ScenarioTarget;"))
            scenario_target_df.to_sql('ScenarioTarget', conn, if_exists='append', index=False)
            
    except ValueError as e:
        print(f"ERROR: Sheet '{SCENARIOS_SHEET}' not found in {EXCEL_PATH}. Please check the sheet name.")
        raise e


def main():
    print(f"Starting ETL → SQL load from {EXCEL_PATH}...")
    engine = get_engine()
    
    load_sites(engine)
    print(f" → Loaded '{SITES_SHEET}'")
    
    load_missile_types(engine)
    print(f" → Loaded '{MISSILES_SHEET}'")
    
    load_scenarios_and_targets(engine)
    print(f" → Loaded '{SCENARIOS_SHEET}'")
    
    print("Done.")

if __name__ == "__main__":
    main()
