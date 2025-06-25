-- Database schema for Strategic Shield
-- This script creates tables for deployment sites, missile types,
-- targets, scenarios, and allocations.

-- Drop tables if they exist to allow re-running the script
DROP TABLE IF EXISTS Allocation;
DROP TABLE IF EXISTS MissileInventory;
DROP TABLE IF EXISTS ScenarioTarget;
DROP TABLE IF EXISTS Scenario;
DROP TABLE IF EXISTS Target;
DROP TABLE IF EXISTS MissileType;
DROP TABLE IF EXISTS DeploymentSite;

-- Deployment sites storing missile launchers
CREATE TABLE DeploymentSite (
    site_id   SERIAL PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    x_coord   DECIMAL      NOT NULL,
    y_coord   DECIMAL      NOT NULL,
    capacity  INTEGER      NOT NULL,
    priority  INTEGER      NOT NULL
);

-- Different missile types with varying ranges
CREATE TABLE MissileType (
    type_id   SERIAL PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    range_km            INTEGER      NOT NULL,
    warhead_multiplier  DECIMAL      NOT NULL,
    accuracy_multiplier DECIMAL      NOT NULL
);

-- Potential targets for the missiles
CREATE TABLE Target (
    target_id SERIAL PRIMARY KEY,
    x_coord   DECIMAL NOT NULL,
    y_coord   DECIMAL NOT NULL,
    priority  INTEGER NOT NULL
);

-- Named scenarios for optimization runs
CREATE TABLE Scenario (
    scenario_id SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL
);

-- Mapping of scenarios to targets
CREATE TABLE ScenarioTarget (
    scenario_id INTEGER NOT NULL REFERENCES Scenario(scenario_id),
    target_id   INTEGER NOT NULL REFERENCES Target(target_id),
    PRIMARY KEY (scenario_id, target_id)
);

-- Central missile pool (unlimited if you choose)
CREATE TABLE MissileInventory (
    type_id     INTEGER NOT NULL REFERENCES MissileType(type_id),
    total_stock INTEGER NOT NULL,
    PRIMARY KEY (type_id)
);


-- Results of an optimization allocation run
CREATE TABLE Allocation (
    run_id      SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES Scenario(scenario_id),
    site_id     INTEGER REFERENCES DeploymentSite(site_id),
    type_id     INTEGER REFERENCES MissileType(type_id),
    allocated   INTEGER NOT NULL
);
