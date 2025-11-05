# RAGEN WebShop - Quick Start Guide

This is a quick reference guide for reproducing RAGEN experiments on the WebShop environment.

## TL;DR - Fastest Way to Start

```bash
# 1. Setup (one-time)
bash scripts/setup_ragen.sh          # Base RAGEN setup
bash scripts/setup_webshop.sh         # WebShop-specific setup

# 2. Verify setup
bash scripts/quick_start_webshop.sh --verify-only

# 3. Start training
bash scripts/quick_start_webshop.sh

# Or manually:
python train.py --config-name _6_webshop
```

## What's Included

This repository now includes several resources to help you reproduce RAGEN on WebShop:

### Documentation
- **`WEBSHOP_REPRODUCTION_GUIDE.md`** - Comprehensive guide with all details
  - Environment setup instructions
  - Training configuration explanations
  - Evaluation procedures
  - Troubleshooting tips

### Scripts
- **`scripts/setup_webshop.sh`** - Automated WebShop environment setup
- **`scripts/quick_start_webshop.sh`** - Quick start script with multiple options
- **`scripts/test_webshop_env.py`** - Test suite to verify your setup

### Examples
- **`examples/webshop_example.py`** - Interactive example showing how to use the WebShop environment

## Quick Start Options

### Option 1: Basic Training (Small Dataset)
```bash
bash scripts/quick_start_webshop.sh
```

### Option 2: Training with LoRA (Memory Efficient)
```bash
bash scripts/quick_start_webshop.sh --lora
```

### Option 3: Training on Full Dataset
```bash
bash scripts/quick_start_webshop.sh --dataset full
```

### Option 4: Evaluation Mode
```bash
bash scripts/quick_start_webshop.sh --eval --model /path/to/checkpoint
```

### Option 5: Manual Training
```bash
conda activate ragen
python train.py --config-name _6_webshop
```

## Directory Structure

```
RAGEN/
├── config/
│   ├── _6_webshop.yaml          # WebShop training config
│   └── envs.yaml                # Environment definitions
├── scripts/
│   ├── setup_webshop.sh         # Setup script
│   ├── quick_start_webshop.sh   # Quick start script
│   └── test_webshop_env.py      # Test suite
├── examples/
│   └── webshop_example.py       # Usage example
├── ragen/
│   └── env/
│       └── webshop/
│           ├── env.py           # WebShop environment
│           └── config.py        # Environment config
├── external/
│   └── webshop-minimal/         # WebShop backend
│       └── webshop_minimal/
│           └── data/            # WebShop datasets
│               ├── small/       # Small dataset
│               └── full/        # Full dataset
├── WEBSHOP_REPRODUCTION_GUIDE.md  # Detailed documentation
└── WEBSHOP_QUICKSTART.md         # This file
```

## Testing Your Setup

Run the test suite to verify everything is working:

```bash
python scripts/test_webshop_env.py
```

This will:
1. Check if WebShop modules can be imported
2. Verify data availability
3. Test environment creation and reset
4. Test taking actions
5. Verify RAGEN integration

All tests should pass before starting training.

## Running the Example

To see how the environment works:

```bash
python examples/webshop_example.py
```

This demonstrates:
- Creating a WebShop environment
- Resetting and getting initial observations
- Taking actions and receiving rewards
- A complete interaction loop

## Key Configuration Files

### `config/_6_webshop.yaml`
Main configuration for WebShop training:
- Model: `Qwen/Qwen2.5-3B-Instruct`
- Max turns: 9 actions per episode
- Context length: 15000 tokens
- Batch sizes and optimization parameters

### `config/envs.yaml`
Environment definition under `WebShop:`:
- Action limits
- Instruction templates
- Dataset selection (small/full)
- Environment-specific config

## Common Commands

### Verify Setup
```bash
bash scripts/quick_start_webshop.sh --verify-only
```

### Train with Default Settings
```bash
python train.py --config-name _6_webshop
```

### Train with Custom Model
```bash
python train.py --config-name _6_webshop \
  model_path=Qwen/Qwen2.5-7B-Instruct
```

### Train with Lower Memory
```bash
python train.py --config-name _6_webshop \
  micro_batch_size_per_gpu=1 \
  ppo_mini_batch_size=8 \
  actor_rollout_ref.rollout.max_model_len=8000
```

### Evaluate a Checkpoint
```bash
python -m ragen.llm_agent.agent_proxy \
  --config-name _6_webshop \
  model_path=/path/to/checkpoint
```

## Monitoring Training

Training metrics are logged to Weights & Biases (wandb). Key metrics:
- **Reward metrics**: Average episode rewards
- **Success rate**: Purchase completion rate
- **val/generations**: Actual agent trajectories (view in wandb dashboard)

## Expected Training Time

Approximate training times (will vary based on hardware):
- **A100 80GB**: ~4-6 hours for 1000 iterations
- **RTX 4090**: ~6-10 hours (with reduced batch sizes)
- **With LoRA**: ~30% faster

## Troubleshooting

### "webshop_minimal not found"
```bash
bash scripts/setup_webshop.sh
```

### "Data directory not found"
```bash
python scripts/download_data.py
```

### "Java not found"
```bash
sudo apt update && sudo apt install default-jdk
```

### CUDA Out of Memory
Use smaller batch sizes or LoRA:
```bash
bash scripts/quick_start_webshop.sh --lora
```

Or manually adjust:
```bash
python train.py --config-name _6_webshop \
  micro_batch_size_per_gpu=1 \
  ppo_mini_batch_size=8
```

## Getting Help

1. Check the detailed guide: `WEBSHOP_REPRODUCTION_GUIDE.md`
2. Run the test suite: `python scripts/test_webshop_env.py`
3. Try the example: `python examples/webshop_example.py`
4. Check [RAGEN Documentation](https://ragen-doc.readthedocs.io/)
5. Open an issue on [GitHub](https://github.com/RAGEN-AI/RAGEN/issues)

## Next Steps

After successful training:
1. Monitor training in wandb dashboard
2. Evaluate trained model on test set
3. Analyze generated trajectories
4. Experiment with different hyperparameters
5. Try larger models or full dataset

## Quick Reference - Environment Details

- **Task**: Interactive shopping agent
- **Action Space**: Text commands (search, click)
- **Observation Space**: Text (HTML rendered as text)
- **Episode Length**: Up to 9 actions
- **Reward**: Based on purchase match score
- **Dataset Sizes**:
  - Small: ~100 products (fast iteration)
  - Full: ~10,000 products (full evaluation)

## Resources

- [RAGEN Paper](https://arxiv.org/abs/2504.20073)
- [RAGEN Documentation](https://ragen-doc.readthedocs.io/)
- [WebShop Paper](https://arxiv.org/abs/2207.01206)
- [Original WebShop Repository](https://github.com/princeton-nlp/WebShop)

---

**For detailed information, see `WEBSHOP_REPRODUCTION_GUIDE.md`**
