import json
import pathlib

import airflow
import requests
import requests.exceptions as request_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG( # The DAG class takes two required arguments.
    dag_id="download_rocket_launches", # The name of the DAG displayed in the Airflow UI
    start_date=airflow.utils.dates.days_ago(14), # The datetime at which the workflow should first start running
    schedule_interval=None,
)

download_launches = BashOperator(
    task_id="download_launches", # The name of the task
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'", # Bash Command
    dag=dag, # Reference to the DAG variable
)
2
def _get_pictures(): # Python function to call
    # Ensure directory exists
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True) # Create picture directory if it doesn't exist

    # Download all pictures in launches.json
    with open("/tmp/launches.json") as f: # Open the result of the previous task
        launches = json.load(f) # Read as dict so we can mingle the data 
        image_urls = [launch["image"] for launch in launches["results"]]
        for image_url in image_urls: # For every launch, fetch the element "image" | Loop over all images URLs
            try:
                response = requests.get(image_url) # Download each image
                image_filename = image_url.split("/")[-1] # Get only filename by selecting everything after the last
                                                          # For example, https://host/RocketImages/Electron.jpg_1440.jpg
                                                          # --> Electron.jpg_1440.jpg
                target_file = f"/tmp/images/{image_filename}" # Construct target file path
                with open(target_file, "wb") as f: # Open target file handle 
                    f.write(response.content) # Store each image | Store image to file path
                print(f"Downloaded {image_url} to {target_file}") # Print to stdout, this will be captured in airflow logs
            except requests.exceptions.MissingSchema: # Catch and process potential errors.
                print(f"{image_url} appears to be an invalid URL.")
            except requests.exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")

get_pictures = PythonOperator( # Instantiate Python Operator to call the Python Function
    task_id="get_pictures",
    python_callable=_get_pictures, # Point to the python function to execute.
    dag=dag
)

notify = BashOperator (
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag
)

download_launches >> get_pictures >> notify