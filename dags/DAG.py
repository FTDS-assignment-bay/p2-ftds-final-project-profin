import os
import pandas as pd
import joblib
import psycopg2
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import warnings
warnings.filterwarnings("ignore")

RAW_DATA_PATH = '/opt/airflow/dags/gold_raw.csv'
CLEAN_DATA_PATH = '/opt/airflow/dags/gold_clean.csv'
MODEL_PATH = '/opt/airflow/models/sarima_model.pkl'
TROY_OUNCE_TO_GRAM = 31.1034768

DB_USER = "airflow"
DB_PASS = " airflow"
DB_HOST = "postgres"
DB_PORT = "5432"

default_args = {
    'owner': 'Data_Engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'gold_prediction_pipeline',
    default_args=default_args,
    schedule_interval='0 8 * * 1-5',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    ranges=False,
    tags=['gold', 'sarima', 'production']
) as dag:

    def init_db(**kwargs):
        conn = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database="airflow")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'gold_predictions'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE gold_predictions OWNER airflow;")
        cursor.close()
        conn.close()

        conn_gold = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database="gold_predictions")
        cursor = conn_gold.cursor()
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS gold;
            CREATE TABLE IF NOT EXISTS gold.historical_data (
                id SERIAL PRIMARY KEY, date DATE UNIQUE NOT NULL, close DOUBLE PRECISION,
                high DOUBLE PRECISION, low DOUBLE PRECISION, open DOUBLE PRECISION, volume BIGINT);
            CREATE TABLE IF NOT EXISTS gold.predictions (
                id SERIAL PRIMARY KEY, prediction_date DATE NOT NULL,
                predicted_close_usd_toz DOUBLE PRECISION, predicted_close_idr_toz DOUBLE PRECISION,
                predicted_close_usd_gr DOUBLE PRECISION, predicted_close_idr_gr DOUBLE PRECISION,
                predicted_change_usd DOUBLE PRECISION, predicted_change_pct DOUBLE PRECISION,
                usd_idr_rate DOUBLE PRECISION, prediction_run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'completed');
        """)
        conn_gold.commit()
        cursor.close()
        conn_gold.close()

    def fetch_data(**kwargs):
        try:
            import yfinance as yf
            data = yf.download(tickers="GC=F", start="2025-01-01", interval="1d", auto_adjust=False, progress=False, multi_level_index=False).reset_index()
            data = data.rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Adj Close": "adj_close", "Volume": "volume"})
        except Exception:
            data = pd.read_csv('/opt/airflow/data/profin_clean.csv')
        data.to_csv(RAW_DATA_PATH, index=False)

    def clean_data(**kwargs):
        df = pd.read_csv(RAW_DATA_PATH)
        df['date'] = pd.to_datetime(df['date'])
        for col in ['close', 'high', 'low', 'open', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['date', 'close']).sort_values('date').reset_index(drop=True)
        df.to_csv(CLEAN_DATA_PATH, index=False)

    def predict_and_save(**kwargs):
        df = pd.read_csv(CLEAN_DATA_PATH)
        df['date'] = pd.to_datetime(df['date'])
        
        sarima_result = joblib.load(MODEL_PATH)
        forecast_obj = sarima_result.get_forecast(steps=1)
        forecast = float(forecast_obj.predicted_mean.iloc[0])
        
        last_date = df["date"].iloc[-1]
        next_date = pd.bdate_range(start=last_date + pd.offsets.BDay(1), periods=1)[0]
        last_close = float(df["close"].iloc[-1])
        
        try:
            import yfinance as yf
            fx = yf.download(tikers="IDR=X", period="5d", interval="1d", auto_adjust=False, progress=False, multi_level_index=False).dropna()
            rate = float(fx["Close"].iloc[-1])
        except Exception:
            rate = 17420.00

        from sqlalchemy import create_engine, text
        engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/gold_predictions")
        
        df_db = df[['date', 'close', 'high', 'low', 'open', 'volume']].copy()
        df_db['date'] = pd.to_datetime(df_db['date']).dt.date
        with engine.begin() as conn:
            for _, row in df_db.iterrows():
                conn.execute(text("""INSERT INTO gold.historical_data (date, close, high, low, open, volume)
                    VALUES (:d, :c, :h, :l, :o, :v) ON CONFLICT (date) DO UPDATE SET
                    close=EXCLUDED.close, high=EXCLUDED.high, low=EXCLUDED.low, open=EXCLUDED.open, volume=EXCLUDED.volume"""),
                    {'d': row['date'], 'c': float(row['close']), 'h': float(row['high']), 'l': float(row['low']), 'o': float(row['open']), 'v': int(row['volume'])})
                    
        p_toz = float(forecast)
        with engine.begin() as conn:
            conn.execute(text("""INSERT INTO gold.predictions (prediction_date, predicted_close_usd_toz, predicted_close_idr_toz,
                predicted_close_usd_gr, predicted_close_idr_gr, predicted_change_usd, predicted_change_pct, usd_idr_rate, status)
                VALUES (:d, :utz, :itz, :ugr, :igr, :cu, :cp, :r, 'completed')"""),
                {'d': next_date.date(), 'utz': p_toz, 'itz': p_toz*rate,
                 'ugr': p_toz/TROY_OUNCE_TO_GRAM, 'igr': (p_toz/TROY_OUNCE_TO_GRAM)*rate,
                 'cu': float(forecast - last_close), 'cp': float(((forecast - last_close) / last_close) * 100), 'r': rate})

    task1 = PythonOperator(task_id='Init_DB', python_callable=init_db)
    task2 = PythonOperator(task_id='Scrape_Data', python_callable=fetch_data)
    task3 = PythonOperator(task_id='Clean_Data', python_callable=clean_data)
    task4 = PythonOperator(task_id='Predict_Save', python_callable=predict_and_save)

    task1 >> task2 >> task3 >> task4