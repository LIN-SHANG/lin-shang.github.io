---
# draft: true
linktitle: Stanford CS336  # 在侧边栏显示的短标题
title: Let's learn Stanford CS336 - LLM Systems!
summary: 关于 Stanford CS336 Large Language Model Systems 的系统性课程解读与笔记。
date: '2025-12-14'
# date: '2024-01-01'

# 核心配置：必须设为 docs 类型，这样才能启用侧边栏布局
tags:
  - Hugo Blox
  - Course

type: docs

content_meta:
  content_type: 'Course'
  difficulty: 'M.S. level and upper'
  prerequisites: ['Markdown']
  trending: false

# 菜单设置：定义该文档属于哪个菜单集
menu:
  Stanford-CS-336: # 这里的名字必须和下面章节中 menu 的名字一致
    name: Overview # 侧边栏最顶部的名字
    weight: 1      # 排序权重，越小越靠前
---

## 课程简介

### 前言
语言模型是现代自然语言处理（NLP）应用的基石，它开创了一种新范式，即通过单一的通用系统来处理一系列下游任务。随着人工智能（AI）、机器学习（ML）和自然语言处理领域的不断发展，深入理解语言模型对于科学家和工程师而言都变得至关重要。本课程旨在让学生全面理解语言模型，引导他们完成自主开发语言模型的全过程。借鉴操作系统课程中从零构建完整操作系统的思路，我们将带领学生了解语言模型创建的各个方面，包括预训练的数据收集与清洗、Transformer模型构建、模型训练以及部署前的评估。

所有在线信息：https://stanford-cs336.github.io/spring2025/ 
这是一门5学分的课程。==*2024年春季课程评价中的评论：整个作业的工作量大约相当于CS 224n的所有5项作业加上期末项目的总和。而这还仅仅是第一个家庭作业。*==
### 你为什么应该选这门课
- 你有强烈的欲望想了解事物的工作原理。
- 你想锻炼自己的研究工程能力。
### 你为什么不应该选这门课
- 你实际上想在这个季度完成研究工作。（去和你的导师谈谈。）
- 你有兴趣了解人工智能领域最热门的新技术（例如，多模态、RAG等）。（你应该为此选一门研讨会课程。）
- 你想在自己的应用领域取得好成果。（你应该直接提示或微调现有的模型。）
### 如何在家跟进学习
- 所有的 lecture 材料和作业都会发布在网上，所以你可以自行跟进学习。
- lecture 会通过CGOE（前身为SCPD）录制，并会在YouTube上发布（会有一定延迟）。
- 我们计划明年再次开设这门课。
### 作业
- 5项作业（基础、系统、缩放定律、数据、对齐）.
- 没有框架代码，但我们会提供单元测试和适配器接口来帮助你检查正确性。
- 先在本地实现以测试正确性，然后在集群上运行以进行基准测试（准确性和速度)。
- 部分作业设有排行榜（在给定的训练预算下最小化困惑度）。
- 人工智能工具（如CoPilot、Cursor）可能会影响学习效果，所以使用时请自行承担风险。

<!-- ## 目录 -->
<!-- Hugo 会自动生成侧边栏，这里也可以手写一些索引 -->

## 这门课程为何存在？
### 为什么我们需要这门课？

我们不妨来问问 [GPT-4 ](https://arxiv.org/pdf/2303.08774)

```
response = query_gpt4o(prompt="why teach a course on buliding language models from scratch? Answer in one sentence.")

print(responese)
```

>Teaching a course on building language models from scratch provides foundational understanding of natural language processing techniques, fosters innovation, and enables effective adaptation of models to specific tasks and domains.

目前存在的很明显的问题：AI 领域的研究者们逐渐和底层的关键技术断联。
 - 8 年前，研究者会亲自实现并训练他们自己的模型。
- 6 年前，研究者们会下载一个模型 (e.g., BERT), 并且亲自 fine-tune它。
- 现在，研究者们可能只会去提示一个强大的专有模型（往往 close-source，e.g., GPT/Claude/ Gemini/-series）。

从汇编语言到面向对象编程，从众多的小模型到一个专有的大模型，完成一个具体任务的抽象程度在逐渐变高，这确实极大的提升了生产力，但是代价是：
- 相较于编程语言或者操作系统，这些抽象是有漏洞的，不稳定的。
- 仍然有一些基础工作需要研究，而这些研究会推翻现有的技术栈。

要完成基础研究，就必须充分的理解这项技术。所以这门课的出发点是通过搭建来完成理解，除此之外还有一些小问题……

### 语言模型的工业化
![Industrialization of Language Models](language_factory.png)
- [GPT-4据称有1.8万亿个参数。](https://www.hpcwire.com/2024/03/19/the-generative-ai-future-is-now-nvidias-huang-says)
- [GPT-4的训练成本据称达到1亿美元。](https://www.wired.com/story/openai-ceo-sam-altman-the-age-of-giant-ai-models-is-already-over/)
- [xAI构建了一个包含20万个H100芯片的集群来训练Grok。](https://www.tomshardware.com/pc-components/gpus/elon-musk-is-doubling-the-worlds-largest-ai-gpu-cluster-expanding-colossus-gpu-cluster-to-200-000-soon-has-floated-300-000-in-the-past)
- [星门（OpenAI、英伟达、甲骨文）在4年内投资5000亿美元。](https://openai.com/index/announcing-the-stargate-project/)
- 此外，关于前沿模型是如何构建的，没有公开的细节。
- 出自[GPT-4的技术报告](https://arxiv.org/pdf/2303.08774.pdf)的 Section 2 ==Scope and Limitations of this Technical Report:==
> This report focuses on the capabilities, limitations, and safety properties of GPT-4. GPT-4 is aTransformer-style model [39] pre-trained to predict the next token in a document, using both publicly available data (such as internet data) and data licensed from third-party providers. The model was then fine-tuned using Reinforcement Learning from Human Feedback (RLHF) [40]. ==Given both the competitive landscape and the safety implications of large-scale models like GPT-4, this report contains no further details about the architecture (including model size), hardware, training compute dataset construction, training method, or similar.==
 We are committed to independent auditing of our technologies, and shared some initial steps and ideas in this area in the system card accompanying this release. We plan to make further technical details available to additional third parties who can advise us on how to weigh the competitive and safety considerations above against the scientific value of further transparency.

### 大就是强 （More is different）
前沿模型对我们来说确实有些遥不可及，但是构建一个 1B参数以内的小语言模型往往不能够代表的大模型的经验认知。

[示例1](https://x.com/stephenroller/status/1579993017234382849)：用于注意力机制与多层感知机（MLP）的浮点运算（FLOPs）占比会随规模变化。

![fraction of FLOPs spent in attention versus MLP changes with code](scaling_params_table.png)

示例 2: 随着模型 scaling 产生的[涌现行为](https://arxiv.org/pdf/2206.07682)趋势

![emergency of behavior with scaling](emergency_behavior.png)
### 我们可以从这门课上学习到什么可以迁移到前沿模型上的知识？
知识有三种类型：
- 机制：事物如何运作（Transformer是什么，模型并行如何利用GPU）
- 思维模式：充分发挥硬件性能，认真对待规模（缩放定律）
- 直觉：哪些数据和建模决策能产生良好的准确性

我们可以教授机制和思维模式（这些是可以迁移的）。
我们只能部分教授直觉（不一定能跨规模迁移）。

### 直觉？🤷
一些设计决策根本（尚未）没有合理依据，只是源于实验。
例子：诺姆·沙泽尔（Noam Shazeer）介绍 [SwiGLU](https://arxiv.org/pdf/2002.05202.pdf) 的论文。
> We have extended the GLU family of layers and proposed their use in Transformer. In a transfer-learning setup, the new variants seem to produce better perplexities for the de-noising objective used in pre-training as well as better results on many downstream language-understanding tasks. These architectures are simple to implement, and have no apparent computational drawbacks. ==We offer no explanation as to why these architectures seem to work: we attribute their success. as all else. to divine benevolence.==


### 苦涩的教训 (The bitter lesson)
错误解读：规模是唯一重要的，算法并不重要。
正确解读：具有可扩展性的算法才是重要的。

==准确率=效率×资源==

实际上，在更大规模下，效率要重要得多（不能浪费）。
[文章](https://arxiv.org/abs/2005.04305) 表明，2012年至2019年间，在ImageNet上的算法效率提升了44倍。
问题框架：在给定一定的计算和数据预算的情况下，人们能构建出的最佳模型是什么？
换句话说，就是要最大化效率！

## 当前格局
### 神经网络出现前（21世纪10年代前）
- 用于测量英语熵的语言模型 [香农 1950](https://www.princeton.edu/~wbialek/rome/refs/shannon_51.pdf)
- 关于n元语法语言模型的大量研究（用于机器翻译、语音识别） [Brants+ 2007](https://aclanthology.org/D07-1090.pdf)

### 神经组件（21世纪10年代）
- 首个神经语言模型 [Bengio 2003](https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf)
- 序列到序列建模（用于机器翻译） [Sutskever 2014](https://arxiv.org/pdf/1409.3215.pdf)
- Adam优化器 [Kingma 2014](https://arxiv.org/pdf/1412.6980.pdf)
- 注意力机制（用于机器翻译） [Bahdanau 2014](https://arxiv.org/pdf/1409.0473.pdf)
- Transformer架构（用于机器翻译） [Vaswani 2017](https://arxiv.org/pdf/1706.03762.pdf)
- 专家混合模型 [Shazeer 2017](https://arxiv.org/pdf/1701.06538.pdf)
- 模型并行化 [Huang 2018](https://arxiv.org/pdf/1811.06965.pdf),[Rajbhandari 2019](https://arxiv.org/abs/1910.02054),[Shoeybi 2019](https://arxiv.org/pdf/1909.08053.pdf)

### 早期基础模型（21世纪10年代末）
- ELMo：基于LSTM的预训练，微调对任务有帮助 [Peters 2018](https://arxiv.org/abs/1802.05365)
- BERT：基于Transformer的预训练，微调对任务有帮助 [Devlin 2018](https://arxiv.org/abs/1810.04805)
- 谷歌的T5（110亿参数）：将所有内容转化为文本到文本的形式 [Raffel 2019](https://arxiv.org/pdf/1910.10683.pdf)

### 迈向规模化，更封闭
- OpenAI的GPT-2（15亿参数）：文本流畅，首次出现零样本迹象，分阶段发布 [Radford 2019](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- 缩放定律：为规模化提供希望和可预测性 [Kaplan 2020](https://arxiv.org/pdf/2001.08361.pdf)
- OpenAI的GPT-3（1750亿参数）：上下文学习，封闭模型 [Brown 2020](https://arxiv.org/pdf/2005.14165.pdf)
- 谷歌的PaLM（5400亿参数）：规模庞大，训练不足 [Chowdhery 2022](https://arxiv.org/pdf/2204.02311.pdf)
- DeepMind的Chinchilla（700亿参数）：计算最优缩放定律 [Hoffmann 2022](https://arxiv.org/pdf/2203.15556.pdf)

### 开源模型
- EleutherAI的开源数据集（The Pile）和模型（GPT-J） [Gao 2020][Wang 2021](https://arxiv.org/pdf/2101.00027.pdf),[wang+ 2021](https://arankomatsuzaki.wordpress.com/2021/06/04/gpt-j/)
- 元宇宙的OPT（1750亿参数）：GPT-3的复现，存在诸多硬件问题 [Zhang 2022](https://arxiv.org/pdf/2205.01068.pdf)
- Hugging Face / BigScience的BLOOM：专注于数据来源 [Workshop 2022](https://arxiv.org/abs/2211.05100)
- 元宇宙的Llama模型 [Touvron 2023](https://arxiv.org/pdf/2302.13971.pdf),[Touvron 2023](https://arxiv.org/pdf/2307.09288.pdf)[Grattafiori 2024](https://arxiv.org/abs/2407.21783)
- 阿里巴巴的通义千问（Qwen）模型 [Qwen 2024](https://arxiv.org/abs/2412.15115)
- 深度求索（DeepSeek）的模型 [DeepSeek-AI 2024](https://arxiv.org/pdf/2401.02954.pdf), [DeepSeek-AI 2024](https://arxiv.org/abs/2405.04434),[DeepSeek-AI 2024](https://arxiv.org/pdf/2412.19437.pdf)
- AI2的OLMo 2 [Groeneveld 2024](https://arxiv.org/pdf/2402.00838.pdf),[OLMo 2024](https://arxiv.org/abs/2501.00656)

### 开放程度
- 封闭模型（例如，GPT-4o）：仅提供API访问 [OpenAI 2023](https://arxiv.org/pdf/2303.08774.pdf)
- 开源权重模型（例如，深度求索模型）：提供权重，包含架构细节的论文，部分训练细节，无数据细节 [DeepSeek-AI 2024](https://arxiv.org/pdf/2412.19437.pdf)
- 开源模型（例如，OLMo）：提供权重和数据，包含大部分细节的论文（但不一定包含原理、失败的实验） [Groeneveld 2024](https://arxiv.org/pdf/2402.00838.pdf)

### 当今的前沿模型
- [OpenAI的o3](https://openai.com/index/openai-o3-mini/) 
- Anthropic的[Claude Sonnet 3.7](https://www.anthropic.com/news/claude-3-7-sonnet) 
- xAI的[Grok3](https://x.ai/news/grok-3)
- [Google' s Gemini 2.5](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/)
- [Meta's Llama3.3](https://ai.meta.com/blog/meta-llama-3/) 
- [DeepSeek's R1](https://arxiv.org/pdf/2501.12948.pdf)
- [Alibaba's Qwen 2.5 Max](https://qwenlm.github.io/blog/qwen2.5-max/)
- [Tencent's Hunyuan-T1](https://tencent.github.io/llm.hunyuan.T1/README_EN.html)
- [Meituan's LongCat](https://github.com/meituan-longcat)

## 课程组成
### 所有的一切都关乎效率
资源：数据+硬件（计算，内存，计算带宽）
给定一组受限的资源，你会如何训练一个最佳的模型？
举例：给定Common Crawl 的语料和两周 32 卡的 H100s 使用权，你将会如何行动？

课程组成大纲：
![Design decisions](design-decisions.png)

### 效率驱动着设计决策
如今，我们受限于计算资源，因此设计决策将着力于充分利用给定的硬件。
-  数据处理：避免浪费宝贵的计算资源去更新不良或无关的数据
-  分词：直接处理原始字节虽然简洁，但在当今的模型架构下计算效率低下。
-  模型架构：许多改动旨在减少内存占用或浮点运算次数（例如，共享键值缓存、滑动窗口注意力机制）
-  训练：我们只需一个 epoch 就能完成训练！
-  缩放定律：在较小的模型上使用更少的计算资源来进行超参数调优
-  对齐：如果针对特定用例对模型进行更多调优，那么所需的基础模型会更小
未来，我们将受限于数据……

### Section-1 : 基础概念 & 任务

目标：对整个工作流程有一个基本的概念认知并感知对应的课程任务设计

组成：分词，模型架构，训练

#### 分词
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

#### 架构
所有的起点：原始 Transformer [Vaswani+ 2017](https://arxiv.org/pdf/1706.03762.pdf)

![transformers](transformer-architecture.png)

变体：
-  激活函数（Activation functions）：ReLU, [SwiGLU](https://arxiv.org/pdf/2002.05202.pdf)
- 位置编码（Positional encodings）：Sinusoidal, [RoPE ](https://arxiv.org/pdf/2104.09864.pdf)
- 正则化（Normalization）LayerNorm [Ba+ 2016](https://arxiv.org/pdf/1607.06450.pdf)， RMSNorm [Zhang+ 2019](https://arxiv.org/abs/1910.07467)
- 正则化的替代项 : pre-norm 与 [post-norm](https://arxiv.org/pdf/2002.04745.pdf)
- 感知机（MLP）：dense，Mixture of experts [Shazeer+ 2017](https://arxiv.org/pdf/1701.06538.pdf)
- 注意力机制（Attention）：full，sliding windows，linear [Jiang+ 2023](https://arxiv.org/pdf/2310.06825.pdf)， [Katharopoulos+ 2020](https://arxiv.org/abs/2006.16236)
- 低维注意力（lower-dimensional attention）：分组查询注意力（group-query attention, aka GQA），多头潜在注意力（multi-head latent attention, aka MLA）
- 状态空间模型 （state-space model，aka SSM）

#### 训练
- 优化器（Optimizer） 例如 [AdamW](https://arxiv.org/pdf/1412.6980.pdf)，[Muon](https://kellerjordan.github.io/posts/muon/)， [SOAP](https://arxiv.org/abs/2409.11321)，[Decoupled Weight Decay Regularization](https://arxiv.org/pdf/1711.05101.pdf)
- 学习率调度器（learning rate schedule），例如 [cosine](https://arxiv.org/pdf/1608.03983.pdf), [WSD](https://arxiv.org/pdf/2404.06395.pdf)
- 批大小（batch size），例如 [critical batch size](https://arxiv.org/pdf/1812.06162.pdf)
- 正则化（regularization），例如 dropout, weight decay
- 超参数设置（hyperparameters），例如注意力的头数量，隐藏层维度：用网格搜索完成探索。

#### 任务1
Stanford CS336原版：[Github](https://github.com/stanford-cs336/assignment1-basics)，[PDF](https://github.com/stanford-cs336/assignment1-basics/blob/main/cs336_spring2025_assignment1_basics.pdf)
- 实现一个 BPE 分词器
- 实现 transformers，交叉熵（Cross-entropy loss），AdamW 优化器，训练循环
- 在 TinyStories 和 OpenWebText上进行训练
- 榜单：给定 90 分钟的 H100 训练时间，最小化 OpenWebText 的困厚度。[去年的榜单](https://github.com/stanford-cs336/spring2024-assignment1-basics-leaderboard)


### Section-2 系统设计 & 任务
目标：将硬件设备的性能都压榨出来

组成： 核（kernel），并行化 （parallelism），推理（inference）

#### 核（ kernels）
GPU 的内部结果如下所示 ，以 A100 为例：

![A100-architech](A100-architechture.png)

类比：仓库 : 动态随机存取存储器(DRAM) :: 工厂 : 静态随机存取存储器(SRAM)

![analogy-gpu-process](analogy_gpu_process.png)

技巧：通过减少数据移动来组织计算，以最大限度地提高GPU的利用率,使用CUDA/Triton/CUTLASS/ThunderKittens编写内核程序。

#### 并行度（Parallelism ）
![parallelism_framework](parallelism_framework.png)

GPU之间的数据移动甚至更慢，但“最小化数据移动”这一原则仍然适用。
使用集合操作，例如，收集（gather）、归约（reduce）、全归约（all-reduce）。
在GPU之间分片，例如，参数、激活值、梯度、优化器状态）。
如何拆分计算：{数据（data-para）、张量（tensor-para）、流水线（pipe-para）、序列（seq-para）}并行性。

#### 推理 （inference）
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

#### 任务 2
Stanford CS336原版：[GitHub](https://github.com/stanford-cs336/spring2024-assignment2-systems)，[PDF](https://github.com/stanford-cs336/spring2024-assignment2-systems/blob/master/cs336_spring2024_assignment2_systems.pdf)
- 在Triton中实现融合的RMSNorm内核。
- 实现分布式数据并行训练。
- 实现优化器状态分片。
- 对实现进行基准测试和性能分析。

### Section-3 Scaling 定律 & 任务
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

#### 任务 3
Stanford CS336 原版：[Github](https://github.com/stanford-cs336/spring2024-assignment3-scaling), [PDF](https://github.com/stanford-cs336/spring2024-assignment3-scaling/blob/master/cs336_spring2024_assignment3_scaling.pdf)
- 我们基于之前的运行定义了一个训练API（超参数→损失）
- 在FLOPs预算下提交“训练任务”并收集数据点
- 为数据点拟合缩放定律
- 提交按比例放大的超参数的预测
- 排行榜：在给定的FLOPs预算下最小化损失

### Section-4 数据 & 任务

问题：我们希望模型有什么样子的能力？多语言？代码？数学？

![data-framework](data_framework.png)


#### 困惑度：语言模型的标准评估
- 标准化测试（例如，MMLU、HellaSwag、GSM8K）
- 指令遵循（例如，AlpacaEval、IFEval、WildBench）
- 缩放测试时计算：思维链、集成
- 以语言模型作为评判者：评估生成任务
- 完整系统：检索增强生成（RAG）、智能体

#### 数据整理
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

#### 数据处理
- 转换：将HTML/PDF转换为文本（保留内容、部分结构、重写）。
- 过滤：保留高质量数据，移除有害内容（通过分类器）。
- 去重：节省计算资源，避免记忆；使用布隆过滤器或最小哈希。

#### 任务4
Stanford 原版： [Github](https://github.com/stanford-cs336/spring2024-assignment4-data), [PDF](https://github.com/stanford-cs336/spring2024-assignment4-data/blob/master/cs336_spring2024_assignment4_data.pdf)
- 将通用爬虫（Common Crawl）的HTML转换为文本
- 训练分类器以过滤出高质量内容和有害内容
- 使用最小哈希进行去重
- 排行榜：在给定的令牌预算下最小化困惑度


### Section-5 对齐  &  任务
到目前为止，基础模型只是原始的潜力，非常擅长完成下一个标记。对齐能让模型真正变得有用。

对齐的目标：
- 让语言模型遵循指令。
- 调整风格（格式、长度、语气等）。
- 融入安全性（例如，拒绝回答有害问题）。
- 两个阶段：
	- supervised_finetuning(）
	- learning_from_feedback()

#### 有监督微调 supervised_finetuning

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

#### 从反馈中学习
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

 验证器 （Verifiers）
- 形式化验证器（例如，用于代码、数学的验证器）
- 习得验证器：针对作为评判者的大语言模型进行训练

 算法（Algorithm）
- Proximal Policy Optimization (PPO) from reinforcement learning [Schulman+ 2017](https://arxiv.org/pdf/1707.06347.pdf),[Ouyang+ 2022](https://arxiv.org/pdf/2203.02155.pdf)

- Direct Policy Optimization (DPO): for preference data, simpler [Rafailov+ 2023](https://arxiv.org/pdf/2305.18290.pdf)

- Group Relative Preference Optimization (GRPO): remove value function [Shao+ 2024](https://arxiv.org/pdf/2402.03300.pdf)


#### 任务 5
Stanford 官方链接：[Github](https://github.com/stanford-cs336/spring2024-assignment5-alignment)，[PDF](https://github.com/stanford-cs336/spring2024-assignment5-alignment/blob/master/cs336_spring2024_assignment5_alignment.pdf)
- 实现有监督微调 
- 实现直接偏好优化（DPO）
- 实现群相对偏好优化 （GRPO）

