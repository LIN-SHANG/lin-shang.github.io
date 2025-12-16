---
title: CS336 lecture-01 - tokenizer
linktitle: Section-01_lecture-01
summary: 基于 CS336 课程讲义，深入探讨了大模型中的分词（Tokenization）技术。从最朴素的字符级、字节级分词，一直讲解到现代 LLM 标配的 BPE（Byte Pair Encoding）算法及其实现。
date: 2025-12-16
python: true
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

> **致谢**：本单元内容的灵感来源于 Andrej Karpathy 关于 Tokenization 的[视频](https://www.youtube.com/watch?v=zduSFxRajkE)，强烈推荐观看。

在语言模型中，**Tokenizer（分词器）** 扮演着“翻译官”的角色，负责在 **字符串（Strings）** 和 **Token 序列（Indices）** 之间进行转换。 语言模型本质上是对 Token 序列（通常由整数索引表示）的概率分布进行建模。 
例如： 
- 输入字符串：`"Hello, 🌍! 你好!"` 
- Token 序列：`[15496, 11, 995, 0]` 

我们需要一个过程将字符串编码（Encode）为 Token，也需要一个过程将 Token 解码（Decode）回字符串。虽然将文本视为 Unicode 字符序列或字节序列在理论上是可行的，但在实际应用中，基于 **BPE（字节对编码）** 的方法是目前最高效的启发式算法。

以下我们将逐步演进，从最简单的分词方法直到 BPE。

## 1. 基础分词方法的尝试与局限 
为了直观感受分词器的工作原理，我们可以先定义一个抽象基类，并尝试几种朴素的实现。 

```python
from abc import ABC, abstractmethod 
class Tokenizer(ABC): 
	@abstractmethod 
	def encode(self, string: str) -> list[int]: 
		pass 
		
	@abstractmethod 
	def decode(self, indices: list[int]) -> str: 
		pass


class BPETokenizerParams:
	"""All you need to specify a BPETokenizer."""
	vocab: dict[int, bytes] # index -> bytes
	merges: dict[tuple[int, int], int] # index1, index2 -> new_index
```

### 1.1 字符级分词 (Character-based Tokenization)
Unicode 字符串本质上是字符的序列。我们可以直接利用`ord()` 将字符转换为码点（整数），用 `chr()` 转回字符。

```python
class CharacterTokenizer(Tokenizer):
    """将字符串表示为 Unicode 码点序列"""
    def encode(self, string: str) -> list[int]:
        return list(map(ord, string))

    def decode(self, indices: list[int]) -> str:
        return "".join(map(chr, indices))

# 测试
# string = "Hello, 🌍! 你好!"
# ord("a") == 97, ord("🌍") == 127757
```

**局限性：**
1. **词表过大**：Unicode 字符集大约有 **1百万**个字符，这意味着模型的词汇表（Vocabulary Size）非常庞大。
2. **效率低下**：许多字符（如 🌍）非常罕见，占据了词表空间却很少被学习到，这是对资源的浪费。

### 1.2 字节级分词 (Byte-based Tokenization)
为了解决词表过大的问题，我们可以将 Unicode 字符串视为字节序列（UTF-8 编码）。每个字节由 0 到 255 之间的整数表示。

```python
class ByteTokenizer(Tokenizer):
    """将字符串表示为字节序列"""
    def encode(self, string: str) -> list[int]:
        string_bytes = string.encode("utf-8")
        indices = list(map(int, string_bytes))
        return indices

    def decode(self, indices: list[int]) -> str:
        string_bytes = bytes(indices)
        string = string_bytes.decode("utf-8")
        return string

# 测试
# bytes("a", encoding="utf-8") == b"a"
# bytes("🌍", encoding="utf-8") == b"\xf0\x9f\x8c\x8d" (4个字节)
```
**局限性：**  
虽然词表大小完美地控制在 256，但**压缩率（Compression Ratio）** 极差。
- `Compression Ratio = Bytes / Tokens`在这里，比率为 1。
- 这意味着序列会变得非常长。由于 Transformer 的注意力机制计算复杂度是序列长度的平方级，过长的序列会导致推理极其缓慢且上下文窗口被浪费。

> [!NOTE]**ASCII，Unicode，UTF-8 到底是什么？** ---> 这篇[ blog ](https://www.ruanyifeng.com/blog/2007/10/ascii_unicode_and_utf-8.html)值得深入学习!


### 1.3 词级分词 (Word-based Tokenization)

这是传统 NLP 中常用的方法，使用正则表达式按空格或标点切分。

```python
import regex

# GPT-2 使用的正则模式示例
GPT2_TOKENIZER_REGEX = r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

def word_tokenizer_demo(string):
    # 简单的正则切分
    segments = regex.findall(r"\w+|.", string)
    return segments
```

**局限性：**

1. 词汇量依然巨大（甚至比 Unicode 字符还多）。
2. **UNK 问题**：训练中未见过的词（Out of Vocabulary）会被标记为 \<UNK\>，这会破坏信息的完整性并影响困惑度（Perplexity）的计算。

## 2. 最佳实践： [Byte Pair Encoding](https://en.wikipedia.org/wiki/Byte-pair_encoding) (BPE)
BPE(字节对编码)最初由 Philip Gage 在 1994 年作为[数据压缩算法](http://www.pennelynn.com/Documents/CUJ/HTML/94HTML/19940045.HTM)提出，后被[神经机器翻译](https://arxiv.org/abs/1508.07909)工作引入 NLP 领域（在那之前，基于词的 tokenizer 方法是主流），并被 [GPT-2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) 等现代大模型广泛采用。

### 2.1 核心思想
BPE的 基础想法：在一个原始文本上训练一个分词器来确定一个词表。
BPE 的核心直觉是：常见字符序列用单个 Token 表示，罕见序列用多个Token 表示。它是“字符级”和“词级”的折中方案。

GPT-2的论文使用基于词的分词方法将文本拆分为初始片段，并在每个片段上运行原始的BPE算法。

> [!TIP] **BPE 算法流程草图**
>
> 1. **初始化**：从字节级 Token 开始（初始词表大小为 256）。
> 2. **统计频率**：遍历语料，统计所有相邻 Token 对的出现频率。
> 3. **寻找最频对**：找到出现频率最高的一对（例如 `(e, s)`）。
> 4. **合并与更新**：将这对 Token 合并为一个新的 Token（例如 `es`，分配新索引 256），并更新词表。
> 5. **迭代**：重复上述步骤 2-4，直到达到预设的合并次数或目标词表大小。

### 2.2 训练一个 tokenizer

```python
string = "the cat in the hat"
params = train_bpe(string, num_merges=3)

def train_bpe(string: str, num_merges: int) -> BPETokenizerParams:
	"""
	这里是一个简单的训练 bpe 的代码原型
	按照之前的设想，我们应该维护好下面三个变量：
	1. indices 所有原始文档的 utf-8 字节编码
	2. merges 记录每次遍历时的相邻 token 共现计数器
	3. 初始 vocab ，所有的词表拓展都从 256 个字节编码开始。
	   
	"""
	indices = list(map(int, string.encode("utf-8")))
	merges: dict[tuple[int, int], int] = {} # 对关联 index 进行合并 index1,index2 => merged index
	vocab: dict[int, bytes] =  {x: bytes([x]) for x in range(256)} # index -> bytes
	
	for i in range(num_merges):
		# 统计每对 tokens 的出现次数
		counts = defaultdict(int)
		for index1, index2 in zip(indices, indices[1:]): # 抽取每一个相邻 pair
			counts[(index1, index2)] += 1
			
		# 找到出现次数最多的 pair
		pair = max(counts, key=counts.get)
		index1, index2 = pair
		
		# 融合 Pair ，新增 Token
		new_index = 256 + i
		merges[pair] = new_index
		vocab[new_index] = vocab[index1] + vocab[index2]
		indices = merge(indices, pair, new_index)
		
	return BPETokenizerParams(vocab=vocab, merges=merges)
	
def merge(indice: list[int], pair: tuple[int, int], new_index: int) -> list[int]:
	"""返回`indices`，但将所有`pair`实例替换为`new_index`"""
	# 初始化一个新的 indice 来完成对现有 indice 的更新
	new_indices = []
	i = 0
	# 
	while i < len(indices):
		if i + 1 < len(indices) and indices[i] == pair[0] and indices[i+1] == pair[1]:
			new_indices.append(new_index)
			i += 2
		else:
			new_indices.append(indices[i])
			i += 1
	return new_indices
		
```

### 2.3 使用tokenizer

```python
# 推理阶段
tokenizer = BPETokenizer(params)
test_string = "the quick brown fox"

# 编码与解码
indices = tokenizer.encode(test_string)
reconstructed_string = tokenizer.decode(indices)

assert test_string == reconstructed_string
print(f"原始字符串: {test_string}")
print(f"Token ID: {indices}")


```


### 2.4 可交互 python 环境
{{< py-ide >}}
```python
# 这是一个可编辑的 Python 环境
from collections import defaultdict

class BPETokenizerParams:
    """All you need to specify a BPETokenizer."""
    def __init__(self, vocab, merges):
        self.vocab = vocab
        self.merges = merges

# 辅助函数 merge 需要先定义，或者是放在类外面
def merge(indices: list[int], pair: tuple[int, int], new_index: int) -> list[int]:
    new_indices = []
    i = 0
    while i < len(indices):
        # 检查是否匹配 pair
        if i + 1 < len(indices) and indices[i] == pair[0] and indices[i+1] == pair[1]:
            new_indices.append(new_index)
            i += 2
        else:
            new_indices.append(indices[i])
            i += 1
    return new_indices

def train_bpe(string: str, num_merges: int) -> BPETokenizerParams:
    # 将字符串转为 UTF-8 字节整数列表
    indices = list(map(int, string.encode("utf-8")))
    merges = {} 
    vocab = {x: bytes([x]) for x in range(256)}
    
    for i in range(num_merges):
        # 统计每对 tokens 的出现次数
        counts = defaultdict(int)
        
        # 【错误修正 1】这里之前写成了 indice[1:]，应该是 indices[1:]
        for index1, index2 in zip(indices, indices[1:]): 
            counts[(index1, index2)] += 1
            
        if not counts:
            break
            
        # 找到出现次数最多的 pair
        pair = max(counts, key=counts.get)
        index1, index2 = pair
        
        # 融合 Pair ，新增 Token
        # 【错误修正 2】这里之前定义了 new_pair，但后面用的是 new_index
        new_index = 256 + i
        
        merges[pair] = new_index
        vocab[new_index] = vocab[index1] + vocab[index2]
        
        # 调用 merge 更新 indices
        indices = merge(indices, pair, new_index)
        
    return BPETokenizerParams(vocab=vocab, merges=merges)

# 测试运行
string = "the cat in the hat"
params = train_bpe(string, num_merges=3)

print("Training complete!")
print("Merges:", params.merges)
print("Vocab size:", len(params.vocab))

```
{{< /py-ide >}}


## 总结

分词是一种“必要的恶（Necessary Evil）”。虽然理想情况下我们希望模型能直接理解原始字节，但 BPE 是目前平衡词表大小、序列长度和信息密度的最有效手段。

在实际的大模型训练（如 GPT-2/3/4）中，BPE 的实现会更加复杂，包括：

1. **预分词（Pre-tokenization）**：先用正则将文本切分为单词块，再在块内进行 BPE，防止跨单词合并。
2. **特殊 Token**：处理 <|endoftext|> 等控制符。
3. **性能优化**：编码过程需要极度优化，不能像上述代码那样遍历所有合并规则。