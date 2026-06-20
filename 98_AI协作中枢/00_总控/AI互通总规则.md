
VAULT="/Users/davidliu/KnowledgeBase/retail-knowledge-vault"

cd "$VAULT" || exit 1

mkdir -p "98_AI协作中枢/00_总控"
mkdir -p "98_AI协作中枢/01_Claude_Code/Claude输出区"
mkdir -p "98_AI协作中枢/01_Claude_Code/Claude记忆区"
mkdir -p "98_AI协作中枢/02_Codex/Codex输出区"
mkdir -p "98_AI协作中枢/03_共享上下文"
mkdir -p ".claude"

cat > "98_AI协作中枢/00_总控/AI互通总规则.md" <<'EOF'
# AI互通总规则

## 一、总原则

本 Obsidian Vault 是“晟果新零售咨询 / 六哥零售科学零售知识库”的主知识库。

Claude Code、Codex、Obsidian 都围绕同一个本地 Markdown Vault 工作。

## 二、写入纪律

1. 任何 Agent 不得随意大规模重命名、删除、移动文件。
2. 修改正式知识库文件前，必须先阅读相关上下文。
3. 涉及真实门店数据、客户资料、原始销售数据时，只能生成分析说明，不得擅自清洗、覆盖、删除原始文件。
4. 新增文件必须放入对应目录，不允许全部堆在根目录。
5. 输出文件优先使用 Markdown；涉及表格工具时再使用 Excel。
6. 每次重要修改后，应在当前任务队列或输出区留下变更记录。

## 三、协作分工

- Claude Code：知识库结构、Markdown 文档、方法论沉淀、项目归档、提示词生成。
- Codex：代码仓库、脚本、Excel 工具、报表系统、自动化工具。
- Obsidian：人工阅读、编辑、链接、复盘、最终知识沉淀。

## 四、禁止事项

- 禁止无确认删除正式文件。
- 禁止把临时推理过程写入正式知识库。
- 禁止把未验证结论写成定论。
- 禁止混用“圣果新零售”，统一使用“晟果新零售”。
