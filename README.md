# sql_generator
Uses offline model to generate SQL queries

## Model used
deepseek-coder-1.3b-instruct.Q3_K_M Offline model
https://huggingface.co/TheBloke/deepseek-coder-1.3B-Instruct-GGUF/tree/main

## Initial configuration

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install miniforge

xcode-select --install

### Install Python bindings for llama.cpp and Hugging Face transformers

conda create -n llama_sql_env python=3.10 -y
conda activate llama_sql_env
CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 pip install llama-cpp-python transformers

## Run script
Run the script within conda virtual environment python interpreter

