---
title: "如果不只是展示代码：如何在 Hugo 静态博客中构建交互式 Python 环境"
date: 2025-12-17

python: true
type: docs

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

```html
{{ if .Params.python }}
  <!-- 1. COI Service Worker (解决环境安全限制) -->
  <script src="{{ "js/coi-serviceworker.js" | relURL }}"></script>

  <!-- 2. PyScript 核心 -->
  <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css" />
  <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>

  <!-- 3. PrismJS 高亮 (使用 jsDelivr 加速) -->
  <link href="https://fastly.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
  <script src="https://fastly.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
  <script src="https://fastly.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
{{ end }}
```

### 第三步：打造 Shortcode 组件 (核心)

这是集大成者。它实现了：

- Base64 传输：防止 Hugo 压缩破坏代码格式。
- CodeJar 集成：提供 IDE 般的编辑体验。
- 变量监控树：右侧实时显示 Python 变量结构。
- Matplotlib 绘图与导出：支持画图并一键复制为 PNG。
- Ctrl+Enter 运行选中代码。


创建文件 `layouts/shortcodes/py-ide.html`
{{< details "点击展开查看 py-ide.html 完整代码" >}}
```html
<!-- 
  PyScript IDE (Ultimate Version)
  Features: Base64 Transport, Variable Tree, Plotting, Streaming Output, Run Selection
-->

<style>
  /* === 容器样式 === */
  .py-ide-container { display: flex; flex-wrap: wrap; margin: 2rem 0; background: #1e1e1e; border-radius: 6px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #333; overflow: hidden; font-family: -apple-system, sans-serif; }
  .py-main-col { flex: 1; min-width: 300px; display: flex; flex-direction: column; border-right: 1px solid #333; }
  .py-sidebar-col { width: 260px; background: #252526; display: flex; flex-direction: column; font-size: 13px; border-left: 1px solid #333; }
  
  /* === Header === */
  .py-header { background: #333333; padding: 0 12px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #252526; height: 38px; font-size: 12px; font-weight: 600; color: #bbb; }
  .py-header-title { display: flex; align-items: center; gap: 10px; }
  .py-shortcut-hint { font-size: 10px; color: #666; font-weight: normal; border: 1px solid #444; padding: 1px 4px; border-radius: 3px;}
  .py-btn-group { display: flex; gap: 6px; }

  /* === Editor (适配 Prism + CodeJar) === */
  .py-editor { 
    min-height: 250px; padding: 15px; 
    font-family: 'Fira Code', 'Menlo', 'Consolas', monospace; 
    font-size: 14px !important; line-height: 1.5 !important; 
    background-color: #1e1e1e; color: #d4d4d4; 
    outline: none; overflow: auto; 
    caret-color: #fff; white-space: pre !important; 
  }
  /* 覆盖 Prism 默认背景 */
  pre[class*="language-"], code[class*="language-"] { text-shadow: none !important; background: transparent !important; margin: 0 !important; padding: 0 !important; border: none !important; box-shadow: none !important; }

  /* === Buttons === */
  .py-icon-btn { border: none; padding: 4px 10px; border-radius: 3px; cursor: pointer; font-size: 11px; font-weight: 600; transition: 0.2s; }
  .py-run-btn { background: #2e7d32; color: #fff; }
  .py-run-btn:hover { background: #388e3c; }
  .py-run-btn:disabled { background: #444; color: #888; cursor: wait; }
  .py-reset-btn { background: transparent; color: #aaa; border: 1px solid #444; }
  .py-reset-btn:hover { background: #444; color: #fff; }

  /* === Output & Plot === */
  .py-output { background: #1e1e1e; color: #cccccc; padding: 10px; font-family: 'Fira Code', 'Menlo', monospace; font-size: 14px; white-space: pre-wrap; border-top: 1px solid #333; max-height: 200px; overflow-y: auto; border-left: 3px solid #007acc; }
  .py-plot-container { background: white; padding: 15px; text-align: center; border-top: 1px solid #333; display: none; }
  
  /* === Variable Tree === */
  .py-tree-container { flex: 1; overflow-y: auto; padding: 8px; font-family: 'Fira Code', monospace; }
  .t-node { margin-left: 14px; line-height: 1.6; }
  .t-key { color: #9cdcfe; margin-right: 5px; cursor: pointer; }
  .t-key:hover { color: #4ec9b0; }
  .t-val { color: #ce9178; }
  .t-type { color: #569cd6; opacity: 0.7; font-size: 0.9em; margin-left: 6px; font-style: italic;}
  .t-arrow { display: inline-block; width: 10px; color: #888; cursor: pointer; transition: transform 0.1s; font-size: 10px; margin-left: -12px; margin-right: 2px;}
  .t-arrow.open { transform: rotate(90deg); }
  .t-collapsible { display: none; }
  .t-collapsible.open { display: block; }
  .t-empty { color: #666; font-style: italic; margin-left: 14px;}
</style>

{{ $rawContent := .Inner }}
{{ $cleanContent := $rawContent | replaceRE "^(?s)\\s*```[a-zA-Z0-9]*\\s+" "" }}
{{ $cleanContent := $cleanContent | replaceRE "\\s*```\\s*$" "" }}
{{ $b64Code := $cleanContent | base64Encode }}

<div class="py-ide-container">
    <div class="py-main-col">
        <div class="py-header">
            <div class="py-header-title">
                <span>TERMINAL</span>
                <span class="py-shortcut-hint">Ctrl + Enter to Run</span>
            </div>
            <div class="py-btn-group">
                <button id="reset-{{ .Ordinal }}" class="py-icon-btn py-reset-btn" py-click="reset_code_{{ .Ordinal }}">↺ RESET</button>
                <button id="btn-{{ .Ordinal }}" class="py-icon-btn py-run-btn" py-click="run_code_{{ .Ordinal }}">▶ RUN</button>
            </div>
        </div>
        
        <div id="editor-{{ .Ordinal }}" class="py-editor language-python" data-code="{{ $b64Code }}"></div>
        <div class="py-output" id="output-{{ .Ordinal }}">> Initializing Python...</div>
        
        <div id="plot-header-{{ .Ordinal }}" class="py-header" style="display: none; justify-content: flex-end; border-top: 1px solid #333;">
            <button id="copy-png-btn-{{ .Ordinal }}" class="py-icon-btn py-reset-btn">复制为 PNG</button>
        </div>
        <div class="py-plot-container" id="plot-{{ .Ordinal }}"></div>
    </div>

    <div class="py-sidebar-col">
        <div class="py-header">VARIABLES</div>
        <div id="tree-{{ .Ordinal }}" class="py-tree-container"></div>
    </div>
</div>

<script type="module">
    import { CodeJar } from 'https://cdn.jsdelivr.net/npm/codejar@3.7.0/codejar.min.js';

    document.addEventListener("DOMContentLoaded", () => {
        const editorEl = document.getElementById("editor-{{ .Ordinal }}");
        const copyBtn = document.getElementById("copy-png-btn-{{ .Ordinal }}");

        if (!editorEl) return;

        // --- 1. 初始化 CodeJar 和 Prism 高亮 ---
        const highlight = (editor) => {
            if (window.Prism) {
                editor.innerHTML = Prism.highlight(editor.textContent, Prism.languages.python, 'python');
            }
        };
        const jar = CodeJar(editorEl, highlight, { tab: '    ' });

        // --- 2. Base64 解码并填充初始代码 ---
        try {
            const rawB64 = editorEl.getAttribute("data-code");
            const decodedCode = decodeURIComponent(escape(window.atob(rawB64)));
            jar.updateCode(decodedCode);
        } catch (e) {
            console.error("Py-IDE Error:", e);
            editorEl.textContent = "# Error loading code.";
        }

        // --- 3. 快捷键绑定 ---
        editorEl.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const runBtn = document.getElementById("btn-{{ .Ordinal }}");
                if (runBtn && !runBtn.disabled) runBtn.click();
            }
        });

        // --- 4. 变量树渲染 (全局暴露) ---
        window.renderJsonTree = (containerId, jsonString) => {
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = "";
            let data;
            try { data = JSON.parse(jsonString); } catch (e) { return; }

            const createNode = (key, value, type, children) => {
                const div = document.createElement("div");
                div.className = "t-node";
                if (children !== null) {
                    const arrow = document.createElement("span");
                    arrow.className = "t-arrow";
                    arrow.innerText = "▶";
                    const label = document.createElement("span");
                    label.innerHTML = `<span class="t-key">${key}:</span><span class="t-type">${type}</span>`;
                    const childContainer = document.createElement("div");
                    childContainer.className = "t-collapsible";
                    const toggle = (e) => {
                        e.stopPropagation();
                        childContainer.classList.toggle("open");
                        arrow.classList.toggle("open");
                        arrow.innerText = arrow.classList.contains("open") ? "▼" : "▶";
                    };
                    arrow.onclick = toggle;
                    label.onclick = toggle;
                    div.appendChild(arrow); div.appendChild(label); div.appendChild(childContainer);
                    if (Object.keys(children).length === 0) {
                        childContainer.innerHTML = '<div class="t-empty">(empty)</div>';
                    } else {
                        for (const [k, v] of Object.entries(children)) childContainer.appendChild(createNode(k, v.val, v.type, v.children));
                    }
                } else {
                    div.innerHTML = `<span class="t-key" style="cursor:default">${key}:</span><span class="t-val">${value}</span>`;
                }
                return div;
            };

            if (Object.keys(data).length === 0) container.innerHTML = '<div class="t-empty" style="margin-top:10px">No user variables</div>';
            else for (const [k, v] of Object.entries(data)) container.appendChild(createNode(k, v.val, v.type, v.children));
        };

        // --- 5. 复制 SVG 为 PNG 功能 ---
        if (copyBtn) {
            copyBtn.onclick = () => {
                const plotContainer = document.getElementById("plot-{{ .Ordinal }}");
                const svgElement = plotContainer ? plotContainer.querySelector('svg') : null;
                if (!svgElement) { alert("无图可复制"); return; }
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const scale = 2; 
                const viewbox = svgElement.viewBox.baseVal;
                canvas.width = viewbox.width * scale; canvas.height = viewbox.height * scale;
                const img = new Image();
                const svgData = new XMLSerializer().serializeToString(svgElement);
                img.onload = () => {
                    ctx.fillStyle = 'white'; ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    canvas.toBlob((blob) => {
                        navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
                            .then(() => {
                                const t = copyBtn.innerText; copyBtn.innerText = "已复制!";
                                setTimeout(() => copyBtn.innerText = t, 2000);
                            });
                    });
                };
                img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgData);
            };
        }
    });
</script>

<script type="py" config='{"packages": ["micropip", "numpy", "matplotlib"]}'>
    from pyscript import window, document, HTML
    import sys, io, micropip, asyncio, html, types, json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if 'kernels' not in globals(): kernels = {}
    if {{ .Ordinal }} not in kernels: kernels[{{ .Ordinal }}] = {}

    class DOMStream:
        def __init__(self, element_id): self.element_id = element_id
        def write(self, text):
            el = document.getElementById(self.element_id)
            if el: el.innerText += text; el.scrollTop = el.scrollHeight
        def flush(self): pass

    async def init_{{ .Ordinal }}():
        document.getElementById("output-{{ .Ordinal }}").innerText = "> System Ready. 🚀\n"
    asyncio.ensure_future(init_{{ .Ordinal }}())

    def get_scope_tree(scope):
        tree_data = {}
        def safe_str(v):
            try: s = str(v)
            except: s = "<error>"
            return html.escape(s[:50] + "..." if len(s) > 50 else s)
        for k, v in scope.items():
            if k.startswith("_") or k in ['open', 'exit', 'quit', 'In', 'Out', 'get_ipython', 'show_plot', 'matplotlib', 'plt', 'micropip', 'fm', 'pyfetch', 'os']: continue
            if isinstance(v, (types.ModuleType, types.FunctionType, type)): continue
            val_type = type(v).__name__
            children = None
            if isinstance(v, dict):
                children = {}
                for sk, sv in list(v.items())[:20]: children[str(sk)] = {"val": safe_str(sv), "type": type(sv).__name__, "children": None}
            elif isinstance(v, (list, tuple)):
                children = {}
                for i, sv in enumerate(v[:20]): children[str(i)] = {"val": safe_str(sv), "type": type(sv).__name__, "children": None}
            tree_data[k] = {"val": safe_str(v) if not children else f"{val_type}[{len(v)}]", "type": val_type, "children": children}
        return json.dumps(tree_data)

    def _show_plot_helper():
        plot_div = document.getElementById("plot-{{ .Ordinal }}")
        plot_header = document.getElementById("plot-header-{{ .Ordinal }}")
        buf = io.StringIO()
        try:
            plt.savefig(buf, format='svg', bbox_inches='tight')
            plot_div.innerHTML = buf.getvalue()
            plot_div.style.display = "block"
            plot_header.style.display = "flex"
        except Exception as e: print(f"Plot Error: {e}")
        finally: plt.clf(); buf.close()

    def reset_code_{{ .Ordinal }}(event):
        kernels[{{ .Ordinal }}] = {}
        kernels[{{ .Ordinal }}]["show_plot"] = _show_plot_helper
        document.getElementById("output-{{ .Ordinal }}").innerText = "> Environment reset."
        window.renderJsonTree("tree-{{ .Ordinal }}", "{}")
        document.getElementById("plot-{{ .Ordinal }}").style.display = "none"
        document.getElementById("plot-header-{{ .Ordinal }}").style.display = "none"

    async def run_code_{{ .Ordinal }}(event):
        output_id, tree_id = "output-{{ .Ordinal }}", "tree-{{ .Ordinal }}"
        btn = document.getElementById("btn-{{ .Ordinal }}")
        output_el = document.getElementById(output_id)
        btn.disabled = True
        btn.innerText = "Running..."
        output_el.innerText = ""
        
        full_code = document.getElementById("editor-{{ .Ordinal }}").textContent
        current_scope = kernels[{{ .Ordinal }}]
        if "show_plot" not in current_scope: current_scope["show_plot"] = _show_plot_helper

        first_line = full_code.strip().split('\n')[0]
        if first_line.startswith("# install:"):
            pkgs = [p.strip() for p in first_line.replace("# install:", "").split(",") if p.strip()]
            if pkgs:
                output_el.innerText += f"> Installing: {', '.join(pkgs)}...\n"
                try: await micropip.install(pkgs)
                except Exception as e: output_el.innerText += f"Install failed: {e}\n"

        stream = DOMStream(output_id)
        sys.stdout, sys.stderr = stream, stream
        try: exec(full_code, current_scope, current_scope)
        except Exception as e: print(f"Runtime Error: {e}")
        finally:
            sys.stdout = sys.__stdout__ 
            try: window.renderJsonTree(tree_id, get_scope_tree(current_scope))
            except Exception as e: print(f"Tree Error: {e}")
            btn.disabled = False
            btn.innerText = "▶ RUN"
</script>
```
{{< /details >}}

### 第四步：部署配置 (deploy.yml)

最后，也是最容易被忽视的一步。为了让 Hugo 正确编译上述代码，GitHub Actions 必须使用 **Extended** 版本。

修改 `.github/workflows/deploy.yml`：
```yaml
- name: Setup Hugo
      uses: peaceiris/actions-hugo@v3
      with:
        hugo-version: '0.152.2' # 建议固定一个较新版本,不建议低于 0.148
        extended: true          # <--- 必须开启！
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