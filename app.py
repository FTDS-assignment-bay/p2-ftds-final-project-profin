import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import yfinance as yf
import joblib
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

DB_USER = "airflow"
DB_PASS = "airflow"
DB_HOST = "127.0.0.1" 
DB_PORT = "5433" 
DB_NAME = "gold_predictions"
TROY_OUNCE_TO_GRAM = 31.1034768
SARIMA_MODEL_PATH = 'models/sarima_model.pkl'

def get_db_data(query):
    conn = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Stellar Gold", page_icon="H", layout="wide")

with st.sidebar:
    st.image("stellargold.png", width=150)
    st.markdown("---")
    menu = st.radio("Pilih Menu", ["Live Dashboard", "Prediksi Emas"])
    st.markdown("---")
    st.caption("Data Engineer: David Andrian")
    st.caption("Data Analyst: Adib Nugroho")
    st.caption("Data Scientist: Michael Richard L")
    st.info("Model: SARIMA(0,1,2)x(0,1,1,5)")

if menu == "Live Dashboard":
    st.title("Dashboard Prediksi Harga Emas")
    try:
        df_live = yf.download(tickers="GC=F", start="2025-01-01", interval="1d", auto_adjust=False, progress=False, multi_level_index=False).reset_index()
        df_live = df_live.rename(columns={"Date": "date", "Close": "close", "High": "high", "Low": "low", "Open": "open", "Volume": "volume"})
        today_data = df_live.iloc[-1]
        
        sarima_result = joblib.load(SARIMA_MODEL_PATH)
        forecast_obj = sarima_result.get_forecast(steps=1)
        pred_value = float(forecast_obj.predicted_mean.iloc[0])
        
        last_db_date = get_db_data("SELECT MAX(date) FROM gold.historical_data").iloc[0, 0]
        last_close = float(get_db_data("SELECT close FROM gold.historical_data ORDER BY date DESC LIMIT 1").iloc[0, 0])
        next_date = pd.bdate_range(start=pd.to_datetime(last_db_date) + pd.Timedelta(days=1), periods=1)[0]
        pct = float(((pred_value - last_close) / last_close) * 100)

        try:
            fx = yf.download(tickers="IDR=X", period="5d", interval="1d", auto_adjust=False, progress=False, multi_level_index=False).dropna()
            rate = float(fx["Close"].iloc[-1])
        except:
            rate = 17420.00

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### Hari Ini ({today_data['date'].strftime('%Y-%m-%d')})")
            st.metric(label="Close (USD/Troy Oz)", value=f"${today_data['close']:,.2f}")
            st.metric(label="High (USD/Troy Oz)", value=f"${today_data['high']:,.2f}")
        with col2:
            st.markdown(f"### Prediksi Besok ({next_date.strftime('%Y-%m-%d')})")
            st.metric(label="Close Prediksi (USD/Troy Oz)", value=f"${pred_value:,.2f}", delta=f"{pct:.3f}%")
            st.metric(label="Close Prediksi (IDR/Gram)", value=f"Rp{pred_value/TROY_OUNCE_TO_GRAM * rate:,.0f}")
            
        st.markdown("---")
        hist_limit = st.slider("Tampilkan data terakhir (hari):", min_value=30, max_value=len(df_live), value=90)
        fig = px.line(df_live.tail(hist_limit), x='date', y=['close', 'high', 'low'], template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.title("Prediksi Harga Emas Tentukan Tanggal")
    
    input_date = st.date_input("Pilih tanggal yang ingin diprediksi:", min_value=datetime.today())
    
    if st.button("Jalankan Prediksi", type="primary"):
        with st.spinner("Memproses data..."):
            try:
                df_hist = get_db_data("SELECT date, close FROM gold.historical_data ORDER BY date ASC")
                if df_hist.empty:
                    st.error("Data historis kosong! Jalankan DAG V2 dulu via Airflow.")
                else:
                    df_hist['date'] = pd.to_datetime(df_hist['date'])
                    last_db_date = df_hist['date'].iloc[-1]
                    
                    bdays = pd.bdate_range(start=last_db_date + pd.Timedelta(days=1), end=input_date)
                    steps = len(bdays)
                    
                    if steps == 0:
                        st.warning("Tanggal yang dipilih sudah lewat atau hari ini!")
                    else:
                        sarima_result = joblib.load(SARIMA_MODEL_PATH)
                        forecast_obj = sarima_result.get_forecast(steps=steps)
                        pred_value = float(forecast_obj.predicted_mean.iloc[-1])
                        last_close = float(df_hist["close"].iloc[-1])
                        
                        try:
                            fx = yf.download(tickers="IDR=X", period="5d", interval="1d", auto_adjust=False, progress=False, multi_level_index=False).dropna()
                            rate = float(fx["Close"].iloc[-1])
                        except:
                            rate = 17420.00
                            
                        st.success("Prediksi Berhasil!")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### Mata Uang: **USD / Troy Ounce**")
                            st.metric(label="Tanggal Prediksi", value=input_date.strftime('%Y-%m-%d'))
                            st.metric(label="Prediksi Close", value=f"${pred_value:,.2f}")
                        with col2:
                            st.markdown("#### Mata Uang: **IDR / Gram**")
                            st.metric(label="Prediksi Close", value=f"Rp{pred_value/TROY_OUNCE_TO_GRAM * rate:,.0f}")
                            st.metric(label="Prediksi High (Estimasi)", value=f"Rp{pred_value * 1.005 / TROY_OUNCE_TO_GRAM * rate:,.0f}")
                            
            except Exception as e:
                st.error(f"Gagal memprediksi: {e}")