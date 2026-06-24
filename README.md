# ChronoGene 39F Full Agent + UI

这是一个全新整理过的单一项目包，已兼容 Python 3.9.6，并且包含：

- 39 岁女性 synthetic fake data
- Agent 后端代码
- CLI 命令
- Streamlit UI
- 报告生成
- 成分机制匹配 demo
- 12 周复测 loop demo

默认目标用户：

```text
subject_id: CG0039
age: 39
sex: female
BMI: 21.8
```

人物设定：

```text
早期光氧化 / 氧化应激压力
节律-压力-恢复轴负担
屏障韧性不足 / 干燥敏感倾向
轻中度慢性炎症
糖化与口腔微生态炎症轴不是主导问题
```

> Synthetic demo only. Not for clinical use.

---

## 一、VS Code 运行方式

### 1. 打开项目

在 VS Code 中打开这个文件夹：

```text
chronogene_39F_full_agent_ui
```

### 2. 打开 Terminal

菜单：

```text
Terminal → New Terminal
```

确认在项目根目录：

```bash
ls
```

你应该看到：

```text
app.py
requirements.txt
pyproject.toml
src
data
models
reports
```

### 3. 创建虚拟环境

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

如果你的电脑要用 `python3`：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

---

## 二、先跑 Agent 后端

### 1. 验证数据

```bash
python -m chronogene_agent.cli validate --data-dir data
```

### 2. 训练 baseline model

```bash
python -m chronogene_agent.cli train \
  --data-dir data \
  --model-path models/baseline_model.joblib
```

### 3. 生成 39 岁女性报告

用 demo ground truth 生成：

```bash
python -m chronogene_agent.cli report \
  --data-dir data \
  --subject-id CG0039 \
  --out reports/CG0039_report.md \
  --json-out reports/CG0039_report.json \
  --use-target
```

或用模型预测生成：

```bash
python -m chronogene_agent.cli report \
  --data-dir data \
  --model-path models/baseline_model.joblib \
  --subject-id CG0039 \
  --out reports/CG0039_model_report.md \
  --json-out reports/CG0039_model_report.json
```

---

## 三、启动 UI

```bash
streamlit run app.py
```

如果提示 `streamlit: command not found`，用：

```bash
python -m streamlit run app.py
```

启动后浏览器会打开：

```text
http://localhost:8501
```

左侧默认：

```text
Data folder: data
Subject: CG0039
Score source: Use target scores (demo ground truth)
```

先不要改，直接看页面即可。

---

## 四、你应该看到什么

UI 里有 5 个页面：

```text
Overview
Evidence Chain
Ingredient Matching
12-Week Loop
Agent Chat
```

CG0039 的主导机制应该大致是：

```text
氧化/光氧化压力
节律-压力-恢复轴
屏障韧性不足
慢性炎症 / SASP
```

---

## 五、常见问题

### 1. `No module named chronogene_agent`

运行：

```bash
pip install -e .
```

### 2. `streamlit: command not found`

运行：

```bash
python -m streamlit run app.py
```

### 3. 页面没显示 CG0039

确认左侧：

```text
Data folder = data
Subject = CG0039
```

### 4. 想重新开始

直接删掉 `.venv`，重新执行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
streamlit run app.py
```


---

## Python 3.9.6 兼容说明

这个版本已经把 `requires-python` 改为 `>=3.9`，并添加了 `setup.py`，所以老版本 pip 也可以执行：

```bash
pip install -e .
```

如果你只想先跑 UI，也可以不执行 editable install，直接：

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
