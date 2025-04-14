### 环境搭建

```bash
# 1. 创建conda环境（需提前安装Anaconda3）
conda create -n quant python=3.10 -y
conda activate futquantures

# 2. 安装核心依赖（特别注意版本）
pip install akshare backtrader quantstats ipywidgets 

# 3. 验证安装
python -c "import akshare as ak; print(ak.__version__)"  # 应输出1.8.95
python -c "import backtrader as bt; print(bt.__version__)"  # 应显示1.9.76.123

# 4. 安装开发工具
pip install jupyterlab ipywidgets matplotlib==3.7.0
```