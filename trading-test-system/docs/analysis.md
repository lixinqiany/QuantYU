### 回报分析(`bt.analyzers.returns`)

1. 总复合回报 $R_{tot}$(Total Compound Return) 
   - 假设每个周期的期末资金是$P_t$，起初资金是$P_{t-1}$，每周期的回报为$R_t$
   - $R_t = \frac{P_t-P_{t-1}}{P_{t-1}}=\frac{P_t}{P_{t-1}}-1$
   - 对数形式：$R_{t-log}=\ln (1+R_t)=\ln (\frac{P_t}{P_{t-1}})$
   - $R_{tot} = \prod_{i=1}(1+R_i) - 1$
   - $R_{tot-log} = \sum_{i=1}\ln(1+R_i) = \sum_{i=1}\ln (\frac{P_1}{P_0} * \frac{P_2}{P_1} ...\frac{P_T}{P_{T-1}}) = \sum_{i=1}\ln(\frac{P_T}{P_0}) $
   - $R_{tot} = \exp(R_{tot-log}) -1$
2. 平均回报 $R_{avg}$
   - $1+R_{tot} = (1+R_{avg})^{T}$
   - $R_{avg} = (1+R_{tot})^{\frac{1}{T}}$
   - 对数形式计算更加高效
   - 假设$T$个周期的总复合对数回报是$R_{tot-log}$
   - $R_{avg} = \frac{R_{tot-log}}{T} = \frac{1}{T} \sum(\ln(\frac{P_t}{P_{t-1}}))$
3. 年化回报 $R_{annualized}$
- 找到按年为周期的固定回报，使得总的复利回报相等
- $1+R_{tot} = (1+R_{annualized})^{t_{actual}}$
- $t_{actual} = \frac {T}{T_{ann}}$
- $R_{annualized} = (1+R_{tot})^{\frac{T_{ann}}{T}}$
- 对数形式
- $R_{log-annualized} = \frac{T_{ann}}{T} \sum(\ln(\frac{P_t}{P_{t-1}}))$
- 如果是日线tann参数就是252，如果是一小时线tann参数就是252*6