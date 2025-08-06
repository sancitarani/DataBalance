# Gunakan image Python 3.9 yang ramping sebagai dasar
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam kontainer
WORKDIR /app

# Instal dependensi sistem yang dibutuhkan untuk build pustaka Python
# build-essential untuk kompilasi, pkg-config dan libfreetype6-dev untuk matplotlib
RUN apt-get update && apt-get install -y build-essential pkg-config libfreetype6-dev libgomp1

# Salin file requirements.txt terlebih dahulu untuk caching yang lebih baik
COPY requirements.txt .

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa kode aplikasi ke dalam direktori kerja
COPY . .

# Perintah untuk menjalankan aplikasi saat kontainer dimulai
# Gunicorn akan berjalan di port 8080, yang akan diekspos oleh Fly.io
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
