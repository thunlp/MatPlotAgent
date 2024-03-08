# nohup bash models/scripts/CodeLlama-34b-Instruct-hf.sh > models/logs/CodeLlama-34b-Instruct-hf_`date +%Y%m%d_%T`.log 2>&1 &
CUDA_VISIBLE_DEVICES=0,1 python -m vllm.entrypoints.openai.api_server \
    --model /data/groups/QY_LLM_Other/models/CodeLlama/CodeLlama-34b-Instruct-hf \
    --port=8006 \
    --gpu-memory-utilization=1 \
    --enforce-eager \
    --tensor-parallel-size 2