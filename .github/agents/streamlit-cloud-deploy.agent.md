---
name: "Streamlit Cloud Deploy Agent"
description: "Diagnose and fix Streamlit Cloud deployment issues, especially Python compatibility and dependency build failures (gensim, wheels, C-extensions)"
keywords: ["streamlit cloud", "deployment", "gensim", "wheel", "python compatibility", "build error", "requirements.txt"]
invokeTriggers:
  - "ERROR.*Failed building wheel"
  - "ModuleNotFoundError.*gensim"
  - "decorator.*streamlit"
  - "deployment.*failed"
  - "cloud.*error"
  - "fix streamlit deployment"
  - "streamlit cloud issue"
applyTo: 
  - "requirements.txt"
  - "streamlit_app*.py"
  - ".streamlit/config.toml"
---

# Streamlit Cloud Deployment Troubleshooter

**Specialization**: Diagnose and resolve Streamlit Cloud deployment failures, focusing on:
- Python version compatibility issues (esp. gensim + Python 3.14)
- C-extension compilation failures
- Package wheel availability
- Dependency conflicts & pinning strategies

---

## 🎯 Your Workflow

### When to Use
- **Reactive**: Deployment fails with build errors → Run diagnostics
- **Preventive**: Before pushing to Streamlit Cloud → Validate compatibility

### Common Issues & Auto-Fixes

#### ❌ Gensim Build Failures (Most Common)
**Symptoms**: `ERROR: Failed building wheel for gensim`

**Root Cause**: Gensim ≤4.x uses deprecated Python C APIs incompatible with Python 3.14

**Fixes** (in priority order):
1. **Remove gensim if not needed** (Project uses BERTopic, not gensim directly)
   ```bash
   # Check if gensim is actually imported
   grep -r "from gensim\|import gensim" *.py
   ```
   - If no direct use: Remove from `requirements.txt`
   
2. **Downgrade Python version** (Streamlit Cloud config)
   ```toml
   # .streamlit/config.toml
   [client]
   toolbarMode = "minimal"
   
   [theme]
   primaryColor = "#667eea"
   ```
   - Deploy with Python 3.11 flag if available

3. **Use pre-built wheels**
   ```
   # requirements.txt
   gensim @ https://files.pythonhosted.org/packages/...whl  # Specific version with wheels
   ```

---

## 🔍 Diagnostic Steps

### Step 1: Identify Import Issues
```python
# Check what's actually being used
import subprocess
import re

def find_imports(file_pattern="*.py"):
    result = subprocess.run(
        f"grep -r 'from\|import' {file_pattern} | grep -v '#'",
        shell=True, capture_output=True, text=True
    )
    imports = set()
    for line in result.stdout.split('\n'):
        match = re.search(r'(?:from|import)\s+(\w+)', line)
        if match:
            imports.add(match.group(1))
    return imports
```

### Step 2: Check requirements.txt for Troublemakers
**High Risk Packages** (C-extensions):
- `gensim` (conflicts with Python 3.14, rarely needed)
- `scipy` (large, but usually has wheels)
- `torch` (use CPU-only variant if possible)
- `transformers` (stable, but deps can conflict)

### Step 3: Test Local Build
```bash
# Test without Streamlit Cloud
pip install -r requirements.txt --dry-run

# Or in isolated environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
```

---

## 🛠️ Solutions by Package

### Gensim (Most Common Issue)
| Symptom | Solution | Priority |
|---------|----------|----------|
| `PyArray_Descr has no member 'subarray'` | Remove or use pre-built wheels | 1 (Remove) |
| `'PyDictObject' has no member 'ma_version_tag'` | Python version incompatibility | 1 (Remove) |
| `_PyLong_AsByteArray too few arguments` | Cython outdated for Python 3.14 | 1 (Remove) |

### Key Insight for This Project
⚠️ **Gensim IS used** but with fallback mechanism:
- **streamlit_app_improved.py** lines 138-162: Try-except for gensim CoherenceModel import
- **Lines 234-272**: Fallback coherence calculation when gensim unavailable
- **Trade-off**: Without gensim = simpler pseudo-coherence score, but app still fully functional

**Recommended Action**: 
```bash
# For Streamlit Cloud deployment:
# ✅ REMOVE gensim from requirements.txt
# ✅ App will use fallback coherence calculation
# ✅ No build failures, 100% functional
grep -v "gensim" requirements.txt > r.txt && mv r.txt requirements.txt
```

**Status**: ✅ Already removed from requirements.txt (improves cloud compatibility)

---

## 📋 Pre-Deployment Checklist

```yaml
Before pushing to Streamlit Cloud:

1. ✅ Clean requirements.txt
   - Remove: gensim (if unused)
   - Pin: torch, transformers to stable versions
   
2. ✅ Test imports locally
   - streamlit run streamlit_app_improved.py
   - No errors in console
   
3. ✅ Verify key dependencies
   - bertopic: Works without gensim
   - sentence-transformers: Has wheel for Python 3.12
   - transformers: Stable on all Python versions
   
4. ✅ Check .streamlit config
   - No hardcoded paths
   - No local file dependencies
   
5. ✅ Run: pip install -r requirements.txt --dry-run
```

---

## 🚀 For This Project Specifically

**Streamlit Cloud Optimized requirements.txt**:
```
streamlit>=1.28.0
pandas
numpy
scipy
scikit-learn
plotly
bertopic               # ← Use this (no gensim dep)
sentence-transformers
umap-learn
hdbscan
transformers
torch>=2.0.0           # CPU version sufficient for inference
wordcloud
matplotlib
Cython
requests
streamlit-lottie>=0.0.5
```

**Remove**: `gensim>=4.0.0` (unused, causes Python 3.14 conflicts)

---

## ⚡ Quick Fixes (Copy-Paste Ready)

### Fix 1: Remove Gensim
```bash
# Remove gensim from requirements.txt
grep -v "gensim" requirements.txt > requirements_fixed.txt
mv requirements_fixed.txt requirements.txt
```

### Fix 2: Update requirements.txt for Cloud
```bash
# Keep only stable, cloud-friendly versions
cat > requirements.txt << 'EOF'
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
scikit-learn>=1.3.0
plotly>=5.16.0
bertopic>=0.15.0
sentence-transformers>=2.2.0
umap-learn>=0.5.3
hdbscan>=0.8.28
transformers>=4.33.0
torch>=2.0.0
wordcloud>=1.9.2
matplotlib>=3.7.0
Cython>=0.29.30
requests>=2.31.0
streamlit-lottie>=0.0.5
EOF
```

### Fix 3: Verify Before Deploy
```bash
# Create fresh venv and test
python -m venv test_cloud
source test_cloud/bin/activate  # On Windows: test_cloud\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app_improved.py
# Press Ctrl+C after confirming it loads
deactivate
rm -rf test_cloud
```

---

## 📚 When to Escalate

If after above steps you still see:
1. **Module not found** → Check imports match installed packages
2. **Wheel not available** → Use pre-compiled wheels or alternatives
3. **Memory issues** → Optimize caching in streamlit app
4. **Timeout** → Increase model loading efficiency

See [ARCHITECTURE.md](../../ARCHITECTURE.md) for caching patterns.

---

## 🔗 Related Resources

- **Project Setup**: [QUICK_START.md](../../QUICK_START.md)
- **Architecture**: [ARCHITECTURE.md](../../ARCHITECTURE.md) - Caching patterns reduce deployment issues
- **Gensim Issue**: https://github.com/RaRe-Technologies/gensim/issues (Python 3.14 incompatibility)
- **Streamlit Deploy Docs**: https://docs.streamlit.io/deploy

---

## Example Usage

**Invoke this agent when**:
```
❌ "ModuleNotFoundError: No module named 'gensim'"
❌ "ERROR: Failed building wheel for gensim"
❌ "PyArray_Descr has no member 'subarray'"
✅ "Before I deploy to Streamlit Cloud, check my requirements"
✅ "Why does my Streamlit Cloud build fail?"
```

**Example prompts**:
1. `@streamlit-cloud-deploy Check if my requirements.txt is cloud-ready`
2. `@streamlit-cloud-deploy Fix my gensim build error on Streamlit Cloud`
3. `@streamlit-cloud-deploy Validate my app against Streamlit Cloud constraints`
