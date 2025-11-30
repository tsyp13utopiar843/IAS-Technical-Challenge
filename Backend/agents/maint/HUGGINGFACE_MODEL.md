# PM Agent - Hugging Face Model Integration

## Overview

The PM (Predictive Maintenance) Agent now supports loading models from **Hugging Face Hub**, eliminating the need for local model files in the repository.

## Setup

### 1. Upload Your Model to Hugging Face

First, upload your trained model artifacts to a Hugging Face repository:

```python
from huggingface_hub import HfApi

api = HfApi()

# Upload your model files
api.upload_file(
    path_or_fileobj="path/to/model.pkl",
    path_in_repo="model.pkl",
    repo_id="your-username/pm-agent-model",
    repo_type="model"
)

api.upload_file(
    path_or_fileobj="path/to/scaler.pkl",
    path_in_repo="scaler.pkl",
    repo_id="your-username/pm-agent-model",
    repo_type="model"
)

# Optional: label encoder
api.upload_file(
    path_or_fileobj="path/to/label_encoder.pkl",
    path_in_repo="label_encoder.pkl",
    repo_id="your-username/pm-agent-model",
    repo_type="model"
)
```

### 2. Configure the Agent

#### Option A: Environment Variable (Recommended)

Set the `HF_MODEL_REPO` environment variable:

```bash
# Linux/Mac
export HF_MODEL_REPO=your-username/pm-agent-model

# Windows PowerShell
$env:HF_MODEL_REPO="your-username/pm-agent-model"

# Docker/Railway
HF_MODEL_REPO=your-username/pm-agent-model
```

#### Option B: Configuration File

Edit `Backend/agents/config/pm_agent.json`:

```json
{
  "agent": {
    "id": "pm_agent"
  },
  "model": {
    "path": "hf://your-username/pm-agent-model",
    "sequence_length": 60,
    "num_features": 6
  }
}
```

### 3. Install Dependencies

```bash
pip install huggingface_hub==0.19.4
```

## How It Works

1. **Priority Loading**:
   - First tries to load from Hugging Face Hub (if `HF_MODEL_REPO` is set or path starts with `hf://`)
   - Falls back to local pickle files
   - Falls back to mock predictions if neither available

2. **Caching**:
   - Models downloaded from HF are cached in `./.hf_cache/`
   - Subsequent runs use the cached version (no re-download)

3. **Required Files in HF Repository**:
   - `model.pkl` - Trained Random Forest/LSTM model
   - `scaler.pkl` - StandardScaler for feature normalization
   - `label_encoder.pkl` (optional) - Label encoder

## Example Hugging Face Repository Structure

```
your-username/pm-agent-model/
├── model.pkl            # Trained model
├── scaler.pkl           # Feature scaler
├── label_encoder.pkl    # Optional label encoder
└── README.md            # Model documentation
```

## Usage

### Local Development

```bash
# Set environment variable
export HF_MODEL_REPO=your-username/pm-agent-model

# Start the agent
cd Backend/agents/maint
python main.py
```

### Docker

Add to `docker-compose.yml`:

```yaml
pm-agent:
  environment:
    - HF_MODEL_REPO=your-username/pm-agent-model
```

### Railway Production

Set environment variable in Railway dashboard:
```
HF_MODEL_REPO = your-username/pm-agent-model
```

## Authentication (Private Models)

For private Hugging Face models:

```bash
# Login to Hugging Face
huggingface-cli login

# Or set token as environment variable
export HUGGING_FACE_HUB_TOKEN=your_token_here
```

## Benefits

✅ **No local model files** - Models stored in HF, not in Git  
✅ **Version control** - HF maintains model versions  
✅ **Easy updates** - Update model on HF, restart agent  
✅ **Collaboration** - Share models across team via HF  
✅ **Automatic fallback** - Works offline with local files  

## Example Public Models

You can use these example models for testing:

- `huggingface/model-name` - Example predictive maintenance model
- Create your own at [huggingface.co](https://huggingface.co/new)

## Troubleshooting

### Model not loading from HF
- Check `HF_MODEL_REPO` environment variable is set
- Verify repository exists and is public (or you're authenticated)
- Check logs for specific error messages

### Cache issues
- Clear cache: `rm -rf ./.hf_cache`
- Model will re-download on next run

### Missing huggingface_hub
```bash
pip install huggingface_hub
```

## Migration from Local Models

No changes needed! The agent automatically falls back to local files if HF loading fails.

To migrate:
1. Upload your existing `artifacts/model.pkl` and `artifacts/scaler.pkl` to HF
2. Set `HF_MODEL_REPO` environment variable
3. Restart the agent

The local `artifacts/` folder is now optional and can be removed from the repository.
