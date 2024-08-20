import airflow
import subprocess
import logging
from airflow import DAG 
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator 
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime , timedelta

default_args = {
    "email_on_failure" : False,
    "depends_on_past"  : False,
    "retries"          : 1,
    "retry_on_delay"   : timedelta(minutes = 1),
    "start_date"       : days_ago(0)
}

def choose_branch(**kwargs):
    current_time = datetime.now().time()
    if current_time.minute <= 10:
        return 'stop_instance'
    elif current_time.minute <= 20 :
        return 'start_instance'
    if current_time.minute <= 30:
        return 'stop_instance'
    elif current_time.minute <= 40 :
        return 'start_instance'
    if current_time.minute <= 50:
        return 'stop_instance'
    elif current_time.minute <= 60 :
        return 'start_instance'
    else:
        return 'no_operation'
        

# def run_gcloud_command(command):
#     try:
#         result = subprocess.run(command, check=True, text=True, capture_output=True)
#         logging.info(f"Command output: {result.stdout}")
#     except subprocess.CalledProcessError as e:
#         logging.error(f"Command failed with exit code {e.returncode}")
#         logging.error(f"Error output: {e.stderr}")

# def stop_instance():
#     command = ["gcloud", "compute", "instances", "stop", "composer-instance", "--zone", "asia-south1-b"]
#     logging.info("Stopping VM instance...")
#     run_gcloud_command(command)

# def start_instance():
#     command = ["gcloud", "compute", "instances", "start", "composer-instance", "--zone", "asia-south1-b"]
#     logging.info("Starting VM instance...")
#     run_gcloud_command(command)



def no_operation():
    pass

with DAG(
    "start_and_stop_instance",
    default_args = default_args,
    description  = "This dag is used to start and stop the vm instance everyday at particular time",
    schedule     = '5,10,15,20,25,30,35,40,45,50 * * * 6-7'
) as dag:
    
    start = EmptyOperator(
        task_id = "start_task"
    )
    
    branch_task = BranchPythonOperator(
        task_id = "branch_task",
        python_callable = choose_branch,
        provide_context = True
    )
    
    start_task = BashOperator(
        task_id = "start_instance",
        bash_command = "gcloud compute instances start composer-instance --zone asia-south1-b"
    )

    stop_task = BashOperator(
        task_id = "stop_instance",
        bash_command = "gcloud compute instances stop composer-instance --zone asia-south1-b"
    )

    no_task = BashOperator(
        task_id = "no_operation",
        bash_command = "echo no operation"
    )

    end = EmptyOperator(
        task_id = "end_task",
        trigger_rule = 'one_success'
    )

branch_task >> [start_task, stop_task, no_task]
[start_task, stop_task, no_task] >> end