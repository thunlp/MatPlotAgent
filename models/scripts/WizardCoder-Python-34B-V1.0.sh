# nohup bash models/scripts/WizardCoder-Python-34B-V1.0.sh > models/logs/WizardCoder-Python-34B-V1.0_`date +%Y%m%d_%T`.log 2>&1 &
CUDA_VISIBLE_DEVICES=1,0,5 python -m vllm.entrypoints.openai.api_server \
    --model /data/groups/QY_LLM_Other/OSS_Code_LLM/WizardCoder-Python-34B-V1.0 \
    --port=8005 \
    --gpu-memory-utilization=1 \
    --max-model-len=16380 \
    --enforce-eager \