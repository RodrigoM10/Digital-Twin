import os
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryUploader:
    def __init__(self, credentials_path="gcp_credentials.json"):
        # Autenticación con la cuenta de servicio
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)
        self.table_id = f"{self.credentials.project_id}.digital_twin_data.telemetry"

    def upload_log_to_bq(self, csv_file_path):
        """Toma el CSV generado localmente y lo sube a la tabla de BigQuery"""
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=False, # Ya definimos el esquema arriba
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND, # Añade datos sin borrar los viejos
        )

        with open(csv_file_path, "rb") as source_file:
            print(f"[CLOUD] Subiendo {csv_file_path} a BigQuery...")
            job = self.client.load_table_from_file(source_file, self.table_id, job_config=job_config)
            
            job.result()  # Espera a que termine la carga

        table = self.client.get_table(self.table_id)
        print(f"[CLOUD] Carga finalizada. La tabla tiene ahora {table.num_rows} filas.")