# nohup bash models/scripts/WizardCoder-33B-V1.1.sh > models/logs/WizardCoder-33B-V1.1_`date +%Y%m%d_%T`.log 2>&1 &
CUDA_VISIBLE_DEVICES=4,5 python -m vllm.entrypoints.openai.api_server \
    --model /data/groups/QY_LLM_Other/OSS_Code_LLM/WizardCoder-33B-V1.1 \
    --port=8004 \
    --gpu-memory-utilization=1 \
    --max-model-len=16380 \
    --enforce-eager \
    --tensor-parallel-size=2 \