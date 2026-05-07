# Data Science
README ini menjelaskan pekerjaan pada bagian Data Science, khususnya dua notebook utama:

- `data_science_time_series.ipynb`
- `data_science_time_series_inference.ipynb`

Bagian Data Science berfokus pada pembuatan model forecasting harga emas menggunakan pendekatan time series. Model digunakan untuk memprediksi harga emas hari berikutnya dan beberapa hari ke depan berdasarkan data historis harga emas.
## 1. data_science_time_series.ipynb
Notebook ini digunakan dalam analisa data, training model, evaluasi model, pemilihan model terbaik dan penyimpanan model final.

### Tahapan yang dilakukan

1. **Import Library**
Menggunakan library seperti pandas, numpy, matplotlib, statsmodel, sklearn dan Prophet untuk analisa data, visualisasi, modeling dan evaluasi.
2. **Data Loading**
Load dataset emas yang berisi kolom date, open, high, low, close, dan volume. Target prediksi adalah kolom close.
3. **Little EDA**
Melakukan visualisasi harga emas untuk melihat pola umum, tren jangka panjang, dan fluktuasi harga emas.
4. **Time Series Decomposition**  
   Memecah data menjadi komponen `trend`, `seasonal`, dan `residual`. Dari hasil decomposition, pergerakan harga emas terlihat lebih banyak dipengaruhi oleh trend, sedangkan seasonality relatif kecil.

5. **Data Preprocessing**  
   Data dibagi menjadi train dan test dengan rasio 90:10. Data train digunakan untuk membangun model, sedangkan data test digunakan untuk evaluasi performa model.

6. **Stationarity Check**  
   Menggunakan Augmented Dickey-Fuller test untuk mengecek apakah data sudah stasioner. Data raw terbukti non-stationary, sehingga perlu dilakukan first differencing.

7. **ACF dan PACF Analysis**  
   ACF dan PACF digunakan untuk melihat pola autocorrelation sebelum dan sesudah differencing. Setelah differencing, data menjadi lebih stabil dan penggunaan `d = 1` pada ARIMA/SARIMA menjadi sesuai.

8. **Model Training**  
   Membandingkan tiga model time series:
   - ARIMA
   - SARIMA
   - Prophet

9. **Model Evaluation**  
   Model dievaluasi menggunakan metrik:
   - MAE
   - RMSE
   - MAPE
   - R2

10. **Model Selection**  
    Berdasarkan hasil evaluasi, model terbaik adalah:

```text
SARIMA(0, 1, 2)x(0, 1, 1, 5)
```

11. **Refit Best Model**  
    Model SARIMA terbaik kemudian dilatih ulang menggunakan seluruh data historis agar model final memanfaatkan data terbaru sebelum digunakan untuk inference.

12. **Model Saving**  
    Model final disimpan sebagai:

```text
sarima_final_model.pkl
```
## Hasil Evaluasi Model

| Model | MAE | RMSE | MAPE | R2 |
|---|---:|---:|---:|---:|
| SARIMA(0, 1, 2)x(0, 1, 1, 5) | 1061.63 | 1356.15 | 28.67% | -1.27 |
| Prophet | 1136.60 | 1419.41 | 31.11% | -1.49 |
| ARIMA(2, 1, 1) | 1156.37 | 1463.61 | 31.37% | -1.64 |

SARIMA dipilih sebagai model terbaik karena menghasilkan nilai MAE, RMSE, dan MAPE paling rendah dibandingkan ARIMA dan Prophet.

Nilai evaluasi pada data test masih belum ideal karena periode test mengalami kenaikan harga emas yang sangat tajam. Forecast juga dilakukan untuk horizon test yang cukup panjang, sehingga model tidak mendapat update dari data aktual terbaru selama periode test.


## 2. data_science_time_series_inference.ipynb

## 2. data_science_time_series_inference.ipynb

Notebook ini digunakan untuk melakukan inference menggunakan model final yang sudah disimpan.

### Tahapan yang dilakukan

1. **Load Library dan Model**  
   Memuat library yang diperlukan dan membaca model final `sarima_final_model.pkl`.

2. **Fetch Data Terbaru**  
   Mengambil data harga emas terbaru dari `yfinance` menggunakan ticker `GC=F`.

3. **Fetch Kurs USD/IDR**  
   Mengambil kurs terbaru USD/IDR dari `yfinance` menggunakan ticker `IDR=X`.

4. **Forecast Harga Emas**  
   Model SARIMA digunakan untuk memprediksi harga emas beberapa business day ke depan.

5. **Konversi Satuan Harga**  
   Hasil prediksi dikonversi ke beberapa format:
   - USD per troy ounce
   - USD per gram
   - IDR per troy ounce
   - IDR per gram

6. **Inference Conclusion**  
   Menyimpulkan hasil prediksi dan menjelaskan bahwa model perlu di-refit secara berkala agar inference tetap relevan dengan data pasar terbaru.

## Contoh Hasil Inference

Contoh output dari notebook inference:

| Informasi | Nilai |
|---|---:|
| Latest actual gold price | 4,696.50 USD per troy ounce |
| Kurs USD/IDR | 17,400 |
| Prediksi next day | 4,523.43 USD per troy ounce |
| Prediksi per gram | 145.43 USD |
| Prediksi per troy ounce dalam IDR | Rp78.71 juta |
| Prediksi per gram dalam IDR | Rp2.53 juta |

Forecast beberapa hari ke depan menunjukkan pergerakan yang cenderung naik perlahan, dari sekitar 4,523 USD sampai 4,573 USD per troy ounce.

## Kesimpulan Bagian Data Science

- Notebook pertama digunakan untuk membangun dan mengevaluasi model forecasting harga emas.
- Model yang dibandingkan adalah ARIMA, SARIMA, dan Prophet.
- SARIMA menjadi model terbaik berdasarkan nilai error paling rendah.
- Model terbaik di-refit menggunakan seluruh data historis dan disimpan sebagai file `.pkl`.
- Notebook kedua digunakan untuk inference, mengambil data terbaru dari yfinance, melakukan forecast, dan mengonversi hasil prediksi ke USD serta IDR.
- Hasil prediksi dapat digunakan sebagai alat bantu analisis, tetapi tidak boleh menjadi satu-satunya dasar keputusan trading atau investasi.
