# Pemodelan Topik Dinamis - Copilot Instructions

## 🎯 Project Overview

This is a comprehensive Indonesian NLP/ML project for dynamic topic modeling and stance analysis on social media data. The system combines BERTopic for topic modeling with IndoBERT for stance/sentiment classification, providing both ML analysis and expert validation workflows.

**Domain**: NLP, Topic Modeling, Sentiment Analysis, Social Media Analytics  
**Primary Language**: Python  
**UI Framework**: Streamlit  
**Main Entry Point**: `streamlit_app_improved.py` (~1350 lines)

---

## 🚀 Quick Start

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app_improved.py

# For evaluation tasks
python evaluate.py [stance|topics] <ground_truth_file>
```

**Dataset Format Required**:
- CSV file with columns: `full_text`, `created_at`, `full_text_comments`
- Optional: `expert_stance` column for evaluation (POSITIVE, NEGATIVE, NEUTRAL)

---

## 🏛️ Architecture & Code Structure

For comprehensive technical details, see [ARCHITECTURE.md](../ARCHITECTURE.md).

### Section Organization (`streamlit_app_improved.py`)

The main app follows a modular structure with clear sections:

1. **PAGE CONFIG & INITIALIZATION** (Lines 1-69)
   - Streamlit page config, custom CSS, logging setup
   - Global styling and theme configuration

2. **LOTTIE ANIMATIONS** (Lines 70-115)
   - Animation loading utilities
   - Animation URLs constants for UI feedback

3. **HEADER & TITLE** (Lines 116-132)
   - Professional header with branding
   - Multi-column layouts for spacing

4. **HELPER FUNCTIONS** (Lines 133-450)
   - Model loading (cached with `@st.cache_resource`)
   - Topic modeling functions
   - Stance analysis functions
   - Text preprocessing utilities
   - File conversion (CSV/HTML)

5. **MAIN APP LOGIC** (Lines 451+)
   - File upload & data preview
   - Mode selection (Analysis vs. Expert Validation)
   - Data preparation pipeline
   - Model loading with visual feedback
   - Preprocessing pipeline
   - Topic modeling with `st.status()` progress tracking
   - Results visualization
   - Stance analysis with progress tracking
   - Results export & persistence

### Data Flow

```
User Upload CSV → Preview Data → Load ML Models (cached)
├─ Preprocess Texts (posts & comments)
├─ Topic Modeling (Embedding → Clustering → Topic Extraction → Topics Over Time)
├─ Visualize Topic Results
├─ Stance Analysis (Sentiment Classification → Confidence Scoring)
├─ Display Metrics & Results
└─ Export Files → Expert Validation Ready
```

---

## 💡 Key Development Conventions

### Caching Strategy
- **Heavy models**: Use `@st.cache_resource` for models that shouldn't be re-instantiated
- **Data**: Use `@st.cache_data` for expensive computations (animations via Lottie)
- **Example**:
  ```python
  @st.cache_resource
  def load_embedding_model():
      return SentenceTransformer('distiluse-base-multilingual-cased-v2')
  
  @st.cache_data
  def load_lottie_url(url: str):
      return requests.get(url).json()
  ```

### Progress Tracking
- Use `st.status()` contexts for multi-step workflows:
  ```python
  with st.status("Processing...", expanded=True) as status:
      st.write("Step 1...")
      # ... work ...
      st.write("Step 2...")
      status.update(label="✅ Complete", state="complete")
  ```
- Provide real-time progress updates for long-running tasks
- Display clear step-by-step feedback in the UI

### Error Handling
- Wrap external API calls and model loading with try-except
- Provide graceful fallbacks (e.g., skip Lottie animations if network fails)
- Log errors for debugging: `logging.error("message")`
- Show user-friendly error messages via `st.error()`

### Text Processing Pipeline
1. **Lowercase & strip whitespace**
2. **Remove URLs, mentions, hashtags**
3. **Remove punctuation** (except where semantically important)
4. **Tokenization & lemmatization** (Indonesian-specific)
5. **Stop word removal**

See [PREPROCESSING_DOCUMENTATION.md](../PREPROCESSING_DOCUMENTATION.md) for details.

### Documentation Standards
- **Docstrings**: Provide for all functions explaining purpose, params, returns
- **Inline comments**: Explain complex logic and design decisions
- **Section headers**: Use clear comments to denote major code sections
- **Example**:
  ```python
  def preprocess_indonesian_text(text: str) -> str:
      """
      Preprocess Indonesian text with language-specific rules.
      
      Args:
          text: Raw Indonesian text
          
      Returns:
          Cleaned and normalized text
      """
      # Strip whitespace and lowercase
      text = text.strip().lower()
      # ... implementation ...
      return text
  ```

---

## 📊 Workflow Modes

The app supports two main modes selectable via sidebar:

### Mode 1: 🔍 Analisis (Analysis)
- Default workflow for running ML analysis
- Handles data upload, preprocessing, topic modeling, sentiment analysis
- Produces visualization and metrics
- Exports results with timestamps

### Mode 2: 🧑‍💼 Validasi Ahli Diplomasi (Expert Validation)
- Framework for domain experts to validate ML predictions
- Supports rating, feedback collection, metrics tracking
- See [VALIDATION_INTERFACE_GUIDE.md](../VALIDATION_INTERFACE_GUIDE.md) for implementation

---

## 🧪 Testing & Validation

### Pre-Deployment Checklist
- [ ] File upload works with sample CSVs
- [ ] Models load correctly (check internet for Lottie animations)
- [ ] Preprocessing completes without errors
- [ ] Topic modeling runs successfully
- [ ] Stance analysis completes
- [ ] All metrics display correctly
- [ ] Download buttons work for CSV/HTML/TXT
- [ ] Session state persists correctly
- [ ] Progress bars and animations display
- [ ] No console errors or warnings

### Evaluation Commands
```bash
# Evaluate stance classification against ground truth
python evaluate.py stance ground_truth_samples.csv --output stance_results.json

# Evaluate topic modeling against ground truth
python evaluate.py topics ground_truth_samples.csv --output topics_results.json
```

See [GROUND_TRUTH_SAMPLES.md](../GROUND_TRUTH_SAMPLES.md) for sample format.

---

## 📚 Documentation Reference

Link to relevant docs (don't duplicate content):

- **[QUICK_START.md](../QUICK_START.md)** - User-friendly setup guide
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Technical code structure details
- **[UI_IMPROVEMENTS.md](../UI_IMPROVEMENTS.md)** - Feature documentation
- **[ENHANCEMENT_SUMMARY.md](../ENHANCEMENT_SUMMARY.md)** - Before/after comparison
- **[PREPROCESSING_DOCUMENTATION.md](../PREPROCESSING_DOCUMENTATION.md)** - Text cleaning details
- **[VALIDATION_INTERFACE_GUIDE.md](../VALIDATION_INTERFACE_GUIDE.md)** - Expert validation workflow
- **[GROUND_TRUTH_SAMPLES.md](../GROUND_TRUTH_SAMPLES.md)** - Sample data format
- **[EVALUATION_DOCUMENTATION.md](../EVALUATION_DOCUMENTATION.md)** - Metrics & evaluation methods
- **[BAB_5_IMPLEMENTATION.md](../BAB_5_IMPLEMENTATION.md)** - System implementation details
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history

---

## 🛠️ Common Development Tasks

### Adding a New ML Model
1. Add model loading function with `@st.cache_resource`
2. Add preprocessing if language-specific
3. Integrate into main app logic using `st.status()` for progress
4. Add metrics/evaluation capability
5. Document in relevant BAB chapter

### Extending Visualization
1. Use Plotly for interactive charts (see existing code)
2. Add Streamlit metric cards for KPIs
3. Include download functionality for generated visualizations
4. Reference [ARCHITECTURE.md#Results Visualization](../ARCHITECTURE.md)

### Adding Export Formats
1. Implement converter function (e.g., `convert_df_to_xlsx()`)
2. Add download button in results section
3. Test with sample data
4. Document in UI_IMPROVEMENTS.md

### Improving Performance
- Use aggressive caching with `@st.cache_resource` for heavy computations
- Batch process large datasets
- Profile with `st.write(st.session_state)` to identify bottlenecks
- See [ARCHITECTURE.md#Performance](../ARCHITECTURE.md) for patterns

---

## 📦 Dependencies Overview

Key packages and versions (see [requirements.txt](../requirements.txt)):

- **streamlit** - Web UI framework
- **bertopic** - Topic modeling algorithm
- **sentence-transformers** - Text embeddings
- **transformers** - BERT models (IndoBERT for Indonesian)
- **torch** - Deep learning backend
- **pandas/numpy** - Data processing
- **plotly** - Interactive visualizations
- **scikit-learn** - ML metrics & utilities
- **streamlit-lottie** - Loading animations

---

## ⚠️ Common Pitfalls & Solutions

### Issue: Model Loading Hangs
- **Cause**: Large model downloads on first run, missing internet
- **Solution**: Ensure stable internet, test with `cache_resource`, add timeout handlers

### Issue: Lottie Animations Not Displaying
- **Cause**: Network connectivity, URL issues
- **Solution**: Already handled with graceful fallback in code, check internet

### Issue: Memory Issues with Large Datasets
- **Cause**: Caching all results in session state
- **Solution**: Implement batch processing, clear cache selectively, see [DEVELOPMENT_LOG.md](../DEVELOPMENT_LOG.md)

### Issue: Indonesian Text Not Preprocessing Well
- **Cause**: Language-specific rules not applied
- **Solution**: Ensure proper lemmatization with IndoBERT tokenizer, check [PREPROCESSING_DOCUMENTATION.md](../PREPROCESSING_DOCUMENTATION.md)

---

## 🔮 Future Enhancement Points

- Multi-language support (beyond Indonesian)
- Real-time streaming data ingestion
- Advanced visualization dashboards (Dash/Power BI)
- API endpoint for model serving
- Mobile-responsive design enhancements
- Database persistence layer for results

See [ARCHITECTURE.md#Extension Points](../ARCHITECTURE.md) for implementation guidance.

---

## 📝 Code Review Guidelines

When reviewing changes:
- ✅ Docstrings provided for all functions
- ✅ Error handling with try-except blocks
- ✅ Uses appropriate caching decorators
- ✅ Progress feedback for long-running tasks
- ✅ Indonesian text properly handled
- ✅ Results exported with timestamps
- ✅ No duplicate logic (DRY principle)
- ✅ Follows section organization pattern
- ✅ Documentation updated accordingly

---

## 📞 Getting Help

1. **Setup Issues?** → Check [QUICK_START.md](../QUICK_START.md)
2. **Understanding Code?** → Read [ARCHITECTURE.md](../ARCHITECTURE.md)
3. **How to Extend?** → Review existing patterns in [ARCHITECTURE.md#Extension Points](../ARCHITECTURE.md)
4. **Debug Problems?** → Check [DEVELOPMENT_LOG.md](../DEVELOPMENT_LOG.md) and error logs
5. **Evaluate Models?** → Run `python evaluate.py [stance|topics] <ground_truth.csv>`

---

**Last Updated**: April 29, 2026  
**Status**: ✅ Production Ready  
**Maintainer Notes**: See [CHANGELOG.md](../CHANGELOG.md) and [VERIFICATION_RECORD.md](../VERIFICATION_RECORD.md)
