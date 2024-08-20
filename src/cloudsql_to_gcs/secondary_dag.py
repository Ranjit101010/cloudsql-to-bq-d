import airflow
import subprocess
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
    if current_time.minute == 5:
        return 'stop_instance'
    elif current_time.minute == 10:
        return 'start_instance'
    else:
        return 'no_operation'
        

def stop_instance():
    subprocess.run(["gcloud", "compute", "instances", "stop", "composer-instance", "--zone", "south-asia1-b"])

def start_instance():
    subprocess.run(["gcloud", "compute", "instances", "start", "composer-instance", "--zone", "south-asia1-b"])

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
        task_id         = "branch_task",
        python_callable = choose_branch,
        provide_context = True
    )
    
    start_task = PythonOperator(
        task_id = "start_instance",
        python_callable = start_instance
    )

    stop_task = PythonOperator(
        task_id = "stop_instance",
        python_callable = stop_instance
    )

    no_task = PythonOperator(
        task_id = "no_operation",
        python_callable = no_operation
    )

    end = EmptyOperator(
        task_id = "end_task"
    )

branch_task >> [start_task, stop_task, no_task]
[start_task, stop_task, no_task] >> end