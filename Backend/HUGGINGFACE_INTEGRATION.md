# Hugging Face Model Integration - Quick Summary

## ✅ What Changed

The PM (Predictive Maintenance) Agent now supports loading models from **Hugging Face Hub** instead of requiring local model files in the repository.

## 🚀 How to Use

### Step 1: Upload Your Model to Hugging Face (One-time)

```bash
cd Backend/agents/maint

# Install huggingface CLI
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login

# Upload your models
python upload_to_huggingface.py --repo your-username/pm-agent-model
```

### Step 2: Configure the Agent

Set the environment variable:

```bash
# Linux/Mac
export HF_MODEL_REPO=your-username/pm-agent-model

# Windows PowerShell
$env:HF_MODEL_REPO="your-username/pm-agent-model"

# Docker (.env or docker-compose.yml)
HF_MODEL_REPO=your-username/pm-agent-model

# Railway (Dashboard → Environment Variables)
HF_MODEL_REPO=your-username/pm-agent-model
```

### Step 3: Run the Agent

```bash
python main.py
# Agent will automatically download model from HF on first run
# Subsequent runs use cached version
```

## 📁 Files Modified

1. **`Backend/agents/maint/model.py`** - Added HF Hub integration
2. **`Backend/requirements.txt`** - Added `huggingface_hub==0.19.4`
3. **`Backend/agents/maint/HUGGINGFACE_MODEL.md`** - Comprehensive guide
4. **`Backend/agents/maint/upload_to_huggingface.py`** - Helper script
5. **`Backend/.env.example`** - Environment variable examples

## 🎯 Benefits

✅ **No local model files in Git** - Models hosted on Hugging Face  
✅ **Easy model updates** - Update on HF, restart agent  
✅ **Automatic caching** - Downloaded once, cached locally  
✅ **Automatic fallback** - Still works with local files if HF fails  
✅ **Version control** - HF maintains model versions  

## 📚 Full Documentation

See **`Backend/agents/maint/HUGGINGFACE_MODEL.md`** for complete documentation including:
- Detailed setup instructions
- Authentication for private models
- Docker and Railway deployment
- Troubleshooting guide
- Migration from local models

## 🔄 Backward Compatibility

The agent still works with local models! If `HF_MODEL_REPO` is not set, it falls back to loading from `artifacts/model.pkl` and `artifacts/scaler.pkl`.

Priority:
1. Hugging Face Hub (if `HF_MODEL_REPO` set)
2. Local pickle files
3. Mock predictions

## Example Public Repository

After uploading, your HF model will be at:
```
https://huggingface.co/your-username/pm-agent-model
```

And will contain:
- `model.pkl`
- `scaler.pkl`
- `label_encoder.pkl` (optional)
- `README.md`
