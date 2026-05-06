FROM apache/airflow:2.3.4-python3.9

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=${PYTHONPATH}:/opt/airflow