### 回报分析(`bt.analyzers.returns`)

通过`addanalyzer(bt.analyzers.Returns, _name=<xxx>, tann=xxx)`将回报分析器添加到cerebro中，之后运行完根据设置的`_name`来索引其对应的`get_analysis`方法。目前发现设置了tann参数之后可以不用设置timeframe和compress。

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

### 回撤分析(`bt.analyzers.DrawDown`)
1. 回撤值（`drawdown`）
   - 两个端点：**当前资产净值**和**资产净值最高点**
   - 当前资产净值从前期净值最高点回落的百分比
2. 最大回撤值（`max.drawdown`）：
   - 所有历史回撤中最大的那一个
   - $\max_{0\to t} \frac{P_\tau - P_t}{P_t}$
   - 衡量策略在最极端情况下的抗风险能力，以及可能面临的最大亏损
3. 回撤周期（`len`）
   -  资产净值达到局部峰值开始，到净值重新超越该峰值所经历的时间长度。
   -  回撤开始到恢复前期高点的时间长度

### 夏普分析(`bt.analyzers.SharpeRatio`)
$$S = \frac{E[R-R_f]}{\sqrt{var[R]}}$$

- $R_f$：无风险收益。可以简单的理解为把钱存在银行的固定收益，无风险且保本。
- $R$：当前数据周期下的每个蜡烛线对比前一根的收益率。
- $\sqrt{var[R]}$：所有数据的收益率序列求方差
- $S = \frac{E[R-R_f]* factor}{\sqrt{var[R]}*\sqrt{factor}}$
- 无风险收益一般是年化，假设我们的数据是日线，则要将其转化到日无风险收益：$1+R_f=(1+R_{df})^{factor}$