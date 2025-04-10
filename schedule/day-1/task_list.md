1. conda environment 创建
```json
{
    name: quant,
    python: 3.11
}
```
2. dependency 安装
```json
{
    installed: [jupyter, notebook, pandas, numpy, seaborn, yfinance],
    not_installed: [backtrader, statsmodels],
    quant_related: [yfinance]
}
```
3. 验证开发环境可用性
```json
{
    notebooks: [env_test.ipynb]
}
```