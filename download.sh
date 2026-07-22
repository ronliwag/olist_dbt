# [!] Run this command to download the dataset from Kaggle. 
#     Make sure you have your Kaggle credentials set in a 
#     .env file or pass them as command line arguments.

#!/bin/bash
# chmod +x download.sh
# ./download.sh
set -e 

# Load credentials from .env file if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Store in a raw landing folder instead of seeds
OUTPUT_DIR="./data/raw"
DATASET_NAME="olistbr/brazilian-ecommerce"

mkdir -p "$OUTPUT_DIR"

# 1. Verify python3 and pip are available
if ! command -v python3 &> /dev/null; then
    echo "[$(date)] Python3 is missing. Installing..."
    sudo apt update && sudo apt install python3 python3-pip -y
fi

# 2. Check if Kaggle CLI is installed
if ! command -v kaggle &> /dev/null; then
    echo "[$(date)] Kaggle CLI not found. Installing..."
    pip3 install --quiet kaggle --break-system-packages
fi

# 3. Allow command line arguments to override credentials if passed
if [ -n "$1" ] && [ -n "$2" ]; then
    export KAGGLE_USERNAME="$1"
    export KAGGLE_KEY="$2"
fi

# 4. Download and unzip dataset
echo "[$(date)] Initiating dataset download from Kaggle ($DATASET_NAME)..."
kaggle datasets download -d "$DATASET_NAME" -p "$OUTPUT_DIR" --unzip

# 5. Validation Check
FILE_COUNT=$(ls -1 "$OUTPUT_DIR"/*.csv 2>/dev/null | wc -l)
echo "[$(date)] Ingestion complete: $FILE_COUNT CSV files extracted into $OUTPUT_DIR"