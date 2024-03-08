# nohup bash models/scripts/deepseek-coder-33b-instruct.sh > models/logs/deepseek-coder-33b-instruct_`date +%Y%m%d_%T`.log 2>&1 &
CUDA_VISIBLE_DEVICES=2,3 python -m vllm.entrypoints.openai.api_server \
    --model /data/groups/QY_LLM_Other/OSS_Code_LLM/deepseek-coder-33b-instruct \
    --port=8003 \
    --gpu-memory-utilization=1 \
    --max-model-len=16380 \
    --enforce-eager \