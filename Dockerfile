# Menggunakan image base Python 3.10
FROM python:3.10-slim

# Menyiapkan working directory
WORKDIR /app

# Menyalin requirements dan menginstall dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode sumber ke container
COPY . .

# Mengekspos port 5000
EXPOSE 5000

# Menjalankan aplikasi menggunakan Gunicorn untuk production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]
