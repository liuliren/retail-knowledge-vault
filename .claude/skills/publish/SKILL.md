---
name: publish
version: v0.3
created: 2026-07-02
author: 六哥 + Claude
description: >
  公众号发布准备引擎（6步）。已签字草稿 → 标点预处理 → 主题选择+预览 →
  配图生成（huashu-gpt-image→gen_via_codex.py，配图缺失时自动触发）→
  上传 ImgBB → 插入 .md → doocs/md 操作指引。Claude 管排版和生图，人管发布动作。
allowed-tools: Bash, Read, Write, Edit
触发词: [publish, 发文, 配图上传, 准备发布, 走发布流程, 发布这篇]
输出物: 带 ImgBB URL + 选定主题的完整发布版 .md + doocs/md 操作指引
---

# /publish · 公众号发布准备引擎 v0.2

> **5步流水线**：前置检查 → 预处理 → **选主题（人）** → 上传配图 → 出操作指引

---

## 前置条件检查（不满足则中止并告知）

- [ ] 文章 frontmatter 含 `status: ready_to_publish` 且有六哥签字行
- [ ] `~/.imgbb_key` 已配置（ImgBB API key）
- [ ] 若需配图：`六哥自媒体/公众号/配图/` 下有对应图片文件

---

## Step 1 · 前置检查 + 配图盘点

读文章 frontmatter，输出：

```
✅ 文章确认
  标题：[标题]
  状态：[status]
  签字：[签字行]

📂 配图目录（六哥自媒体/公众号/配图/）：
  [ls 结果，每行一个文件]

🖼 建议配图位置：
  封面（顶部）：[推荐文件名 或 "待准备"]
  文内第N处：[位置描述 + 推荐文件名 或 "待准备"]
```

若配图目录为空或缺对应文件 → **不中止，进 Step 4 自动生图**。
若六哥确认跳过配图，可直接跳到 Step 5。

---

## Step 2 · 文章预处理

运行标点标准化脚本（把半角逗号/句号统一成全角，公众号排版要求）：

```bash
cd "/Users/davidliu/六哥自媒体"
python3 tools/normalize_punct.py "公众号/<文章文件名>.md"
```

若文章含 Markdown 表格，询问六哥是否转图：

```
文章中检测到表格。转成图片在公众号里显示更稳定（表格在移动端常错位）。
转图？[是/否]
```

若选是：
```bash
python3 tools/table2img.py "公众号/<文章文件名>.md"
# 输出：表格已转图，图片存入配图/，.md 中引用替换为 ![表格](配图/tableN.png)
```

---

## Step 3 · 排版主题选择（人工选择 · 必做）

展示主题速查表，让六哥选：

```
请选择这篇文章的排版主题：

序号 | 主题          | 气质          | 最适合
-----|--------------|---------------|----------------------------
  1  | McKinsey     | 深蓝·专业·强结构 | 方法论/框架/7D诊断
  2  | WSJ          | 近黑·数据·严肃  | 行业复盘/数据评论/趋势研判
  3  | NewYorker    | 墨黑·叙事·文学  | 深度故事/门店观察/随笔
  4  | WashingtonPost | 近黑·新闻·通用 | 新闻性复盘/事件解读
  5  | MUJI         | 米白·克制·温润  | 价值观/软表达/轻随笔
  6  | Apple        | 极简·大字·冲击  | 产品化方法论/重磅单一观点
  7  | Tesla        | 深黑·红线·強观点 | 行业批判/趋势预判/檄文
  8  | IBM          | 蓝方角·数据·体系 | 数据复盘/SOP/M-DEC

输入序号（1-8）选择主题，或直接说主题名：
```

六哥回答后，生成本地预览 PNG 供验收：

```bash
cd "/Users/davidliu/六哥自媒体"
python3 tools/theme_preview.py \
  --md "公众号/<文章文件名>.md" \
  --theme <选定主题名>
# 输出：排版主题/_预览_<主题名>.png
```

输出：
```
✅ 主题已选：[主题名]
预览图已生成：排版主题/_预览_[主题名].png
请打开预览图确认效果。满意后告我继续；需要换主题回复主题序号。
```

→ **等六哥确认预览满意后才进 Step 4。**

---

## Step 4 · 配图生成（配图缺失时触发 · 已有配图则跳过直接进 Step 5）

**生图链路**：`huashu-gpt-image` prompt 铁律 → `gen_via_codex.py`（GPT-image-2，吃 ChatGPT 订阅额度）→ 存入配图目录

### 4.1 写配图 prompt（遵循 huashu-gpt-image 铁律）

每张图一个中文 prompt，硬约束：
- **≤80 字**，超过则重写
- **用真实参考名**替代形容词（如「麦肯锡报告配图风」「Dieter Rams 工业设计感」「《经济学人》数据图风」）
- **禁止** `Subject:` / `Style:` / `Constraints:` 等英文段落式伪结构
- **图里文字默认中文**（描述性标签/标题），品牌名/技术名保留原样
- 结尾写明尺寸需求（封面 1410×600，文内图 1080×810）

**主题风格对应**（按 Step 3 选定主题匹配）：
| 主题 | 配图 prompt 风格锚 |
|---|---|
| WSJ | 《华尔街日报》头版图表风，近黑白色调，赭石点缀 |
| McKinsey | 麦肯锡咨询报告配图风，深蓝结构感，干净留白 |
| NewYorker | 《纽约客》手绘插画风，线条简洁，砖红黑白 |
| IBM | IBM Carbon 设计系统风，蓝白方角，数据图感 |
| Apple | Apple 产品页配图风，极简居中，浅灰底 |

### 4.2 生成 JSONL batch 文件

在 `六哥自媒体/公众号/配图/` 下创建 `_batch_jobs.jsonl`，每行一张图：

```json
{"prompt": "[中文prompt·≤80字]", "out": "公众号/配图/<文章slug>_封面.png", "size": "1410x600", "quality": "high"}
{"prompt": "[中文prompt·≤80字]", "out": "公众号/配图/<文章slug>_01_<描述>.png", "size": "1080x810", "quality": "high"}
```

### 4.3 跑 gen_via_codex.py 批量出图

```bash
cd "/Users/davidliu/六哥自媒体"
CODEX=~/.nvm/versions/node/v20.20.2/bin/codex

# 临时把 codex 加进 PATH，让 gen_via_codex.py 能找到它
export PATH="$HOME/.nvm/versions/node/v20.20.2/bin:$PATH"

python3 ~/.claude/skills/huashu-gpt-image/scripts/gen_via_codex.py \
  --batch 公众号/配图/_batch_jobs.jsonl \
  --concurrency 2
```

> **⚠️ 注意**：必须用单张逐张跑（`--ignore-user-config`），不能用 batch 模式。codex 开了十几个 plugin，skills context budget 爆满后 imagegen 被踢出去会导致全部超时。正确姿势：
>
> ```bash
> # 每张单独跑，用 --ignore-user-config 排除 plugin 干扰
> echo "[中文prompt]" | timeout 180 codex exec -s workspace-write \
>   --skip-git-repo-check --ignore-user-config \
>   -C "/Users/davidliu/六哥自媒体" - 2>&1 | tail -10
> ```
>
> 每张约 60-90s，并发跑两个 terminal 即可。

### 4.4 确认产出

```bash
ls -la "/Users/davidliu/六哥自媒体/公众号/配图/"
```

列出生成的图片文件，确认尺寸和数量。若某张失败（❌）→ 单独重跑：

```bash
python3 ~/.claude/skills/huashu-gpt-image/scripts/gen_via_codex.py \
  --prompt "[重写的prompt]" \
  --out 公众号/配图/<失败的文件名>.png \
  --size <尺寸> --quality high
```

---

## Step 5 · 配图上传 ImgBB

```bash
cd "/Users/davidliu/六哥自媒体"

# 单张：
python3 tools/upload_image.py 公众号/配图/<文件名>.png --md

# 批量（只传本文章的图，避免把其他文章旧图混进去）：
python3 tools/upload_image.py 公众号/配图/<文章slug>_*.png --md
```

收集所有上传结果，整理成插入清单：

```
上传完成，图片清单：

封面   → ![封面](https://i.ibb.co/XXX/封面.png)
文内图1 → ![说明](https://i.ibb.co/XXX/图1.png)
...
```

然后按位置把 URL 插入 .md：

**封面**（正文标题下方、第一段之前）：
```markdown
# 标题

![封面](https://i.ibb.co/...)

正文第一段...
```

**文内图**（对应段落结束后）：
```markdown
...段落结束。

![说明](https://i.ibb.co/...)

## 下一节
```

编辑完成后确认：`已在 N 处插入图片。`

---

## Step 5 · 输出 doocs/md 操作指引

```
📋 doocs/md 排版操作步骤：

  工具地址：md.doocs.org（在线版，无需安装）

  1. 打开 md.doocs.org
  2. 把以下文件正文粘贴进左侧（从 # 标题开始，不含 frontmatter）：
       [文章完整路径]
  3. 右侧点「样式」→「自定义CSS」→ 粘入主题文件内容：
       [主题CSS完整路径：六哥自媒体/排版主题/<主题名>.css]
  4. 预览确认：图片正常显示 / 标题层级 / 粗体分隔线
     （ImgBB 图需联网才显示，VPN 问题会导致预览不出图但发布后读者正常看）
  5. 点「复制」→ 粘贴到公众号后台新建图文
  6. 公众号后台手动上传封面图（独立于正文，建议用 [封面文件名]）
  7. 预览 → 六哥签字 → 发送

💡 主题文件直接用 cat 复制内容：
     cat "/Users/davidliu/六哥自媒体/排版主题/<主题名>.css"
```

---

## Step 6 · 发布后更新（六哥告知发布完成后执行）

更新选题库 `12_自媒体内容与表达转化/01_选题库.md`：
- 对应行改为 `✅已发·YYYY-MM-DD`

更新已发稿回流索引 `12_自媒体内容与表达转化/05_已发稿回流索引.md`：
- 填入发布时间，蒸馏状态改为「待蒸馏」
- 提醒六哥发布后走 `/ingest` 回流进知识库

---

## 铁律

- **Step 3 主题选择必须六哥确认预览后才往下走**，不允许跳过
- **不主动发布**：Claude 只做到"文章可粘贴公众号后台"，点发送是六哥的动作（D档）
- **frontmatter 不进 doocs/md**：只复制 `---` 以下正文，frontmatter 会破坏排版
- **封面图单独处理**：doocs/md 不控制公众号封面图，必须在公众号后台另行上传
- **配图命名规范**：`文章slug_序号_描述.png`，方便归档复用

---

## 配图目录约定

```
六哥自媒体/公众号/配图/
  <文章slug>_封面.png
  <文章slug>_01_<描述>.png
  <文章slug>_02_<描述>.png
```

参考：简史上下篇 → `上篇_封面.png`、`下篇_02_密度飞轮.png`

---

## 版本记录

| v0.3 | 2026-07-02 | 加入 Step4 生图（huashu-gpt-image→gen_via_codex.py→配图目录）·流程升为6步·配图缺失不再中止 |
| v0.2 | 2026-07-02 | 加入 Step2 预处理 + Step3 主题选择（8套速查+预览确认）·流程重构为5步 |
| v0.1 | 2026-07-02 | 初版·基于简史上下篇发布实证流程 |
