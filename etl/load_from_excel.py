#!/usr/bin/env python3
"""
etl/load_from_excel.py

Reads Excel sheets and upserts into the SQL schema:
  - sites
  - missile_types
  - scenarios (with user-provided probabilities)
  - scenario_targets
"""

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert

# ─── CONFIG ────────────────────────────────────────────────────────────────────
# 1) Install deps: pip install pandas openpyxl sqlalchemy psycopg2-binary
# 2) Adjust this URL for your DB:
DATABASE_URL = "postgresql://username:password@localhost:5432/strategic_shield"

# Mapping of scenario_id → probability
SCENARIO_PROBS = {
    1: 0.3,
    2: 0.3,
    3: 0.4,
}
# ────────────────────────────────────────────────────────────────────────────────

def get_engine():
    return create_engine(DATABASE_URL, future=True)

def upsert_dataframe(df: pd.DataFrame, table_name: str, key_cols: list, engine=None):
    """
    Upsert a DataFrame into table_name using key_cols for ON CONFLICT.
    (Postgres-only dialect shown; adjust for MySQL or SQLite as needed.)
    """
    if engine is None:
        engine = get_engine()
    metadata = MetaData()
    metadata.reflect(bind=engine, only=[table_name])
    table = Table(table_name, metadata, autoload_with=engine)

    records = df.to_dict(orient="records")
    stmt = insert(table).values(records)
    # on_conflict_do_update with all non-PK columns
    update_cols = {
        col.name: col for col in table.c
        if col.name not in key_cols
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=key_cols,
        set_=update_cols
    )
    with engine.begin() as conn:
        conn.execute(stmt)

def load_sites():
    df = pd.read_excel("data/sites.xlsx", sheet_name=0)
    # Rename if your Excel headers differ from the SQL DDL
    df = df.rename(columns={
        "site_id":        "site_id",
        "name":           "name",
        "x_coord":        "x_coord",
        "y_coord":        "y_coord",
        "capacity":       "capacity",
        "priority":       "priority",
    })
    upsert_dataframe(df, table_name="sites", key_cols=["site_id"])

def load_missile_types():
    df = pd.read_excel("data/missile_types.xlsx", sheet_name=0)
    df = df.rename(columns={
        "type_id":             "type_id",
        "name":                "name",
        "range_km":            "range_km",
        "warhead_multiplier":  "warhead_multiplier",
        "accuracy_multiplier": "accuracy_multiplier",
        "stock_amount":        "stock_amount",
    })
    upsert_dataframe(df, table_name="missile_types", key_cols=["type_id"])

def load_scenarios():
    # Derive from your scenario_targets sheet + manual probabilities
    st = pd.read_excel("data/scenario_targets.xlsx", sheet_name=0)
    scenarios = (
        st[["scenario_id", "scenario_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    scenarios["probability"] = scenarios["scenario_id"].map(SCENARIO_PROBS)
    upsert_dataframe(scenarios, table_name="scenarios", key_cols=["scenario_id"])

def load_scenario_targets():
    df = pd.read_excel("data/scenario_targets.xlsx", sheet_name=0)
    df = df.rename(columns={
        "scenario_id":   "scenario_id",
        "scenario_name": "scenario_name",  # optional in SQL; you can drop if normalized
        "target_name":   "target_name",
        "x_coord":       "x_coord",
        "y_coord":       "y_coord",
        "priority":      "priority",
    })
    upsert_dataframe(df, table_name="scenario_targets", key_cols=["scenario_id", "target_name"])

def main():
    print("Starting ETL → SQL load …")
    load_sites()
    print(" → sites loaded")
    load_missile_types()
    print(" → missile_types loaded")
    load_scenarios()
    print(" → scenarios loaded")
    load_scenario_targets()
    print(" → scenario_targets loaded")
    print("Done.")

if __name__ == "__main__":
    main()
