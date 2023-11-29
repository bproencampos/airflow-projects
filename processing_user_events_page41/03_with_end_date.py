from airflow import DAG
import datetime as dt

dag = DAG(
    dag_id="03_with_end_date",
    schedule_interval="@daily",
    start_date=dt.datetime(year=2023, month=20, day=3),
    end_date=dt.datetime(year=2023, month=10, day=10),
)