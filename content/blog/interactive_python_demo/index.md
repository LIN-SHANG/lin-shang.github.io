---
title: "如果不只是展示代码：Run Python in My Hugo blog."
date: 2025-12-17

authors:
  - me
python: true
type: docs
# image:
#   caption: "Image credit: [HugoBlox](https://hugoblox.com)"
#   focal_point: Center
#   placement: 1
content_meta:
  trending: true

# cover:
#   image: cover.png  # Auto-detected from cover image in this folder
#   icon:
#     name: "📔"

tags: ["Hugo", "Python", "PyScript", "WebAssembly", "Tutorial"]
categories: ["Tech Engineering"]
summary: "静态网站也能跑 Python？本文详细记录了如何利用 PyScript 和 WebAssembly 技术，在 Hugo 学术博客中从零打造一个支持代码高亮、实时运行、变量监控甚至绘图功能的 'Mini Jupyter Notebook'。"
---

## 背景：为什么我们需要“活”的代码？

作为一名计算机科学/AI方向的研究者，我们在撰写技术博客时，常常需要展示算法逻辑或数据处理流程。传统的 Hugo 博客通过 Markdown 的代码块（Code Block）展示代码，虽然美观，但它是**死**的。

读者无法修改参数来验证想法，无法查看中间变量的状态，更无法直观地看到绘图结果。

**如果能在博客里直接嵌入一个类似 Jupyter Notebook 的可交互环境，岂不美哉？**

起初我认为这需要部署一个后端服务（如 JupyterHub），直到我发现了 **PyScript** 和 **WebAssembly (WASM)**。这意味着我们可以在**纯静态**的网页（如 GitHub Pages）中，利用**浏览器**的算力来运行 Python，无需任何服务器成本。

本文将复盘我从原型到最终实现的完整踩坑历程，并提供一套开箱即用的解决方案。

---

## 核心技术栈

*   **Hugo (Extended)**: 静态网站生成器。
*   **PyScript (Pyodide)**: 基于 WASM 的浏览器端 Python 运行时。
*   CodeJar + PrismJS: 关键组件。CodeJar 处理编辑行为（如 Tab 缩进、光标管理），PrismJS 负责语法高亮。
*   **Micropip**: 浏览器端的 Python 包管理器（用于安装 Numpy 等）。

---

## 避坑指南：由“死”到“活”的四个难点

在直接给出代码之前，我想先分享开发过程中遇到的几个“史诗级”大坑，这能帮你理解为什么代码要写成最终那个样子。

### 1. 浏览器的“安全锁” (COOP/COEP)
**现象**：Python 环境根本无法启动，控制台报错 `SharedArrayBuffer is not defined`。

**原因**：为了防止幽灵熔断（Spectre）攻击，现代浏览器默认禁用了高精度计时和共享内存，除非服务器发送特定的安全响应头。

**解决**：GitHub Pages 无法配置服务器头。我们必须使用 `coi-serviceworker.js` 脚本，在前端通过 Service Worker 欺骗浏览器，开启隔离环境。

### 2. HTML 压缩导致的“缩进消失术”
**现象**：本地运行正常，推送到 GitHub 后，Python 代码的所有缩进全没了，导致 `IndentationError`。

**原因**：GitHub Actions 构建时使用了 `hugo --minify`。HTML 压缩器认为 `<div>` 里的空格是多余的，直接删除了。

**解决**：**Base64 传输法**。在 Hugo 模板层将代码转为 Base64 字符串，传给前端后再用 JS 解码。HTML 压缩器看不懂 Base64，自然不敢乱动。

### 3. 编辑体验：contentEditable vs 高亮
**现象**：普通的 textarea 没有高亮；使用 div contenteditable 虽然可以渲染 HTML 标签来高亮，但每次输入会导致光标乱跳。

**解决**：引入 CodeJar。这是一个仅 2KB 的微型库，它接管了 contenteditable 元素的光标和输入事件，完美配合 PrismJS 实现实时高亮。

### 4. 无法加载第三方库
**现象**：`import numpy` 报错。

**原因**：浏览器里没有预装这些库。

**解决**：在 PyScript 启动配置中预声明 `packages`，并使用 `micropip` 进行动态加载。

---

## 手把手教程：复刻同款 Mini IDE

请按照以下目录结构创建或修改你的 Hugo 项目文件。

### 第一步：配置 Service Worker (static)

创建文件 `static/js/coi-serviceworker.js`。

下载地址：[coi-serviceworker GitHub](https://github.com/gzuidhof/coi-serviceworker/blob/master/coi-serviceworker.js)*(将该文件内容完整复制进去即可)*


### 第二步：注入依赖库 (Head Hooks)

我们需要在页面头部引入 PyScript、PrismJS（高亮）和 Service Worker。
创建或修改 `layouts/_partials/hooks/head-end/custom_style.html`：

{{< details "点击展开查看 custom_style.html.html 完整代码" >}}
```txt
直接查看 https://github.com/LIN-SHANG/lin-shang.github.io/tree/main/layouts/_partials/hooks/head-end/custom_style.html
```
{{< /details >}}

### 第三步：打造 Shortcode 组件 (核心)

这是集大成者。它实现了：

- Base64 传输：防止 Hugo 压缩破坏代码格式。
- CodeJar 集成：提供 IDE 般的编辑体验。
- 变量监控树：右侧实时显示 Python 变量结构。
- Matplotlib 绘图与导出：支持画图并一键复制为 PNG。
- Ctrl+Enter 运行选中代码。


创建文件 `layouts/shortcodes/py-ide.html`
{{< details "点击展开查看 py-ide.html 完整代码" >}}
```txt
直接查看 https://github.com/LIN-SHANG/lin-shang.github.io/tree/main/layouts/shortcodes/py-ide.html
```
{{< /details >}}

### 第四步：部署配置 (deploy.yml)

最后，也是最容易被忽视的一步。为了让 Hugo 正确编译上述代码，GitHub Actions 必须使用 **Extended** 版本。

修改 `.github/workflows/deploy.yml`：
```yaml
'''
前面的很多代码
'''
- name: Setup Hugo
      uses: peaceiris/actions-hugo@v3
      with:
        hugo-version: '0.152.2' # 建议固定一个较新版本,不建议低于 0.148
        extended: true          # <--- 必须开启！
        
'''
后面的很多代码
'''
```
## 效果展示与使用

**功能亮点：**
1. **逐行运行**：选中某一行，按 Ctrl + Enter，仅运行选中部分。
2. **变量探查**：右侧会自动解析当前的变量，字典和列表可以折叠展开。
3. **绘图支持**：调用 show_plot() 即可显示 Matplotlib 图像。
4. **状态保持**：变量在多次运行之间是共享的，无需重复定义。

{{< py-ide >}}
```python
# 💡 小技巧：动态安装第三方库 😎
# 只需要 # install: package_1, package_2 
# install: pandas
import numpy as np 
import matplotlib.pyplot as plt 

# 1. 定义数据
x = np.linspace(0, 10, 100) 
y = np.sin(x) 
y2 = np.cos(x)

# 2. 绘制图像
plt.figure(figsize=(6, 4))
plt.plot(x, y, label='Sin', color='#4CAF50')
plt.plot(x, y2, label='Cos', color='#FFC107', linestyle='--')
plt.title("Interactive Plot in Hugo") 
plt.legend()
plt.grid(True, alpha=0.3)

# 3. 显示图像
show_plot() 

# 4. 这里的变量 x 和 y 会自动显示在右侧变量树中
```
{{< /py-ide >}}

## 结语

通过这次折腾，我们将一个“只读”的 Hugo 博客变成了一个“可交互”的教学平台。虽然 PyScript 的初始化速度（约 1-2 秒）仍有待提升，但对于 Numpy、Pandas 和基础算法教学，这已经是一个堪称完美的轻量级方案。

P.S. 记得给浏览器一点时间下载 Python 内核，看到 "System Ready" 后再点击运行。