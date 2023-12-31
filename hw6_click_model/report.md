# HW6 功能设计

## 一、背景与意义

随着在线导航（高德、百度、谷歌）、网约车（滴滴、Uber）等基于位置的服务（Location-Based Service, LBS）的迅猛发展，LBS 应用在用户的日常生活中扮演着重要的角色，帮助用户定位目的地，兴趣点（Point of Interest, POI）搜索近年来受到了越来越多的关注。为了提升用户体验，确保用户能够准确、快速地检索到目标地点，一项高效、精准的 POI 搜索是必不可少的一环。另外，通过 POI 搜索，LBS 应用可以为客户公司提供定位服务、路线规划、动态和 3D 地图等开发接口和插件，促进更多的商业机会，建立有益的合作伙伴关系，提高应用的商业竞争力。

城市化的高速发展使得 POI 搜索不仅需要能够处理实时更新的地理信息数据，确保用户获取到的信息是最新的和准确的，而且 POI 带有的附属信息越来越复杂和细化，许多具有特殊意义的地点对用户的日常生活和出行至关重要，这使得产品也需要能够适应类型更丰富、规模更大的数据。

不同用户对 POI 的定义和关注点各不相同，个性化的搜索模型可以更好地理解用户的需求，提供更符合其喜好和习惯的 LBS 服务，从而提高用户满意度。

## 二、现状分析

搜索系统除了先验的基于内容的相关性排序之外，还往往需要利用用户交互的后验信息作为补充。其中，点击模型（Click Model）是对用户点击行为的建模，描述用户在搜索过程中受到的不同因素的影响，以及这些影响之间的相互作用，最终更准确地估计用户的点击概率；点击模型既可以将输出作为特征输入到排序模型中，也可以将排序模型的输出作为输入，重新排序，是排序模型的优化手段。

POI 搜索的典型应用场景是根据用户输入，检索并返回一个 POI 列表给用户。现有的 POI 搜索主要集中在如何构建更好的检索模型，但对用户行为的研究仍然不够深入。用户行为研究是传统信息检索领域的一项重要研究课题，对 Web 搜索的搜索引擎结果页（Search Engine Result Page, SERP）的研究已经非常丰富，但在移动设备搜索乃至 POI 搜索这个细分领域，用户行为的研究还远远不够。

POI 搜索和传统搜索引擎搜索的不同之处主要有两点：首先，这是一个非常垂直的搜索领域，用户搜索意图通常是明确且特定的，而且由于 SERP 通常会同时返回地点名称和地址，用户可以直接确定搜索结果是否满足自己的需求，然后通常会点击进行下一步操作（查看路线、导航、呼叫网约车等），因此，用户的行为模式实际上比在搜索引擎上更清晰和简单；其次，大部分 POI 搜索在用户输入的同时提供即时的结果，不需要点击某个提交键，虚拟键盘的遮挡也让用户在输入中能看到的搜索结果数量减少很多，这都直接影响了用户在搜索会话中的查询重构和结果检查行为。具体地说，用户比起下滑查看当前 SERP 的更多结果，更倾向于持续在查询结尾添加信息，并只关注排名最高的几个结果。

除了导致用户行为的不同，即时搜索也给 POI 搜索中的用户数据分析带来了额外的问题，因为用户的查询重构和结果检查是混在一起的，这就需要采用和搜索引擎不同的方式识别二者的序列。

## 三、方案设计

本 POI 搜索系统以给定的历史数据作为输入，训练一个点击模型，该模型是一个概率模型，可以根据过去的观察预测用户在搜索结果列表中的点击行为，并据此对搜索结果排序。

和通用的点击模型相比，本系统结合用户在 POI 搜索中的行为模式特点，对通用点击模型进行了一定程度的简化，摒弃了一些在 POI 搜索中并不需要考虑的变量，关注了用户的结果重构行为，优化了搜索结果的排序方案。

## 四、技术路线

### 1. 用户行为

已知在 POI 搜索中的用户行为的探究中，可以得到如下几点特征：

1. 用户会从上往下地查看 SERP；
   - 用户会查看平均每个 viewport 前 67% 的结果；
2. 在看到相关的 POI 之前，用户的注意力是均匀分布的；
3. 用户查看了相关 POI 之后，就不再往下看其他结果，结束这个 session；
4. 用户很少会点击不相关的结果；
5. 比起下滑查看当前 SERP 的更多结果，用户倾向于重构 query 以查询新结果；
   - 用户倾向于重构 query 并把注意力放在 top 3 的即时结果处；
6. 用户通常会在整个 session 中持续在 query 后面添加信息。

即时搜索的问题在于 query 重构和结果检查是混在一起的，需要采用和搜索引擎不同的方法识别二者的序列。数据处理时可以采用的手段是，如果在两个连续的 queries 之间存在滑动行为，或者检查时间到达了某个限度（比如，设为用户检查无关结果的平均时间 ），就视作两个不同的 queries；反之，将第一个 query 看作第二个的一部分，只将第二个看作用户实际上提交的 query。

因此，可以总结出 POI 搜索和聚合搜索引擎搜索的几点区别：

1. 用户通常只会点击一个结果（可以假设一个 session 只发生一次点击行为）；
   1. 如果有 query 重构，那么重构之前的 query 的结果基本不会被点击。
2. 所有结果都是 vertical 的，用户不需要点击就知道这个结果是否满足需要；
3. 所有结果的展示形式都是一致的，唯一的区别是内容；
4. 用户通常会点击需要的结果（基本不存在不需要点击就可以满足用户需求的情况）。

### 2. 点击模型

一般的搜索场景是，用户在一个 session $s$ 中提交了一个 query $q$，会返回一个含有 M（通常 =10）个结果 $(d_{1},d_{2},\dots,d_{M})$ 的 SERP。M 个二元的随机变量 $(C_{1},C_{2},\dots,C_{M})$ 表示结果 $d_{i}$ 是否被点击，是则 =1，否则 =0；一个点击模型，就是对序列 $(C_{1},C_{2},\dots,C_{M})$ 的联合分布 $P(C_{1},C_{2},\dots,C_{M})$ 的概率生成模型。

首先介绍点击模型的经典检验假说（Examination Hypothesis）：用户只会在查看了结果而且被吸引的时候点击它。写成数学形式即为：
$$
C_{i}=1 \Leftrightarrow E_{i}=1 \wedge A_{i}=1
$$
其中 E 和 A 都是二元的随机隐变量，E 表示用户是否查看了结果，A 表示用户是否（只要查看了就会）被结果吸引。A 与 query $q$ 和结果 $d_{i}$ 的相似度有关：
$$
P(A_{i})=1=\alpha_{q,d_{i}}
$$
A 和 E 是相互独立的，这样，$d_{i}$ 的点击可能性就可以列出计算公式：
$$
P(C_{i}=1)=P(E_{i}=1)P(A_{i}=1)
$$
不同点击模型对 $P(E_{i})$ 的实现不一样，根据 POI 搜索的用户行为，结合级联模型（Cascade Model） 和 User Browsing Model，假设 $P(E_{i})$ 仅依赖于结果当前的位置：
$$
P(E_{i}=1)=\gamma_{i}
$$
除此之外，对 query 重构行为进行建模，引入一个新的二元隐变量 $R$，表示当前的 query 是否后续被重构，$P(R)$ 依赖于当前的和后一个 query：
$$
P(R_{q_{i}}=1)=\beta_{q_{i},q_{i+1}}
$$
更新点击行为的决定因素，加上变量 $R$，假设只有 query 没有后续重构的时候，它的结果才可能被点击：
$$
P(C_{q,i}=1)=P(E_{q,i}=1)P(A_{q,i}=1)P(R_{q}=0)
$$
对于这种带有多个隐变量的点击模型的求解，通常使用的方法除了最大似然估计之外，还要使用期望最大化算法（EM 算法）做参数估计，先随机设定初值，然后从数据中迭代计算 N 轮后，使超参数 $\alpha, \beta, \gamma$ 收敛。

学习到超参数之后，就可以用它们计算每个结果的预测分数，用来对结果排名。

### 3. 核心代码目录结构

```
config.py								—— 配置
input_reader.py					   —— 读入训练数据
click_model.py					      —— 点击模型
run.py									—— 模型测试和排序
output/									—— 训练数据输出
```

运行 `run.py` 训练和测试模型，指定训练数据文件，如：

`python run.py < click_log_sample.txt`

训练数据文件每行有 5 个元素，使用 tab 键隔开，形如：  

`1	北大	北京	["B000A816R6", "B000A7YZU9", "B0FFFHN2J7", "B000A85CAQ", "B000A7FZQ6"]	[1, 0, 0, 0, 0]`

1. session 的 id（目前只是顺序编号，后续可以使用 hashid 等）
2. query
3. 地区
4. SERP 上展示的搜索结果列表，此处使用了高德 POI 搜索 API 中每个 POI 的唯一 id
5. 用户点击列表

## 五、总结

本 POI 搜索系统旨在利用该领域的用户行为优化搜索结果的排名，因此在现有点击模型的基础上进行了一定的改造，根据用户搜索模式在历史数据中找到新的关系，进一步挖掘用户点击的特征，预期能在实际项目中发挥出比较好的结果。

## 六、参考文献

1. Pablo Sánchez et al. 2022. Point-of-Interest Recommender Systems based on Location-Based Social Networks: A Survey from an Experimental Perspective . *ACM Comput. Surv.* https://doi.org/10.1145/3510409
2. Haitian Chen et al. 2023. Behavior Modeling for Point of Interest Search. *In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’23).* https://doi.org/10.1145/3539618.3591955
3. Yukun Zheng et al. 2019. Constructing Click Model for Mobile Search with Viewport Time. *ACM Trans. Inf. Syst*. https://doi.org/10.1145/3360486