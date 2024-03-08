# 第三方模型使用

# 安装依赖

1. Conda 环境（py3.10）【环境安装（python3.10 cuda11.8）】

```
conda create -n myenv python=3.10 -y
conda activate myenv
```

2. Install vLLM with CUDA 11.8.

```
<!-- pip install https://github.com/vllm-project/vllm/releases/download/v0.2.2/vllm-0.2.2+cu118-cp310-cp310-manylinux1_x86_64.whl -->

pip install https://github.com/vllm-project/vllm/releases/download/v0.2.7/vllm-0.2.7+cu118-cp310-cp310-manylinux1_x86_64.whl
```


3. 安装torch CUDA118

```
pip uninstall torch -y
pip install torch --upgrade --index-url https://download.pytorch.org/whl/cu118
```

4. 可能会报错xform版本不一致,检查xformers的版本与cuda是否一致。如果不一致，使用下面命令下载cuda118对应的xformers

```
pip3 install -U xformers --index-url https://download.pytorch.org/whl/cu118
```

5. 安装accelerate

```
pip install accelerate 
```