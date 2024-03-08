# nohup bash models/scripts/Magicoder-S-DS-6.7B.sh > models/logs/Magicoder-S-DS-6.7B_`date +%Y%m%d_%T`.log 2>&1 &
export CUDA_VISIBLE_DEVICES=7
python -m vllm.entrypoints.openai.api_server \
    --model /data/groups/QY_LLM_Other/OSS_Code_LLM/Magicoder-S-DS-6.7B \
    --port=8002 \
    # --chat-template /home/zhoupeng/project/LLM/agent/plotagent/benchmark/newPlotAgent/plot-agent/models/scripts/Magicoder_chat_template.jinja