# 🚀 Quick Start Guide - Streamlit Dashboard yang Ditingkatkan

## 📋 Prasyarat

- Python 3.8+
- pip package manager
- Data CSV dengan format yang sesuai

## ⚡ Setup Cepat (5 Menit)

### 1️⃣ Install Dependencies

```bash
# Masuk ke direktori project
cd /workspaces/pemodelan3

# Install semua package
pip install -r requirements.txt
```

### 2️⃣ Jalankan Aplikasi

```bash
streamlit run streamlit_app_improved.py
```

Browser akan otomatis membuka http://localhost:8501

### 3️⃣ Upload Dataset

- Klik tombol "📤 Upload dataset CSV"
- Pilih file CSV Anda
- Tunggu preview data muncul

## 📊 Format Dataset yang Diperlukan

CSV file Anda **harus** memiliki kolom berikut:

```
full_text             <- Teks postingan utama
created_at            <- Tanggal/waktu postingan (YYYY-MM-DD HH:MM:SS)
full_text_comments    <- Teks komentar/reply
```

**Kolom Opsional (untuk evaluasi metrics):**
```
expert_stance         <- Label manual (POSITIVE, NEGATIVE, NEUTRAL)
```

### Contoh Dataset Format:

```csv
full_text,created_at,full_text_comments,expert_stance
"Kebijakan baru sangat bagus","2024-01-01 10:30:00","Saya setuju dengan ini","POSITIVE"
"Keputusan ini salah","2024-01-02 11:45:00","Ini kesalahan pemerintah","NEGATIVE"
"Informasi penting","2024-01-03 12:00:00","Menarik untuk dianalisis","NEUTRAL"
```

## 🎯 Workflow Aplikasi

### Mode 1: 🔍 Analisis (Default)

Langkah-langkah otomatis:

```
1. Upload CSV
   ↓
2. Preview Data & Statistik
   ↓
3. Loading Models (embedding + sentiment)
   ↓
4. Data Preprocessing
   - Membersihkan posts
   - Membersihkan comments
   ↓
5. Topic Modeling dengan st.status()
   - Embedding
   - Clustering
   - Topic Extraction
   ↓
6. Hasil Topic Modeling
   - Topics Over Time (graph)
   - Word Clouds per Topic
   - Top Topics Table
   ↓
7. Stance Analysis dengan st.status()
   - Sentiment classification
   - Confidence scoring
   ↓
8. Hasil & Metrics
   - Sample hasil
   - Evaluation metrics (jika ada expert_stance)
   ↓
9. Success Summary
```

### Mode 2: 🧑‍💼 Validasi Ahli Diplomasi

(Tersedia setelah menjalankan Mode Analisis)

- Validasi hasil Stance
- Validasi hasil Topic
- Export hasil validasi

## 🎨 Fitur-Fitur Utama

### ✨ Visual Feedback yang Lebih Baik

| Fitur | Fungsi |
|-------|--------|
| **st.status()** | Container yang expand/collapse untuk feedback status proses |
| **Lottie Animation** | Animasi saat loading models |
| **st.toast()** | Notifikasi pop-up saat tahap selesai |
| **Color-coded boxes** | Kotak status dengan warna untuk sub-tahap |
| **Metrik Cards** | Display KPI dalam format card yang professional |

### 📊 Progress Tracking

Progress bar menampilkan:
- Persentase completion
- Jumlah dokumen/komentar diproses
- Waktu elapsed
- Detail sub-tahap

### 🎬 Animasi & Emoji

- Consistent emoji usage untuk visual hierarchy
- Lottie animations saat loading
- Color-coded background untuk berbagai status

## 💾 Output Files

Setelah analisis selesai, file berikut tersimpan di folder `results/`:

```
results/
├── original_data_[timestamp].csv          <- Data asli
├── posts_with_topics_[timestamp].csv      <- Posts + Topic
├── comments_with_stance_[timestamp].csv   <- Comments + Sentiment
├── top_topics_[timestamp].csv             <- Daftar topics
├── topic_validation_[timestamp].csv       <- Untuk validasi
├── coherence_results_[timestamp].json     <- Metrics coherence
├── topic_metrics_[timestamp].json         <- Metrics topic
├── topics_over_time_[timestamp].html      <- Interactive graph
├── wordcloud_topic_*.png                  <- Word clouds per topic
└── sentiment_distribution_[timestamp].html <- Sentiment visualization
```

## 🔧 Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'streamlit_lottie'"

**Solusi:**
```bash
pip install streamlit-lottie>=0.0.5
```

### ❌ Error: "Gensim not available"

**Solusi:**
```bash
pip install gensim
```

### ❌ Animasi Lottie tidak muncul

**Solusi:**
- Check koneksi internet (Lottie diload dari URL)
- Buka browser console untuk cek error
- Animasi adalah optional, aplikasi tetap jalan tanpa itu

### ❌ Proses sangat lambat

**Solusi:**
- Reduce jumlah dokumen (test dengan subset dulu)
- Gunakan GPU jika tersedia
- Pastikan tidak ada aplikasi berat lain berjalan

### ❌ CSV tidak terdeteksi dengan benar

**Solusi:**
- Pastikan file format UTF-8 (bukan UTF-16 atau lainnya)
- Cek kolom nama: persis `full_text`, `created_at`, `full_text_comments`
- Pastikan tidak ada space di nama kolom

## 🎯 Contoh Penggunaan

### Test dengan Sample Data

Jika ingin test dengan data kecil dulu:

```bash
# File sample sudah ada di workspace
# Contoh gunakan sample_posts_comments.csv
```

### Customize Aplikasi

Edit `streamlit_app_improved.py` untuk:

**Ubah warna:**
```python
# Cari: background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
# Ganti dengan warna pilihan Anda
```

**Ubah Lottie URL:**
```python
# Cari: LOTTIE_LOADING = "https://lottie.host/..."
# Ganti dengan URL lain dari https://lottiefiles.com/
```

**Ubah messages:**
```python
# Cari: st.write("...")
# Ganti dengan message Anda
```

## 📚 Dokumentasi Lengkap

Untuk penjelasan detail tentang setiap fitur, baca:
- **[UI_IMPROVEMENTS.md](./UI_IMPROVEMENTS.md)** - Penjelasan teknis semua fitur baru

## 🆘 Need Help?

Jika ada masalah:

1. Check Streamlit logs:
   ```bash
   streamlit run streamlit_app_improved.py --logger.level=debug
   ```

2. Baca dokumentasi resmi:
   - [Streamlit Docs](https://docs.streamlit.io/)
   - [Streamlit Lottie](https://github.com/anmolagarwal-dev/streamlit-lottie)

3. Check file logs di terminal output

## ✅ Checklist Sebelum Deploy

- [ ] Python 3.8+ installed
- [ ] All requirements installed (`pip install -r requirements.txt`)
- [ ] Internet connection available (untuk Lottie animations)
- [ ] Dataset CSV sudah siap dengan format yang benar
- [ ] Folder `results/` writable (untuk save results)
- [ ] Sufficient RAM untuk BERTopic & BERT models (~4GB minimum)

## 🎉 Hasilnya

Aplikasi Anda sekarang memiliki:

✅ Modern & professional UI
✅ Real-time feedback visual
✅ Engaging animations
✅ Clear progress tracking
✅ Professional metrics display
✅ Better user experience overall

---

**Last Updated**: April 29, 2026
**Version**: 1.0 - Improved Edition
