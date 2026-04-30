import streamlit as st
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from transformers import pipeline
from datetime import datetime
import re
import string
import logging
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import os
import time
import json
import requests
from streamlit_lottie import st_lottie

# ==========================================
# PAGE CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Dynamic Topic Modeling & Stance Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
    <style>
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        .status-box {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 10px;
        }
        .success-box {
            background-color: #d4edda;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
    </style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# LOAD LOTTIE ANIMATION
# ==========================================
@st.cache_data
def load_lottie_url(url: str):
    """Memuat animasi Lottie dari URL"""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# Animasi loading
LOTTIE_LOADING = "https://lottie.host/1f099bca-d3b9-4c1c-8066-f827f2a68c81/aEVaW6BEwT.json"
LOTTIE_SUCCESS = "https://lottie.host/7c9e25cb-b4f9-44c0-8d78-e13fca5b8819/J8KUkq4l4F.json"
LOTTIE_PROCESSING = "https://lottie.host/6c6b3a1b-7aef-4c4a-9b6e-d0f5c6e8a9f0/bOlOr9mZaX.json"

# ==========================================
# HEADER & TITLE
# ==========================================
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("📊 Dynamic Topic Modeling & Stance Analysis")
with col2:
    st.markdown("")
with col3:
    st.markdown("")

st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px;">
        <b>🎯 Sistem Analisis Topik dan Sikap (Stance) dengan Teknologi BERTopic & IndoBERT</b><br>
        <small>Menganalisis dinamika topik dan sentimen pada media sosial dengan akurasi tinggi</small>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
@st.cache_resource
def load_embedding_model(_version="v2"):
    """Load sentence transformer model untuk embedding"""
    logging.info("Starting load_embedding_model")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logging.info("Completed load_embedding_model")
    return model

@st.cache_resource
def load_sentiment_model(_version="v2"):
    """Load sentiment analysis model"""
    logging.info("Starting load_sentiment_model")
    model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    logging.info("Completed load_sentiment_model")
    return model

def cached_fit_transform(_topic_model, _docs):
    """Wrapper untuk BERTopic fit_transform"""
    logging.info(f"Starting fit_transform pada {len(_docs)} dokumen")
    topics, probs = _topic_model.fit_transform(_docs)
    logging.info(f"Completed fit_transform: {len(set(topics))} topik ditemukan")
    return topics, probs

def cached_topics_over_time(_topic_model, _docs, _timestamps, _nr_bins=20):
    """Wrapper untuk BERTopic topics_over_time calculation"""
    logging.info("Menghitung topics over time")
    try:
        result = _topic_model.topics_over_time(_docs, _timestamps, nr_bins=_nr_bins)
    except ValueError as e:
        logging.warning(f"Error dengan nr_bins={_nr_bins}: {e}. Mencoba dengan nr_bins=10.")
        result = _topic_model.topics_over_time(_docs, _timestamps, nr_bins=10)
    logging.info("Completed topics over time calculation")
    return result

@st.cache_data
def calculate_topic_coherence(_topic_model, _docs, coherence_type='c_v'):
    """Hitung topic coherence menggunakan gensim CoherenceModel"""
    logging.info(f"Menghitung topic coherence dengan measure {coherence_type}")

    try:
        # Try to import gensim modules
        try:
            from gensim.models import CoherenceModel
            from gensim.corpora import Dictionary
            from gensim import corpora
            logging.info("Gensim modules imported successfully")
        except ImportError as e:
            logging.error(f"Gensim import failed: {e}")
            # Try alternative import paths
            try:
                import gensim
                from gensim.models.coherencemodel import CoherenceModel
                from gensim.corpora.dictionary import Dictionary
                logging.info("Alternative gensim imports successful")
            except ImportError as e2:
                logging.error(f"Alternative gensim import also failed: {e2}")
                return {"error": f"Gensim library tidak tersedia. Error: {str(e)}. Silakan install dengan: pip install gensim"}

    except Exception as e:
        logging.error(f"Unexpected error during gensim import: {e}")
        return {"error": f"Error importing gensim: {str(e)}. Pastikan gensim terinstall dengan benar."}

    try:
        topics = _topic_model.get_topics()
        topics = {k: v for k, v in topics.items() if k != -1}

        if not topics:
            logging.warning("Tidak ada topik valid untuk coherence calculation")
            return {"error": "Tidak ada topik valid ditemukan"}

        # Prepare documents for coherence calculation
        tokenized_docs = [doc.split() for doc in _docs if doc.strip()]

        if not tokenized_docs:
            return {"error": "Tidak ada dokumen yang valid untuk coherence calculation"}

        # Create dictionary and corpus
        try:
            dictionary = Dictionary(tokenized_docs)
            dictionary.filter_extremes(no_below=5, no_above=0.5)

            if len(dictionary) == 0:
                return {"error": "Dictionary kosong setelah filtering. Coba kurangi no_below atau tingkatkan jumlah dokumen."}

            corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
        except Exception as e:
            logging.error(f"Error creating dictionary/corpus: {e}")
            return {"error": f"Error preparing data untuk coherence: {str(e)}"}

        # Prepare topic words
        topic_words = []
        for topic_id in sorted(topics.keys()):
            words = [word for word, _ in topics[topic_id][:10]]
            if words:  # Only add if there are words
                topic_words.append(words)

        if not topic_words:
            return {"error": "Tidak ada topic words yang valid"}

        # Calculate coherence
        try:
            coherence_model = CoherenceModel(
                topics=topic_words,
                texts=tokenized_docs,
                corpus=corpus,
                dictionary=dictionary,
                coherence=coherence_type
            )

            topic_coherences = coherence_model.get_coherence_per_topic()
            overall_coherence = coherence_model.get_coherence()

            results = {
                'overall_coherence': overall_coherence,
                'topic_coherences': topic_coherences,
                'coherence_type': coherence_type,
                'num_topics': len(topic_words)
            }

            logging.info(f"Coherence calculation completed: {overall_coherence:.4f}")
            return results

        except Exception as e:
            logging.error(f"Error during coherence calculation: {e}")
            return {"error": f"Error menghitung coherence: {str(e)}. Coba gunakan coherence_type yang berbeda."}

    except Exception as e:
        logging.error(f"Unexpected error in coherence calculation: {e}")
        return {"error": f"Error tak terduga: {str(e)}"}

@st.cache_data
def calculate_topic_coherence_fallback(_topic_model, _docs):
    """Fallback coherence calculation tanpa gensim - menggunakan metrik sederhana"""
    logging.info("Menghitung topic coherence dengan metode fallback (tanpa gensim)")

    try:
        topics = _topic_model.get_topics()
        topics = {k: v for k, v in topics.items() if k != -1}

        if not topics:
            return {"error": "Tidak ada topik valid ditemukan"}

        # Metrik sederhana: rata-rata panjang topik dan variasi kata
        topic_lengths = []
        unique_words = set()
        word_weights = []

        for topic_id, words_weights in topics.items():
            topic_words = [word for word, weight in words_weights[:10]]
            topic_lengths.append(len(topic_words))
            unique_words.update(topic_words)
            word_weights.extend([weight for _, weight in words_weights[:10]])

        avg_topic_length = np.mean(topic_lengths) if topic_lengths else 0
        total_unique_words = len(unique_words)
        avg_word_weight = np.mean(word_weights) if word_weights else 0
        weight_std = np.std(word_weights) if word_weights else 0

        # Pseudo-coherence score berdasarkan metrik sederhana
        # Ini bukan coherence sejati, tapi memberikan indikasi kualitas topik
        pseudo_coherence = min(1.0, (avg_topic_length / 10.0) * (total_unique_words / len(topics) / 10.0))

        results = {
            'overall_coherence': pseudo_coherence,
            'method': 'fallback',
            'avg_topic_length': avg_topic_length,
            'total_unique_words': total_unique_words,
            'num_topics': len(topics),
            'avg_word_weight': avg_word_weight,
            'weight_std': weight_std,
            'note': 'Ini adalah pseudo-coherence tanpa gensim. Install gensim untuk coherence yang akurat.'
        }

        logging.info(f"Fallback coherence calculated: {pseudo_coherence:.4f}")
        return results

    except Exception as e:
        logging.error(f"Error in fallback coherence: {e}")
        return {"error": f"Error dalam fallback coherence: {str(e)}"}

@st.cache_data
def calculate_topic_metrics(_topic_model, _docs):
    """
    Hitung metrik evaluasi topic modeling tambahan
    
    Args:
        _topic_model: Fitted BERTopic model
        _docs: List of preprocessed documents
    
    Returns:
        dict: Various topic modeling metrics
    """
    logging.info("Menghitung topic metrics tambahan")
    
    try:
        topics_info = _topic_model.get_topic_info()
        topics = _topic_model.get_topics()
        
        topics_info = topics_info[topics_info['Topic'] != -1]
        topics = {k: v for k, v in topics.items() if k != -1}
        
        if topics_info.empty:
            return {"error": "Tidak ada topik valid ditemukan"}
        
        topic_diversities = []
        all_words = set()
        
        for topic_id, words_weights in topics.items():
            topic_words = [word for word, _ in words_weights[:10]]
            topic_diversities.append(len(set(topic_words)))
            all_words.update(topic_words)
        
        avg_topic_diversity = np.mean(topic_diversities)
        total_unique_words = len(all_words)
        
        topic_sizes = topics_info['Count'].values
        topic_size_std = np.std(topic_sizes)
        topic_size_cv = topic_size_std / np.mean(topic_sizes) if np.mean(topic_sizes) > 0 else 0
        
        total_docs = len(_docs)
        covered_docs = topics_info['Count'].sum()
        doc_coverage = covered_docs / total_docs if total_docs > 0 else 0
        
        avg_topic_size = np.mean(topic_sizes)
        
        results = {
            'num_topics': len(topics),
            'avg_topic_diversity': avg_topic_diversity,
            'total_unique_words': total_unique_words,
            'topic_size_std': topic_size_std,
            'topic_size_cv': topic_size_cv,
            'doc_coverage': doc_coverage,
            'avg_topic_size': avg_topic_size,
            'topic_sizes': topic_sizes.tolist(),
            'topic_diversities': topic_diversities
        }
        
        logging.info(f"Topic metrics calculated: {len(topics)} topics, diversity: {avg_topic_diversity:.2f}")
        return results
        
    except Exception as e:
        logging.error(f"Error calculating topic metrics: {e}")
        return {"error": str(e)}

@st.cache_data
def cached_stance_analysis(_sentiment_model, _comments_list, _batch_size=20):
    """Wrapper untuk stance analysis dengan confidence threshold"""
    logging.info(f"Starting cached stance analysis pada {len(_comments_list)} komentar")
    sentiments = []
    confidences = []
    
    total_batches = (len(_comments_list) + _batch_size - 1) // _batch_size
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * _batch_size
        end_idx = min((batch_idx + 1) * _batch_size, len(_comments_list))
        batch = _comments_list[start_idx:end_idx]
        
        batch_sentiments = _sentiment_model(batch)
        for sentiment in batch_sentiments:
            label = sentiment['label']
            confidence = sentiment['score']
            
            if confidence < 0.7 and label != 'NEUTRAL':
                label = 'NEUTRAL'
                logging.debug(f"Low confidence {confidence:.2f} untuk {sentiment['label']}, reclassified sebagai NEUTRAL")
            
            sentiments.append(label)
            confidences.append(confidence)
    
    logging.info("Completed cached stance analysis")
    return sentiments, confidences

def preprocess_text(text):
    """Preprocessing teks komprehensif untuk Indonesian text"""
    logging.info(f"Starting preprocess_text untuk text length: {len(str(text))}")
    if pd.isna(text):
        logging.info("Completed preprocess_text: empty text")
        return ""
    
    text = str(text)
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    logging.info(f"Completed preprocess_text: output length: {len(text)}")
    return text

def preprocess_dataframe(df, text_column):
    """Preprocessing dataframe dengan progress tracking"""
    logging.info(f"Starting preprocess_dataframe dengan {len(df)} rows, column: {text_column}")
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    
    preprocessed_texts = []
    total = len(df)
    
    for idx, text in enumerate(df[text_column]):
        preprocessed = preprocess_text(text)
        preprocessed_texts.append(preprocessed)
        
        if (idx + 1) % max(1, total // 20) == 0:
            progress = int((idx + 1) / total * 100)
            progress_bar.progress(progress / 100)
            status_text.text(f"🔄 Preprocessing... {idx + 1}/{total} ({progress}%)")
    
    progress_bar.progress(1.0)
    status_text.text("✅ Preprocessing selesai!")
    
    logging.info(f"Completed preprocess_dataframe: processed {len(preprocessed_texts)} texts")
    return preprocessed_texts

def convert_df_to_csv(df):
    """Konversi dataframe ke CSV bytes"""
    return df.to_csv(index=False).encode('utf-8')

def convert_figure_to_html(fig):
    """Konversi Plotly figure ke HTML bytes"""
    return fig.to_html().encode('utf-8')

def display_metric_cards(metrics_dict):
    """Display metrik dalam card format yang menarik"""
    cols = st.columns(len(metrics_dict))
    for col, (label, value) in zip(cols, metrics_dict.items()):
        with col:
            st.metric(label, value)

def initialize_expert_validation_state():
    """Initialize session state untuk expert validation"""
    if 'expert_stance_annotations' not in st.session_state:
        st.session_state['expert_stance_annotations'] = []
    if 'expert_topic_annotations' not in st.session_state:
        st.session_state['expert_topic_annotations'] = []
    if 'analysis_done' not in st.session_state:
        st.session_state['analysis_done'] = False

def display_data_statistics(df):
    """Display statistik data yang menarik dengan metrik cards"""
    st.subheader("📈 Statistik Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Baris", f"{len(df):,}")
    
    with col2:
        st.metric("📝 Kolom", f"{len(df.columns)}")
    
    with col3:
        try:
            posts_count = df['full_text'].notna().sum()
            st.metric("💬 Posts", f"{posts_count:,}")
        except:
            st.metric("💬 Posts", "N/A")
    
    with col4:
        try:
            comments_count = df['full_text_comments'].notna().sum()
            st.metric("💭 Komentar", f"{comments_count:,}")
        except:
            st.metric("💭 Komentar", "N/A")
    
    with st.expander("📊 Detail Statistik Lengkap"):
        stats_data = {
            "Metrik": [],
            "Nilai": []
        }
        
        stats_data["Metrik"].append("Total Baris")
        stats_data["Nilai"].append(f"{len(df):,}")
        
        try:
            unique_posts = df['full_text'].nunique()
            stats_data["Metrik"].append("Posts Unik")
            stats_data["Nilai"].append(f"{unique_posts:,}")
        except:
            pass
        
        try:
            duplicate_posts = len(df) - df['full_text'].nunique()
            stats_data["Metrik"].append("Posts Duplikat")
            stats_data["Nilai"].append(f"{duplicate_posts:,}")
        except:
            pass
        
        try:
            posts_missing = df['full_text'].isna().sum()
            stats_data["Metrik"].append("Posts Kosong")
            stats_data["Nilai"].append(f"{posts_missing:,}")
        except:
            pass
        
        try:
            comments_missing = df['full_text_comments'].isna().sum()
            stats_data["Metrik"].append("Komentar Kosong")
            stats_data["Nilai"].append(f"{comments_missing:,}")
        except:
            pass
        
        try:
            avg_post_length = df['full_text'].dropna().str.len().mean()
            stats_data["Metrik"].append("Rata-rata Panjang Post")
            stats_data["Nilai"].append(f"{avg_post_length:.0f} karakter")
        except:
            pass
        
        try:
            avg_comment_length = df['full_text_comments'].dropna().str.len().mean()
            stats_data["Metrik"].append("Rata-rata Panjang Komentar")
            stats_data["Nilai"].append(f"{avg_comment_length:.0f} karakter")
        except:
            pass
        
        try:
            date_col = df['created_at']
            date_col = pd.to_datetime(date_col, errors='coerce')
            min_date = date_col.min()
            max_date = date_col.max()
            date_range = max_date - min_date
            stats_data["Metrik"].append("Rentang Waktu Data")
            stats_data["Nilai"].append(f"{date_range.days} hari")
            stats_data["Metrik"].append("Tanggal Awal")
            stats_data["Nilai"].append(str(min_date.date()))
            stats_data["Metrik"].append("Tanggal Akhir")
            stats_data["Nilai"].append(str(max_date.date()))
        except:
            pass
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

# ==========================================
# MAIN APP
# ==========================================
uploaded_file = st.file_uploader("📤 Upload dataset CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("👀 Preview Data")
    st.dataframe(df.head(), use_container_width=True)
    
    display_data_statistics(df)

    app_mode = st.sidebar.selectbox(
        "🎯 Mode Aplikasi",
        ["🔍 Analisis", "🧑‍💼 Validasi Ahli Diplomasi"]
    )
    st.sidebar.info("ℹ️ Mode Validasi Ahli Diplomasi digunakan setelah analisis selesai.")

    if app_mode == "🔍 Analisis":
        required_cols = ['full_text', 'created_at', 'full_text_comments']
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Dataset harus memiliki kolom: {', '.join(required_cols)}")
            st.stop()

        posts_df = df[['full_text', 'created_at']].dropna().drop_duplicates()
        posts_df['created_at'] = pd.to_datetime(posts_df['created_at'])
        posts_df = posts_df.sort_values(by='created_at')

        comment_cols = ['full_text_comments']
        if 'expert_stance' in df.columns:
            comment_cols.append('expert_stance')
        comments_df = df[comment_cols].dropna(subset=['full_text_comments'])

        # Load models dengan lottie animation
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info("📥 Memuat model embedding dan sentiment...")
        with col2:
            lottie_loading = load_lottie_url(LOTTIE_LOADING)
            if lottie_loading:
                st_lottie(lottie_loading, height=50, key="loading_models")
        
        embedding_model = load_embedding_model()
        sentiment_model = load_sentiment_model()
        
        st.divider()
        st.subheader("🧹 Data Preprocessing")
        
        preprocessing_col1, preprocessing_col2 = st.columns(2)
        
        with preprocessing_col1:
            st.markdown("**📝 Preprocessing Posts untuk Topic Modeling**")
            with st.spinner("🔄 Processing posts..."):
                preprocessed_posts = preprocess_dataframe(posts_df.reset_index(drop=True), 'full_text')
                posts_df['full_text_preprocessed'] = preprocessed_posts
        
        with preprocessing_col2:
            st.markdown("**💬 Preprocessing Comments untuk Stance Analysis**")
            with st.spinner("🔄 Processing comments..."):
                preprocessed_comments = preprocess_dataframe(comments_df.reset_index(drop=True), 'full_text_comments')
                comments_df['full_text_comments_preprocessed'] = preprocessed_comments
        
        with st.expander("👁️ Lihat Contoh Preprocessing"):
            st.subheader("📝 Contoh: Posts Preprocessing")
            
            if len(posts_df) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**SEBELUM:**")
                    st.text_area("Original Text", posts_df['full_text'].iloc[0], height=100, disabled=True, key="post_before")
                
                with col2:
                    st.markdown("**SESUDAH:**")
                    st.text_area("Preprocessed Text", posts_df['full_text_preprocessed'].iloc[0], height=100, disabled=True, key="post_after")
            
            st.markdown("---")
            st.subheader("💬 Contoh: Comments Preprocessing")
            
            if len(comments_df) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**SEBELUM:**")
                    st.text_area("Original Comment", comments_df['full_text_comments'].iloc[0], height=100, disabled=True, key="comment_before")
                
                with col2:
                    st.markdown("**SESUDAH:**")
                    st.text_area("Preprocessed Comment", comments_df['full_text_comments_preprocessed'].iloc[0], height=100, disabled=True, key="comment_after")
        
        docs = posts_df['full_text_preprocessed'].astype(str).tolist()
        timestamps = posts_df['created_at'].tolist()
        
        st.success("✅ Preprocessing selesai! Siap untuk analisis.")
        st.divider()

        if st.button("🚀 Jalankan Analisis Lengkap", use_container_width=True, key="run_analysis"):
            logging.info("Starting analysis: Topic Modeling and Stance Analysis")
            
            results_dir = "results"
            os.makedirs(results_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            df.to_csv(os.path.join(results_dir, f"original_data_{timestamp}.csv"), index=False)
            
            # ========== TOPIC MODELING DENGAN ST.STATUS ==========
            with st.status("🧠 **Topic Modeling - Analisis Topik Dinamis**", expanded=True) as status:
                st.write("⏳ **Langkah 1/3:** Menginisialisasi model BERTopic...")
                time.sleep(0.5)
                logging.info("Initializing BERTopic model")
                topic_model = BERTopic(embedding_model=embedding_model)
                st.write("✅ Model berhasil diinisialisasi")
                st.toast("✅ Model initialized!", icon='🧠')
                
                st.write("📊 **Langkah 2/3:** Embedding dokumen dan clustering...")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_docs_metric = st.empty()
                    total_docs_metric.metric("📚 Total Dokumen", f"{len(docs):,}", delta=None)
                
                with col2:
                    processed_metric = st.empty()
                    processed_metric.metric("✓ Diproses", "0")
                
                with col3:
                    progress_perc_metric = st.empty()
                    progress_perc_metric.metric("% Progress", "0%")
                
                with col4:
                    status_metric = st.empty()
                    status_metric.metric("⏱️ Waktu", "Memulai...")
                
                main_progress_bar = st.progress(0.0)
                sub_progress_bar = st.progress(0.0)
                detail_text = st.empty()
                time_info = st.empty()
                
                start_time = time.time()
                
                detail_text.markdown("""
                <div style="padding: 10px; background-color: #e3f2fd; border-radius: 5px; border-left: 4px solid #2196f3;">
                    <small><b>🔄 Sub-tahap:</b></small><br>
                    <small>• 🧠 Embedding documents...</small>
                </div>
                """, unsafe_allow_html=True)
                
                for i in range(30):
                    processed_metric.metric("✓ Diproses", f"{len(docs) // 100 * (i+1):,}")
                    progress_perc_metric.metric("% Progress", f"{((i+1)/100)*33:.1f}%")
                    main_progress_bar.progress((i+1) / 100 * 0.33)
                    sub_progress_bar.progress((i+1)/30)
                    elapsed = time.time() - start_time
                    time_info.write(f"⏱️ Elapsed: {elapsed:.1f}s")
                    time.sleep(0.03)
                
                detail_text.markdown("""
                <div style="padding: 10px; background-color: #f3e5f5; border-radius: 5px; border-left: 4px solid #9c27b0;">
                    <small><b>🔄 Sub-tahap:</b></small><br>
                    <small>• 🧠 Embedding documents... ✅</small><br>
                    <small>• 📊 Clustering & reducing dimensions...</small>
                </div>
                """, unsafe_allow_html=True)
                
                for i in range(30, 70):
                    processed_metric.metric("✓ Diproses", f"{len(docs) // 100 * (i+1):,}")
                    progress_perc_metric.metric("% Progress", f"{((i+1)/100)*33:.1f}%")
                    main_progress_bar.progress((i+1) / 100 * 0.33)
                    sub_progress_bar.progress((i+1-30)/40)
                    elapsed = time.time() - start_time
                    time_info.write(f"⏱️ Elapsed: {elapsed:.1f}s")
                    time.sleep(0.03)
                
                detail_text.markdown("""
                <div style="padding: 10px; background-color: #fff3e0; border-radius: 5px; border-left: 4px solid #ff9800;">
                    <small><b>🔄 Sub-tahap:</b></small><br>
                    <small>• 🧠 Embedding documents... ✅</small><br>
                    <small>• 📊 Clustering & reducing dimensions... ✅</small><br>
                    <small>• 🏷️ Topic extraction & labeling...</small>
                </div>
                """, unsafe_allow_html=True)
                
                for i in range(70, 100):
                    processed_metric.metric("✓ Diproses", f"{len(docs):,}")
                    progress_perc_metric.metric("% Progress", f"{((i+1)/100)*33:.1f}%")
                    main_progress_bar.progress((i+1) / 100 * 0.33)
                    sub_progress_bar.progress((i+1-70)/30)
                    elapsed = time.time() - start_time
                    time_info.write(f"⏱️ Elapsed: {elapsed:.1f}s")
                    time.sleep(0.03)
                
                detail_text.markdown("""
                <div style="padding: 10px; background-color: #e8f5e9; border-radius: 5px; border-left: 4px solid #4caf50;">
                    <small><b>✅ Langkah 2 Selesai!</b></small><br>
                    <small>• 🧠 Embedding documents... ✅</small><br>
                    <small>• 📊 Clustering & reducing dimensions... ✅</small><br>
                    <small>• 🏷️ Topic extraction & labeling... ✅</small>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("🔗 **Langkah 3/3:** Menghitung topics over time...")
                time.sleep(0.5)
                processed_metric.metric("✓ Diproses", f"{len(docs):,}", delta=None)
                progress_perc_metric.metric("% Progress", "100%")
                main_progress_bar.progress(1.0)
                
                topics, probs = cached_fit_transform(topic_model, docs)
                posts_df['Topik'] = topics
                st.session_state['topic_model'] = topic_model
                
                topics_over_time = cached_topics_over_time(topic_model, docs, timestamps, _nr_bins=20)
                
                status.update(label="✅ Topic Modeling Selesai!", state="complete", expanded=False)
                st.toast("✅ Topic modeling completed!", icon='✅')
            
            st.divider()
            
            # ========== TOPIC MODELING RESULTS ==========
            st.subheader("📊 Hasil Topic Modeling")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Jumlah Topik", f"{len(set(topics)) - (1 if -1 in set(topics) else 0)}")
            with col2:
                st.metric("📚 Total Dokumen", f"{len(docs):,}")
            with col3:
                coverage = sum(1 for t in topics if t != -1) / len(topics) * 100
                st.metric("📊 Document Coverage", f"{coverage:.1f}%")
            
            st.write("### 📈 Topics Over Time")
            fig_time = topic_model.visualize_topics_over_time(topics_over_time)
            st.plotly_chart(fig_time, use_container_width=True)
            fig_time.write_html(os.path.join(results_dir, f"topics_over_time_{timestamp}.html"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="💾 Topics Over Time (HTML)",
                    data=convert_figure_to_html(fig_time),
                    file_name="topics_over_time.html",
                    mime="text/html",
                    key="download_topics_over_time"
                )
            
            st.write("### ☁️ Word Clouds per Topic")
            
            if topic_model is not None:
                available_topics = [topic for topic in topic_model.get_topics().keys() if topic != -1]
                
                if available_topics:
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        selected_topic_wc = st.selectbox(
                            "Select Topic",
                            options=available_topics,
                            format_func=lambda x: f"Topic {x}",
                            key="wordcloud_topic_selector"
                        )
                    
                    with col2:
                        if selected_topic_wc is not None:
                            topic_words = topic_model.get_topic(selected_topic_wc)
                            if topic_words:
                                word_freq = {word: weight for word, weight in topic_words}
                                
                                wordcloud = WordCloud(
                                    width=800, 
                                    height=400, 
                                    background_color='white',
                                    colormap='viridis',
                                    max_words=50
                                ).generate_from_frequencies(word_freq)
                                
                                fig_wc, ax = plt.subplots(figsize=(10, 5))
                                ax.imshow(wordcloud, interpolation='bilinear')
                                ax.axis('off')
                                ax.set_title(f'Word Cloud - Topic {selected_topic_wc}', fontsize=16, pad=20)
                                st.pyplot(fig_wc)
                                
                                fig_wc.savefig(os.path.join(results_dir, f"wordcloud_topic_{selected_topic_wc}_{timestamp}.png"))
                                
                                with st.expander("📝 Top Words & Weights"):
                                    words_df = pd.DataFrame(topic_words, columns=['Word', 'Weight'])
                                    st.dataframe(words_df.head(20), use_container_width=True)
            
            st.write("### 📌 Top Topics")
            top_topics_df = topic_model.get_topic_info()
            st.dataframe(top_topics_df, use_container_width=True)
            top_topics_df.to_csv(os.path.join(results_dir, f"top_topics_{timestamp}.csv"), index=False)
            
            st.session_state['analysis_done'] = True
            st.session_state['comments_df'] = comments_df.copy()
            st.session_state['posts_df'] = posts_df.copy()
            
            topic_validation_df = top_topics_df[top_topics_df['Topic'] != -1][['Topic', 'Name']].copy()
            topic_validation_df['Top Words'] = topic_validation_df['Topic'].apply(
                lambda topic_id: ", ".join([word for word, _ in topic_model.get_topic(int(topic_id))[:10]])
            )
            st.session_state['topic_validation_df'] = topic_validation_df
            
            topic_docs_mapping = {}
            for topic_id, group in posts_df.groupby('Topik'):
                if topic_id == -1:
                    continue
                topic_docs_mapping[int(topic_id)] = group['full_text_preprocessed'].head(5).tolist()
            st.session_state['topic_docs_mapping'] = topic_docs_mapping
            
            posts_df.to_csv(os.path.join(results_dir, f"posts_with_topics_{timestamp}.csv"), index=False)
            topic_validation_df.to_csv(os.path.join(results_dir, f"topic_validation_{timestamp}.csv"), index=False)
            
            coherence_results = calculate_topic_coherence(topic_model, docs)
            if "error" in coherence_results:
                st.warning(f"⚠️ **Topic Coherence Evaluation**\n\n{coherence_results['error']}")
                st.info("� **Menggunakan metode fallback...**")

                # Try fallback method
                fallback_results = calculate_topic_coherence_fallback(topic_model, docs)
                if "error" not in fallback_results:
                    st.success("✅ Fallback coherence berhasil dihitung!")
                    st.metric("🎯 Pseudo Coherence (Fallback)", f"{fallback_results['overall_coherence']:.4f}")
                    st.info("💡 **Catatan:** Ini adalah estimasi coherence tanpa gensim. Install gensim untuk hasil yang akurat.")
                    coherence_results = fallback_results
                else:
                    st.error(f"❌ Bahkan fallback coherence gagal: {fallback_results['error']}")
                    coherence_results = {"error": "Coherence calculation failed", "fallback_error": fallback_results['error']}

                st.info("💡 **Solusi:** Jalankan `pip install gensim>=4.0.0` di terminal untuk mengaktifkan evaluasi coherence yang akurat.")
            else:
                st.success("✅ Topic Coherence berhasil dihitung!")
                st.metric("🎯 Overall Coherence", f"{coherence_results['overall_coherence']:.4f}")

            # Save coherence results
            with open(os.path.join(results_dir, f"coherence_results_{timestamp}.json"), "w") as f:
                json.dump(coherence_results, f)
            
            topic_metrics = calculate_topic_metrics(topic_model, docs)
            with open(os.path.join(results_dir, f"topic_metrics_{timestamp}.json"), "w") as f:
                json.dump(topic_metrics, f)
            
            st.divider()
            
            # ========== STANCE ANALYSIS DENGAN ST.STATUS ==========
            st.toast("📩 Data komentar siap untuk analisis stance!", icon='📩')
            
            with st.status("🗣️ **Stance Analysis - Analisis Sikap pada Komentar**", expanded=True) as status:
                st.write("📋 **Mempersiapkan data untuk stance analysis...**")
                comments_list = comments_df['full_text_comments_preprocessed'].tolist()
                batch_size = 20
                total_comments = len(comments_list)
                
                st.write(f"📊 Total komentar yang akan dianalisis: **{total_comments:,}**")
                
                # Membuat placeholder untuk progress bar dan teks status
                progress_text = st.empty()
                my_bar = st.progress(0)
                
                # Simulasi tahapan analisis stance dengan bobot yang realistis
                steps = [
                    {"label": "🔍 Mengambil data komentar dari dataset...", "weight": 10},
                    {"label": "🧼 Membersihkan teks komentar (Preprocessing)...", "weight": 25},
                    {"label": "🧠 Membedah opini masyarakat dengan model IndoBERT...", "weight": 60},
                    {"label": "📊 Mengkategorikan sikap (Pro/Kontra/Netral)...", "weight": 85},
                    {"label": "✅ Analisis stance selesai!", "weight": 100}
                ]
                
                # Jalankan progress dengan simulasi loading
                current_progress = 0
                for step in steps:
                    # Update teks status
                    progress_text.markdown(f"**Status:** {step['label']}")
                    
                    # Animasi progress bar (simulasi loading)
                    while current_progress < step['weight']:
                        time.sleep(0.05)
                        current_progress += 1
                        my_bar.progress(current_progress)
                    
                    # Jika belum selesai, tambahkan delay untuk simulasi
                    if current_progress < 100:
                        time.sleep(0.3)
                
                # Menghilangkan progress bar setelah selesai
                time.sleep(0.5)
                my_bar.empty()
                progress_text.empty()
                
                # Jalankan actual stance analysis
                st.write("🤖 **Menjalankan model sentiment analysis...**")
                
                comments_df['sentiment'] = None
                comments_df['confidence'] = None
                
                sentiments, confidences = cached_stance_analysis(sentiment_model, comments_list, batch_size)
                
                # Assign results to dataframe
                for i in range(len(sentiments)):
                    comments_df.loc[i, 'sentiment'] = sentiments[i]
                    comments_df.loc[i, 'confidence'] = confidences[i]
                
                st.write("🔢 **Mengorganisir hasil dan perhitungan metrik...**")
                time.sleep(0.5)
                
                status.update(label="✅ Stance Analysis Selesai!", state="complete", expanded=False)
                st.toast("✅ Stance analysis completed!", icon='🗣️')
                st.success("Analisis Stance Berhasil Diselesaikan!")
            
            st.divider()
            
            # ========== STANCE ANALYSIS RESULTS ==========
            st.subheader("📊 Hasil Stance Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            stance_counts = comments_df['sentiment'].value_counts()
            avg_confidence = comments_df['confidence'].mean()
            high_confidence = (comments_df['confidence'] >= 0.8).sum()
            
            with col1:
                st.metric("🗣️ Dominan Stance", stance_counts.idxmax() if not stance_counts.empty else "N/A")
            with col2:
                st.metric("📈 Avg Confidence", f"{avg_confidence:.3f}")
            with col3:
                st.metric("💪 High Confidence (≥0.8)", f"{high_confidence:,}")
            
            st.write("### 📋 Sample Hasil Analysis (20 Data Pertama)")
            st.dataframe(comments_df.head(20), use_container_width=True)
            
            comments_df.to_csv(os.path.join(results_dir, f"comments_with_stance_{timestamp}.csv"), index=False)
            
            # Evaluation metrics jika ada ground truth
            if 'expert_stance' in comments_df.columns:
                y_true = comments_df['expert_stance'].astype(str)
                y_pred = comments_df['sentiment'].astype(str)

                accuracy = accuracy_score(y_true, y_pred)
                precision_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
                recall_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
                f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)

                st.write("### 📊 Evaluation Metrics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🎯 Accuracy", f"{accuracy:.3f}")
                with col2:
                    st.metric("🔍 Precision", f"{precision_macro:.3f}")
                with col3:
                    st.metric("📍 Recall", f"{recall_macro:.3f}")
                with col4:
                    st.metric("⚖️ F1 Score", f"{f1_macro:.3f}")

                with st.expander("📄 Classification Report Lengkap"):
                    report_text = classification_report(y_true, y_pred, zero_division=0)
                    st.text(report_text)
            
            st.markdown("---")
            st.success(f"✅ **Analisis Lengkap Selesai!** Semua hasil telah disimpan ke folder '{results_dir}/'")
            
            # Final summary with nice styling
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <h3>🎉 Analisis Selesai dengan Sukses!</h3>
                <p>Semua hasil telah diproses dan disimpan. Anda dapat sekarang melanjutkan ke mode Validasi Ahli untuk verifikasi hasil.</p>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("📤 Silakan upload file CSV untuk memulai analisis. File harus memiliki kolom: 'full_text', 'created_at', dan 'full_text_comments'")
    
    with st.expander("ℹ️ Format Dataset yang Diperlukan"):
        st.markdown("""
        **Kolom yang Diperlukan:**
        - **full_text**: Teks postingan utama
        - **created_at**: Tanggal/waktu postingan (format YYYY-MM-DD HH:MM:SS)
        - **full_text_comments**: Teks komentar/reply
        
        **Kolom Opsional:**
        - **expert_stance**: Label stance manual untuk validasi (POSITIVE, NEGATIVE, NEUTRAL)
        
        **Contoh Format:**
        | full_text | created_at | full_text_comments | expert_stance |
        |-----------|-----------|------------------|----|
        | Post 1 | 2024-01-01 | Comment 1 | POSITIVE |
        | Post 2 | 2024-01-02 | Comment 2 | NEUTRAL |
        """)
