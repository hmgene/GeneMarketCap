#https://docs.vllm.ai/en/latest/getting_started/installation.html
mamba create -n vllm python=3.9 -y
mamba activate vllm
mamba install nvidia/label/cuda-12.1.0::cuda-toolkit
