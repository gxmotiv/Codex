#!/usr/bin/env bash
set -euo pipefail
MODEL="${1:-llama3}"
ollama pull "$MODEL"
echo "Pulled $MODEL for local KP interpretation."
