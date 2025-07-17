# Makefile for Project Setup and Data Loading

# Phony targets don't represent files
.PHONY: all setup install load-data data-quality clean agent streamlit test full

# Default command: sets up the environment and loads data
all: setup load-data

# Setup and install dependencies
default: all

# Convenience target to create the environment and install dependencies
setup: install

# Creates the virtual environment if it doesn't exist, then installs dependencies
install:
	@echo "--- Ensuring virtual environment exists ---"
	uv venv
	@echo "--- Syncing dependencies from pyproject.toml ---"
	uv sync

# Runs the Python script to process and load data into the database
load-data:
	@echo "--- Running data loading script ---"
	uv run python scripts/load_data.py

# Runs the Python script to generate data quality report
data-quality:
	@echo "--- Running data quality check ---"
	uv run python scripts/data_quality_check.py

# Run the LangGraph agent directly (test context, no Streamlit)
agent:
	@echo "--- Running agent/langgraph_agent.py directly (test context) ---"
	uv run python -m agent.langgraph_agent

# Run the Streamlit dashboard	
streamlit:
	@echo "--- Running Streamlit dashboard (venv + native Streamlit) ---"
	. .venv/bin/activate && streamlit run report/app.py

# Run all unit tests (pytest or custom)
test:
	@echo "--- Running unit tests ---"
	uv pip install pytest || true
	uv run pytest

# Run everything for a full project setup (setup, ETL, data quality, dashboard)
full:
	@echo "--- Running full project pipeline: setup, ETL, data quality, dashboard ---"
	$(MAKE) setup
	$(MAKE) load-data
	$(MAKE) data-quality
	$(MAKE) streamlit

# Removes the virtual environment and the generated database
clean:
	@echo "--- Cleaning up project artifacts ---"
	rm -rf .venv
	rm -f database/srag_database.db