# Project: Gold Price Forecasting

## 1. Summary: Gold Price Analysis

Analisis dilakukan untuk memahami pola historis harga emas sebelum digunakan pada proses machine learning. Berdasarkan exploratory data analysis (EDA), harga emas menunjukkan tren meningkat dalam jangka panjang dengan beberapa fluktuasi pada periode tertentu.

Selain itu, variabel harga seperti open, high, low, dan close memiliki hubungan yang sangat kuat sehingga dapat membantu model machine learning dalam mempelajari pola pergerakan harga emas.

Dataset kemudian dibersihkan dan dipersiapkan untuk tahap selanjutnya dalam pengembangan model prediksi harga emas.

---

## 2. Business Insights

### A. Long-Term Gold Price Growth

Harga emas menunjukkan kecenderungan meningkat dari tahun ke tahun. Kondisi ini menunjukkan bahwa emas memiliki nilai yang relatif kuat dalam jangka panjang.

Pola tren yang konsisten ini dapat membantu proses forecasting karena model machine learning dapat mempelajari arah pergerakan harga berdasarkan data historis.

---

### B. Gold Price Volatility

Meskipun memiliki tren meningkat, harga emas tetap mengalami fluktuasi pada beberapa periode tertentu.

Perubahan harga yang cukup signifikan ini menunjukkan bahwa prediksi harga emas memerlukan analisis historis yang baik agar model mampu memahami perubahan pola pasar dari waktu ke waktu.

---

### C. Trading Volume Activity

Volume transaksi mengalami perubahan yang cukup signifikan pada beberapa periode tertentu.

Lonjakan volume transaksi dapat mengindikasikan meningkatnya aktivitas pasar yang berpotensi memengaruhi pergerakan harga emas.

---

### D. Strong Correlation Between Price Variables

Variabel open, high, low, dan close memiliki hubungan yang sangat kuat satu sama lain karena merepresentasikan pergerakan harga emas pada periode yang sama.

Hubungan antar variabel ini dapat membantu proses machine learning dalam mengenali pola pergerakan harga emas dengan lebih baik.

---

## 3. Conclusion

Berdasarkan hasil exploratory data analysis, dataset historis harga emas memiliki pola tren dan hubungan antar variabel yang cukup baik untuk digunakan pada tahap machine learning.

Selain itu, proses data cleaning telah dilakukan dengan menghapus data yang tidak valid, mengubah tipe data, menjadikan kolom date sebagai index, serta menghapus kolom yang tidak digunakan.

Dataset hasil cleaning kemudian disimpan dan siap digunakan untuk proses pengembangan model prediksi harga emas.