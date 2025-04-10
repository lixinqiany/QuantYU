# 安装Anaconda后，创建专用的量化交易环境
conda create -n quant python=3.11
conda activate quant

# 安装必要的库
conda install jupyter notebook pandas numpy matplotlib seaborn scikit-learn
conda install -c conda-forge yfinance backtrader statsmodels
pip install akshare

# 启动Jupyter Notebook
jupyter notebook

# 公开quant环境的kernel
pip install ipykernel
python -m ipykernel install --user --name=quant --display-name "quant"
# 验证
jupyter kernelspec list