# Strategic Shield

This repository hosts the implementation of **Strategic Shield: Multi-Scenario Missile Deployment Optimizer**. The project includes a SQL schema, data loading routines, Gurobi optimization scripts, a backend API and a React frontend.

## Project structure

- `db/` – SQL schemas and example data
- `etl/` – scripts for data extraction and loading
- `optim/` – Gurobi optimization models
- `backend/` – API services and web server
- `frontend/` – React application
- `docs/` – technical documentation
- `tests/` – unit tests and CI configuration

## Setup

1. **Clone the repository** and create a Python virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```

2. **Install Node dependencies** for the frontend:
   ```bash
   cd frontend
   npm install
   ```

3. **Database**: use PostgreSQL 14 or MySQL 8 as preferred. Ensure connection credentials are correctly configured in the backend service.

## License

All contents are provided for educational purposes. Replace or remove any confidential data before committing.
