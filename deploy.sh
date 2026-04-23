#!/bin/bash
# Script Deployment StockIQ untuk Oracle Cloud (Ubuntu 22.04)

echo "🔄 Memulai deployment StockIQ..."

# Pindah ke direktori proyek (sesuaikan path ini nanti jika perlu)
# cd /var/www/stockiq

# 1. Update kode terbaru dari GitHub
echo "📥 Menarik kode terbaru dari Git..."
git pull origin main

# 2. Hentikan container yang sedang berjalan
echo "🛑 Menghentikan container lama..."
docker-compose down

# 3. Build ulang image (berjaga-jaga jika ada perubahan di requirements.txt)
echo "🏗️ Membangun ulang Docker image..."
docker-compose build

# 4. Jalankan kembali container di background (detached mode)
echo "🚀 Menjalankan container baru..."
docker-compose up -d

# 5. Membersihkan image/container lama yang tidak terpakai agar server tidak penuh
echo "🧹 Membersihkan sisa container lama..."
docker system prune -f

echo "✅ Deployment selesai! Aplikasi StockIQ sudah berjalan kembali."
