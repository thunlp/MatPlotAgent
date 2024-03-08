# nohup bash models/scripts/deepseek-coder-6.7b-instruct.sh > models/logs/deepseek-coder-6.7b-instruct_`date +%Y%m%d_%T`.log 2>&1 &
export CUDA_VISIBLE_DEVICES=6
python -m vllm.entrypoints.openai.api_server \
    --model /data/groups/QY_LLM_Other/OSS_Code_LLM/deepseek-coder-6.7b-instruct \
    --port=8001