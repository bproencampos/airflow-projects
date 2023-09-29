import datetime as dt
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="01_unscheduled",
    start_date=dt.datetime(2019, 1, 1), # Define the start date for the DAG
    schedule_interval=None, # Specify that this is an unscheduled DAG
)

fetch_events = BashOperator (
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data && curl -o /data/events.json https://localhost:5000/events" # Fetch and store the events from the API
    ),
    dag=dag
)

def _calculate_stats(input_path, output_path):
    """Calculate events statistics."""
    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index() # Load the events and calculate required statistics 
    Path(output_path).parent.mkdir(exist_ok=True) # Make sure the output directory exists and write resolut to CSV 
    stats.to_csv(output_path, index=False)

calculate_stats = PythonOperator (
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={
        "input_path": "/data/events.json",
        "output_path": "/data/stats.csv",
    },
    dag=dag
)

fetch_events >> calculate_stats # Set order of execution