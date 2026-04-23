# Menggunakan image base Python 3.10
FROM python:3.10-slim

# Menyiapkan environment variable untuk Hugging Face
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Membuat non-root user (Wajib di Hugging Face)
RUN useradd -m -u 1000 user

# Berpindah ke user yang baru dibuat
USER user

# Set working directory
WORKDIR $HOME/app

# Menyalin requirements dan menginstall dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode sumber ke container dengan hak akses user
COPY --chown=user . .

# Membuat folder instance jika belum ada agar SQLite bisa menulis data
RUN mkdir -p $HOME/app/instance

# Mengekspos port 7860 (Standar Hugging Face Spaces)
EXPOSE 7860

# Menjalankan aplikasi menggunakan Gunicorn
CMD gunicorn --bind 0.0.0.0:7860 --workers 1 run:app
