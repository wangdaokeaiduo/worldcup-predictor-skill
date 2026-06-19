# 🏆 World Cup Predictor Skill (2026 世界杯全景预测引擎)

基于大语言模型、12 维度深度分析、Elo-泊松概率模型，并内嵌 **SkillOpt 自我进化机制** 的超强赛事预测 AI Skill。

## ✨ 核心特性 (Features)

1. **十二维度全景扫射**：涵盖核心球员状态、历史交锋、战术克制、门将扑救、体能与赛程密度、定位球能力、板凳深度、主客场环境等 12 项核心指标。
2. **Elo-泊松概率模型推演**：不靠拍脑门，基于真实球队 Elo 积分差值，叠加 12 维度修正系数，使用泊松分布计算精准预期进球数 (λ) 与胜平负概率。
3. **五人虚拟教练团博弈**：内置 5 位风格迥异的教练（控球派、防反派、玄学派、纯模型派、解说派），进行多视角辩论与战术推演。
4. **🧠 自我进化机制 (SkillOpt Evolution)**：独创 `evolution_ledger.py`。记录每一次预测，并在比赛结束后录入真实比分，模型会自动反思预测偏差，动态调整 12 维度的权重参数（例如：若低估了主场优势，下一次主场权重自动上调）。
5. **一键生成精美前端页面**：自带 Python 脚本，一键将枯燥的预测数据生成具备**全移动端适配**、毛玻璃 UI 和平滑动画的惊艳 HTML 报告。

### 🆕 最近更新 (Recent Updates)
- **双保险预测机制 (Dual-Score Prediction)**：抛弃单一的绝对比分输出。预测结果和生成的HTML页面现在会同时列出概率最高的**前2个比分**（如 2:1 或 2:0），极大提升了实战参考价值，完美贴合球赛的不确定性。
- **极致的移动端体验 (Perfect Mobile Responsiveness)**：深度重构了生成的 HTML 模板。全面引入 `@media` 断点适配、刘海屏 `safe-area-inset` 保护以及 `-webkit-overflow-scrolling` 触摸优化。无论在平板、大屏手机还是极窄屏设备上，赛事导航大厅和预测报告都能呈现顶级视觉效果，告别内容截断和横向滚动条！

---

## 📂 目录结构

```text
worldcup_predictor/
├── SKILL.md                 # AI 核心提示词与操作规范（Agent 直接读取）
├── prediction_ledger.json   # 引擎的“进化记忆本”（保存历史预测与动态权重）
├── scripts/
│   ├── evolution_ledger.py  # 自我进化算法引擎 (计算得分、反思、调整权重)
│   └── generate_html.py     # HTML 报告自动生成工具
├── templates/
│   └── report_template.html # 移动端适配的精美毛玻璃 HTML 模板
└── examples/
    └── usa_vs_aus_data.json # 预测结果的数据结构示例
```

---

## 🚀 快速开始 (Quick Start)

### 1. 作为 Agent Skill 使用
直接将本仓库拉取到你的 AI Agent (如 Cursor / Gemini / Cline 等) 的 `skills/` 目录下。
让 Agent 读取 `SKILL.md`，然后给它发指令：
> “请帮我预测 2026 世界杯 美国 vs 澳大利亚 的比赛。”

### 2. 生成精美 HTML 网页报告
当 Agent 完成预测数据收集后，你可以使用内置工具生成 HTML 网页：
```bash
# 进入脚本目录
cd scripts/

# 运行生成命令 (基于 JSON 数据)
python3 generate_html.py ../examples/usa_vs_aus_data.json ../output_report.html
```
生成的 `output_report.html` 完美适配手机端，包含返回主页导航、酷炫动画和胜率能量条！

### 3. 触发“自我进化” (SkillOpt)
比赛踢完后，将真实比分喂给引擎，让它变得更聪明：
```bash
# 命令格式: python3 evolution_ledger.py result <预测ID> <A队真实进球> <B队真实进球>
python3 scripts/evolution_ledger.py result 1 2 1

# 查看引擎反思与权重进化报告
python3 scripts/evolution_ledger.py review
```

### 4. 🎨 示例效果展示 (Live Demo)
我们在 `demo_site/` 目录下为你保留了真实生成的示例网页。**点击下方链接即可直接在浏览器中预览渲染后的精美网页效果**：
- 🌐 **赛事大厅导航**：[点击预览赛事大厅](https://wangdaokeaiduo.github.io/worldcup-predictor-skill/demo_site/index.html)
- 🇺🇸 **美国 vs 澳大利亚预测**：[点击预览美国 vs 澳大利亚](https://wangdaokeaiduo.github.io/worldcup-predictor-skill/demo_site/usa-vs-australia.html)
- 🇰🇷 **韩国 vs 墨西哥预测**：[点击预览韩国 vs 墨西哥](https://wangdaokeaiduo.github.io/worldcup-predictor-skill/demo_site/korea-vs-mexico.html)

> 💡 **提示**：无论你用 Cursor 还是 Codebuddy 执行，所有新生成的预测页面都会自动保存到本地的 `demo_site/` 文件夹下，并实时更新你的赛事导航中心！

---

## 💻 相对路径开箱即用
本项目内的所有数据读写（如 Python 读取 `prediction_ledger.json`）均采用绝对动态相对路径 `os.path.dirname(__file__)`。**无论你将本项目 clone 到什么路径，代码都能直接运行，完全无需修改！**

---

## 📜 许可证 (License)
MIT License. 欢迎各类预测大神、球迷与开发者 Fork 和 Star！🌟
