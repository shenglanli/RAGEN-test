#!/bin/bash

# Quick Start Script for RAGEN WebShop Training
# This script provides an easy way to start training on WebShop

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[RAGEN-WebShop] ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] ${1}${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] ${1}${NC}"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --verify-only       Only verify setup without training"
    echo "  --dataset [small|full]  Choose dataset (default: small)"
    echo "  --lora              Use LoRA for parameter-efficient training"
    echo "  --eval              Run evaluation instead of training"
    echo "  --model MODEL       Specify model path (default: Qwen/Qwen2.5-3B-Instruct)"
    echo "  -h, --help          Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Start training with default settings"
    echo "  $0 --verify-only    # Only verify the setup"
    echo "  $0 --lora           # Train with LoRA"
    echo "  $0 --dataset full   # Train on full dataset"
    echo "  $0 --eval           # Run evaluation"
    exit 1
}

# Parse command line arguments
VERIFY_ONLY=false
DATASET="small"
USE_LORA=false
RUN_EVAL=false
MODEL_PATH="Qwen/Qwen2.5-3B-Instruct"

while [[ $# -gt 0 ]]; do
    case $1 in
        --verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --lora)
            USE_LORA=true
            shift
            ;;
        --eval)
            RUN_EVAL=true
            shift
            ;;
        --model)
            MODEL_PATH="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Step 1: Verify conda environment
print_step "Checking conda environment..."
if ! conda env list | grep -q "ragen"; then
    print_error "RAGEN conda environment not found!"
    echo "Please run: bash scripts/setup_ragen.sh"
    exit 1
fi
print_success "RAGEN environment found"

# Step 2: Activate environment
print_step "Activating RAGEN environment..."
eval "$(conda shell.bash hook)"
conda activate ragen

# Step 3: Verify WebShop installation
print_step "Verifying WebShop installation..."
if ! python -c "from webshop_minimal import WebAgentTextEnv" 2>/dev/null; then
    print_error "WebShop not installed!"
    echo "Please run: bash scripts/setup_webshop.sh"
    exit 1
fi
print_success "WebShop installed correctly"

# Step 4: Verify data
print_step "Checking WebShop data..."
if [ ! -d "external/webshop-minimal/webshop_minimal/data/$DATASET" ]; then
    print_error "WebShop $DATASET dataset not found!"
    echo "Please run: bash scripts/setup_webshop.sh"
    exit 1
fi
print_success "WebShop $DATASET dataset found"

# Step 5: Quick environment test
print_step "Testing WebShop environment..."
python -c "
from webshop_minimal import WebAgentTextEnv, init_basedir
init_basedir('$DATASET')
env = WebAgentTextEnv()
obs = env.reset(session=0)
print('Environment test successful!')
print(f'Initial observation length: {len(obs)} characters')
" || {
    print_error "Environment test failed!"
    exit 1
}
print_success "Environment test passed"

if [ "$VERIFY_ONLY" = true ]; then
    print_success "Setup verification complete! Everything looks good."
    echo ""
    echo "To start training, run:"
    echo "  bash scripts/quick_start_webshop.sh"
    exit 0
fi

# Step 6: Display configuration
echo ""
echo "=========================================="
echo "RAGEN WebShop Training Configuration"
echo "=========================================="
echo "Model: $MODEL_PATH"
echo "Dataset: $DATASET"
echo "LoRA: $([ "$USE_LORA" = true ] && echo "Enabled" || echo "Disabled")"
echo "Mode: $([ "$RUN_EVAL" = true ] && echo "Evaluation" || echo "Training")"
echo "=========================================="
echo ""

# Step 7: Run training or evaluation
if [ "$RUN_EVAL" = true ]; then
    print_step "Starting evaluation..."
    python -m ragen.llm_agent.agent_proxy --config-name _6_webshop \
        model_path="$MODEL_PATH"
else
    print_step "Starting training..."

    if [ "$USE_LORA" = true ]; then
        print_step "Training with LoRA..."
        python train.py --config-name base-lora \
            model_path="$MODEL_PATH" \
            es_manager.train.env_configs.tags=[WebShop] \
            es_manager.val.env_configs.tags=[WebShop] \
            agent_proxy.max_turn=9 \
            actor_rollout_ref.rollout.max_model_len=15000
    else
        python train.py --config-name _6_webshop \
            model_path="$MODEL_PATH"
    fi
fi

print_success "Done!"
