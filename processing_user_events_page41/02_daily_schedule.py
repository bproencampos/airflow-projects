from airflow import DAG
import datetime as dt

dag = DAG(
    dag_id="02_daily_schedule",
    schedule_interval="@daily",
    start_date=dt.datetime(2023, 10, 3)
)