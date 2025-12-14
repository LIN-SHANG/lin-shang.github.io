---
title: Pipeline of CS336
linktitle: Pipeline of CS336
summary: 关于 Stanford CS336 章节课程安排
date: 2025-12-14
type: docs
content_meta:
  content_type: Course
  difficulty: M.S. level and upper
  prerequisites:
    - Markdown
  trending: false
menu:
  Stanford-CS-336:
    name: Overview
    weight: 1
---


# 课程组成
## 所有的一切都关乎效率
资源：数据+硬件（计算，内存，计算带宽）
给定一组受限的资源，你会如何训练一个最佳的模型？
举例：给定Common Crawl 的语料和两周 32 卡的 H100s 使用权，你将会如何行动？

课程组成大纲：
![Design decisions](design-decisions.png)

## 效率驱动着设计决策
如今，我们受限于计算资源，因此设计决策将着力于充分利用给定的硬件。
-  数据处理：避免浪费宝贵的计算资源去更新不良或无关的数据
-  分词：直接处理原始字节虽然简洁，但在当今的模型架构下计算效率低下。
-  模型架构：许多改动旨在减少内存占用或浮点运算次数（例如，共享键值缓存、滑动窗口注意力机制）
-  训练：我们只需一个 epoch 就能完成训练！
-  缩放定律：在较小的模型上使用更少的计算资源来进行超参数调优
-  对齐：如果针对特定用例对模型进行更多调优，那么所需的基础模型会更小
未来，我们将受限于数据……

## Section-1 : 基础概念 & 任务

目标：对整个工作流程有一个基本的概念认知并感知对应的课程任务设计

组成：分词，模型架构，训练

### 分词
一个分词器的抽象代码实现如下：
```
class Tokenizer(ABC):
	"""Abstract interface for a tokenizer"""
	def encode(self, string: str) -> list[int]:
		raise NotImplementedError
		
	def decode(self, indices: list[int]) -> str:
		raise NotImplementedError
```
分词器可以在strings 和 整数序列(tokens)两个相互转换。
![tokenized-example](tokenized-example.png)
直觉来看：将字符串拆分为常见片段。

本次课程将要讲授的方法是 [Byte-Pair Encoding (BPE)Tokenizer](https://arxiv.org/abs/1508.07909) , 当然目前也在一些 Tokenizer-free的方法，[Xue+ 2021](https://arxiv.org/abs/2105.13626),[Yu+ 2023](https://arxiv.org/pdf/2305.07185.pdf),[Pagnoni+ 2024](https://arxiv.org/abs/2412.09871),[Deiseroth+ 2024](https://arxiv.org/abs/2406.19223) 。直接实用 bytes 的方法看起来非常有前景，但是目前还没有被大规模应用到前沿模型。

### 架构
所有的起点：原始 Transformer [Vaswani+ 2017](https://arxiv.org/pdf/1706.03762.pdf)

![transformers](transformer-architecture.png)

### 变体：
-  激活函数（Activation functions）：ReLU, [SwiGLU](https://arxiv.org/pdf/2002.05202.pdf)
- 位置编码（Positional encodings）：Sinusoidal, [RoPE ](https://arxiv.org/pdf/2104.09864.pdf)
- 正则化（Normalization）LayerNorm [Ba+ 2016](https://arxiv.org/pdf/1607.06450.pdf)， RMSNorm [Zhang+ 2019](https://arxiv.org/abs/1910.07467)
- 正则化的替代项 : pre-norm 与 [post-norm](https://arxiv.org/pdf/2002.04745.pdf)
- 感知机（MLP）：dense，Mixture of experts [Shazeer+ 2017](https://arxiv.org/pdf/1701.06538.pdf)
- 注意力机制（Attention）：full，sliding windows，linear [Jiang+ 2023](https://arxiv.org/pdf/2310.06825.pdf)， [Katharopoulos+ 2020](https://arxiv.org/abs/2006.16236)
- 低维注意力（lower-dimensional attention）：分组查询注意力（group-query attention, aka GQA），多头潜在注意力（multi-head latent attention, aka MLA）
- 状态空间模型 （state-space model，aka SSM）

### 训练
- 优化器（Optimizer） 例如 [AdamW](https://arxiv.org/pdf/1412.6980.pdf)，[Muon](https://kellerjordan.github.io/posts/muon/)， [SOAP](https://arxiv.org/abs/2409.11321)，[Decoupled Weight Decay Regularization](https://arxiv.org/pdf/1711.05101.pdf)
- 学习率调度器（learning rate schedule），例如 [cosine](https://arxiv.org/pdf/1608.03983.pdf), [WSD](https://arxiv.org/pdf/2404.06395.pdf)
- 批大小（batch size），例如 [critical batch size](https://arxiv.org/pdf/1812.06162.pdf)
- 正则化（regularization），例如 dropout, weight decay
- 超参数设置（hyperparameters），例如注意力的头数量，隐藏层维度：用网格搜索完成探索。

### 任务1
Stanford CS336原版：[Github](https://github.com/stanford-cs336/assignment1-basics)，[PDF](https://github.com/stanford-cs336/assignment1-basics/blob/main/cs336_spring2025_assignment1_basics.pdf)
- 实现一个 BPE 分词器
- 实现 transformers，交叉熵（Cross-entropy loss），AdamW 优化器，训练循环
- 在 TinyStories 和 OpenWebText上进行训练
- 榜单：给定 90 分钟的 H100 训练时间，最小化 OpenWebText 的困厚度。[去年的榜单](https://github.com/stanford-cs336/spring2024-assignment1-basics-leaderboard)


## Section-2 系统设计 & 任务
目标：将硬件设备的性能都压榨出来

组成： 核（kernel），并行化 （parallelism），推理（inference）

### 核（ kernels）
GPU 的内部结果如下所示 ，以 A100 为例：

![A100-architech](A100-architechture.png)

类比：仓库 : 动态随机存取存储器(DRAM) :: 工厂 : 静态随机存取存储器(SRAM)

![analogy-gpu-process](analogy_gpu_process.png)

技巧：通过减少数据移动来组织计算，以最大限度地提高GPU的利用率,使用CUDA/Triton/CUTLASS/ThunderKittens编写内核程序。

### 并行度（Parallelism ）
![parallelism_framework](parallelism_framework.png)

GPU之间的数据移动甚至更慢，但“最小化数据移动”这一原则仍然适用。
使用集合操作，例如，收集（gather）、归约（reduce）、全归约（all-reduce）。
在GPU之间分片，例如，参数、激活值、梯度、优化器状态）。
如何拆分计算：{数据（data-para）、张量（tensor-para）、流水线（pipe-para）、序列（seq-para）}并行性。

### 推理 （inference）
生成令牌为模型实际使用时的必需操作；

推理对强化学习、测试时计算、评估均不可或缺；

全球范围内，推理计算（每次使用）成本已超过训练计算（一次性成本）；

推理包含预填充、解码两个阶段。如下所示：
![prefill-decode](prefill-decode.png)

预填充（类似于训练）：给定标记，可以一次性处理所有标记（计算受限）

解码：需要一次生成一个标记（内存受限）

加速解码的方法：
• 使用更轻量的模型（通过模型剪枝、量化、蒸馏）
• 推测性解码：使用更轻量的“草稿”模型生成多个标记，然后使用完整模型并行评分（精确解码！）
• 系统优化：KV缓存、批处理。

### 任务 2
Stanford CS336原版：[GitHub](https://github.com/stanford-cs336/spring2024-assignment2-systems)，[PDF](https://github.com/stanford-cs336/spring2024-assignment2-systems/blob/master/cs336_spring2024_assignment2_systems.pdf)
- 在Triton中实现融合的RMSNorm内核。
- 实现分布式数据并行训练。
- 实现优化器状态分片。
- 对实现进行基准测试和性能分析。

## Section-3 Scaling 定律 & 任务
目标：进行小规模实验，预测大规模下的超参数/损失。

问题：给定一个浮点运算次数预算（$C$），是使用更大的模型（$N$）还是在更多的标记（$D$）上训练？
Compute-optimal scaling laws: [kaplan+ 2020](https://arxiv.org/pdf/2001.08361.pdf), [Hoffmann+ 2022](https://arxiv.org/pdf/2203.15556.pdf)

![scaling_laws](chinchilla-isoflop.png)

TL;DR：$D^* = 20 N^*$（例如，14亿参数的模型应该在280亿个token上进行训练), 但这并没有考虑到推理成本！
<details>
<summary style="cursor: pointer; color: #0366d6;"><strong>👉 点击展开：为什么说它没有考虑“推理成本”？</strong></summary>

这里有一个关键的反转：Chinchilla 定律 ($D^*=20N^*$) 追求的是 **训练成本最低**（Compute-optimal）。

但在实际应用中，模型训练只有一次，而 **推理(被用户使用)** 会有无数次。
- 如果严格遵守 20倍定律，我们会得到一个参数很大、但训练数据适中的模型。虽然训练省钱，但因为它太大了，**每次运行都很贵且慢**。
- 现代模型（如 Llama 3）通常会**打破这个定律**，用远超 20 倍的数据（比如 100 倍）去“过度训练”一个小模型。这样虽然训练时多花了钱，但得到的小模型在未来使用时**速度快、成本低**。
</details>

### 任务 3
Stanford CS336 原版：[Github](https://github.com/stanford-cs336/spring2024-assignment3-scaling), [PDF](https://github.com/stanford-cs336/spring2024-assignment3-scaling/blob/master/cs336_spring2024_assignment3_scaling.pdf)
- 我们基于之前的运行定义了一个训练API（超参数→损失）
- 在FLOPs预算下提交“训练任务”并收集数据点
- 为数据点拟合缩放定律
- 提交按比例放大的超参数的预测
- 排行榜：在给定的FLOPs预算下最小化损失

## Section-4 数据 & 任务

问题：我们希望模型有什么样子的能力？多语言？代码？数学？

![data-framework](data_framework.png)


### 困惑度：语言模型的标准评估
- 标准化测试（例如，MMLU、HellaSwag、GSM8K）
- 指令遵循（例如，AlpacaEval、IFEval、WildBench）
- 缩放测试时计算：思维链、集成
- 以语言模型作为评判者：评估生成任务
- 完整系统：检索增强生成（RAG）、智能体

### 数据整理
• 数据并非凭空而来。
```
def look_at_web_data():

	urls = get_common_crawl_urls()[:3] # @inspect urls

	documents = list(read_common_crawl(urls[1], limit=300))

	random.seed(40)

	random.shuffle(documents)

	documents = markdownify_documents(documents[:10])

	write_documents(documents, "var/sample-documents.txt")
	
# urls=[
"https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-18/segments/1712296815919.75/warc/CC-MAIN-20240412101354-20240412131354-00000.warc.gz",
"https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-18/segments/1712296815919.75/warc/CC-MAIN-20240412101354-20240412131354-00001.warc.gz",
"https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-18/segments/1712296815919.75/warc/CC-MAIN-20240412101354-20240412131354-00002.warc.gz",
]

```
- 来源：从互联网爬取的网页、书籍、arXiv论文、GitHub代码等。
- 诉诸合理使用来使用版权数据进行训练？([henderson+ 2023](https://arxiv.org/pdf/2303.15715.pdf))
- 可能需要授权数据（例如，[谷歌与红迪网的数据合作](https://www.reuters.com/technology/reddit-ai-content-licensing-deal-with-google-sources-say-2024-02-22/))
- 格式：HTML、PDF、目录（而非文本！）

### 数据处理
- 转换：将HTML/PDF转换为文本（保留内容、部分结构、重写）。
- 过滤：保留高质量数据，移除有害内容（通过分类器）。
- 去重：节省计算资源，避免记忆；使用布隆过滤器或最小哈希。

### 任务4
Stanford 原版： [Github](https://github.com/stanford-cs336/spring2024-assignment4-data), [PDF](https://github.com/stanford-cs336/spring2024-assignment4-data/blob/master/cs336_spring2024_assignment4_data.pdf)
- 将通用爬虫（Common Crawl）的HTML转换为文本
- 训练分类器以过滤出高质量内容和有害内容
- 使用最小哈希进行去重
- 排行榜：在给定的令牌预算下最小化困惑度


## Section-5 对齐  &  任务
到目前为止，基础模型只是原始的潜力，非常擅长完成下一个标记。对齐能让模型真正变得有用。

对齐的目标：
- 让语言模型遵循指令。
- 调整风格（格式、长度、语气等）。
- 融入安全性（例如，拒绝回答有害问题）。
- 两个阶段：
	- supervised_finetuning(）
	- learning_from_feedback()

### 有监督微调 supervised_finetuning

指令数据格式：（prompt，response）pair
```
sft_data = list[chatExample] = [
	ChatExample(
		turns = [
			Turn(role="system", content="You are a helpful assistant."),
			Turn(role="user", content="what is 1 + 1?),
			Turn(role="assistant", content="The answer is 2."),
		],
	),
]
```
数据通常涉及人工标注。

直觉：基础模型已经具备相关技能，只需要几个例子就能展现出来。[Zhou+ 2023](https://arxiv.org/pdf/2305.11206.pdf)

监督学习：微调模型以最大化  Prob(response | prompt）。

### 从反馈中学习
现在我们有一个初步的指令遵循模型。让我们在不进行昂贵标注的情况下改进它。

反馈学习的重点是偏好数据 ，验证器，和算法。

一个偏好的数据的格式如下：

使用模型针对给定提示生成多个响应（例如，[A、B]）。用户给出偏好（例如，A < B 或 A > B）。
```
preference_data: list[PreferenceExample] = [

	PreferenceExample(

		history=[

			Turn(role="system", content="You are a helpful assistant."),

			Turn(role="user", content="What is the best way to train a language model?"),

		],

		response_a="You should use a large dataset and train for a long time.",

		response_b="You should use a small dataset and train for a short time.",

		chosen="a",

	)

]

```

####  验证器 （Verifiers）
- 形式化验证器（例如，用于代码、数学的验证器）
- 习得验证器：针对作为评判者的大语言模型进行训练

 #### 算法（Algorithm）
- Proximal Policy Optimization (PPO) from reinforcement learning [Schulman+ 2017](https://arxiv.org/pdf/1707.06347.pdf),[Ouyang+ 2022](https://arxiv.org/pdf/2203.02155.pdf)

- Direct Policy Optimization (DPO): for preference data, simpler [Rafailov+ 2023](https://arxiv.org/pdf/2305.18290.pdf)

- Group Relative Preference Optimization (GRPO): remove value function [Shao+ 2024](https://arxiv.org/pdf/2402.03300.pdf)


### 任务 5
Stanford 官方链接：[Github](https://github.com/stanford-cs336/spring2024-assignment5-alignment)，[PDF](https://github.com/stanford-cs336/spring2024-assignment5-alignment/blob/master/cs336_spring2024_assignment5_alignment.pdf)
- 实现有监督微调 
- 实现直接偏好优化（DPO）
- 实现群相对偏好优化 （GRPO）

