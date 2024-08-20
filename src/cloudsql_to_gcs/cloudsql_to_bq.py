from airflow import DAG 
import airflow 
from airflow.operators.python import PythonOperator , BranchPythonOperator, ShortCircuitOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago 
from datetime import datetime, timedelta
import mysql.connector as connector
import pandas as pd
from google.cloud import storage, bigquery

# variable decleration
BUCKET_NAME             = 'bucket-cloudsql-to-bq-d'
BLOB_NAME               = 'incoming/customers_data.ndjson'
PROJECT_ID              = 'cloudsql-to-bq-d'


default_args = {
    "depends_on_past"  : False,
    "start_date"       : days_ago(0),
    "retries"          : 1,
    "retry_delay"      : timedelta(minutes = 1),
    "email"            : ['ranjithbugide1610110@gmail.com'],
    "email_on_retry"   : True
}

# function definition

def cloudsql_to_gcs_to_bq():
    """
    """
    try:
        config = {
            'user'  : 'root',
            'host'  : '34.66.73.145',
            'password' : 'Hani',
            'database' : 'customers'
        }

        connection = connector.connect(**config)
        cursor     = connection.cursor()
        query      = f'''SELECT * FROM Customers'''
        cursor.execute(query)
        columns   = [col[0] for col in cursor.description]
        results   = cursor.fetchall()
        df        = pd.DataFrame(results, columns = columns)
        df['FullName'] = df['FirstName'] + ' ' + df['LastName']
        df             = df.drop(columns = ['FirstName', 'LastName'])
        ndjson_data    = df.to_json(orient = 'records', lines = True)

        # with open("/home/divya/customers_data.ndjson", 'w') as file:
        #     file.write(ndjson_data)
        
        is_placed      = upload_ndjson_file_to_bucket(ndjson_data, BUCKET_NAME, BLOB_NAME)
        if is_placed:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error: {e}")
        connection.close()
        cursor.close()
        return False 


def upload_ndjson_file_to_bucket(ndjson_file: str, bucket_name: str, blob_name: str):
    '''
    '''
    try:
        # gcs_client = storage.Client(project = PROJECT_ID)
        gcs_client = storage.Client(project = PROJECT_ID)
        gcs_bucket = gcs_client.get_bucket(bucket_name)
        gcs_blob   = gcs_bucket.blob(blob_name)
        gcs_blob.upload_from_string(ndjson_file)
        print("#####################################################")
        print(f'ndjson file is uploaded successfully in {gcs_blob.name} bucket {gcs_bucket.name}')
        print(f"####################################################")
        return True
    except Exception as e:
        print(f'Error : {e}')
        print("#####################################################")
        print(f'ndjson file is not uploaded successfully in {gcs_blob.name} bucket {gcs_bucket.name}')
        print(f"####################################################")
        return False


ndjson_file_path = f'gs://{BUCKET_NAME}/{BLOB_NAME}'
schema_file_path = '/tmp/schema/local-schema-file.json'
dataset_table = 'customers_stg_dataset.customers_stg_table'
    

with DAG(
    "cloudsql_to_bq",
    default_args = default_args,
    schedule = "0 5 * * 1-5"
) as dag: 
    
   start =  EmptyOperator(
       task_id = 'start'
   )
   
   upload_file_in_gcs  = ShortCircuitOperator(
       task_id         = "upload_data_in_gcs_bucket",
       python_callable = cloudsql_to_gcs_to_bq
   )

   upload_schema_file = BashOperator(
       task_id      = "upload_schema_file",
       bash_command = "gsutil cp gs://asia-south1-cloudsql-to-bq--62c868cc-bucket/dags/schema_for_stage_table.json /tmp/schema/local-schema-file.json"
   )

   gcs_to_bq = BashOperator(
        task_id='bq_command',
        bash_command=f"""
        bq load \
        --replace \
        --source_format=NEWLINE_DELIMITED_JSON \
        --schema={schema_file_path} \
        {dataset_table} \
        {ndjson_file_path}
        """,
    )

   staging_to_serving = BigQueryInsertJobOperator(
        task_id='staging_to_serving',
        configuration={
            "query": {
                "query": f"""
                            MERGE INTO `cloudsql-to-bq-d.customers_srv_dataset.customers_latest_srv` AS target
                            USING `cloudsql-to-bq-d.customers_stg_dataset.customers_stg_table` AS source
                            ON source.CustomerID = target.CustomerID
                            -- update existing records when matched 
                            WHEN MATCHED THEN
                            UPDATE SET
                                target.FullName = source.FullName,
                                target.Email = source.Email,
                                target.Phone = source.Phone,
                                target.Address = source.Address,
                                target.Username = source.Username,
                                target.Password = source.Password,
                                target.DateOfBirth = source.DateOfBirth,
                                target.Gender = source.Gender,
                                target.CreatedAt = source.CreatedAt,
                                target.UpdatedAt = CURRENT_TIMESTAMP()

                            WHEN NOT MATCHED THEN
                            INSERT (CustomerID, FullName, Email, Phone, Address, Username, Password, DateOfBirth, Gender, CreatedAt, UpdatedAt)
                            VALUES (source.CustomerID, source.FullName, source.Email, source.Phone, source.Address, source.Username, source.Password, source.DateOfBirth, source.Gender, source.CreatedAt, CURRENT_TIMESTAMP())

                            """,
                "useLegacySql": False,  # Set to True if using Legacy SQL
            },
            "destinationTable": {
                "projectId": "cloudsql-to-bq-d",
                "datasetId": "customers_srv_dataset",
                "tableId": "customers_latest_srv",
            },
            "writeDisposition": "WRITE_TRUNCATE",  # Options: WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY
        }  # Connection ID for Google Cloud
    )

   end = EmptyOperator(
       task_id = "end"
   )


   # task dependencies

   start >> upload_file_in_gcs >> upload_schema_file >> gcs_to_bq >> staging_to_serving >> end