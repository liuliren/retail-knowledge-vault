> **⚠️ 2026-06-30 注**：本文为 Claude 工具学习笔记（Reference 层，非零售方法论），存放在 `00_入口与总索引/` 位置有误，待 NAV-GOV-02 G05 迁移至 `98_AI协作中枢/`。当前只读保留，勿作零售知识库导航使用。

  **1. 官方文档学习范围**                                                 

  **范围维度:** 入口索引                                                  

  **本轮覆盖:** llms.txt（已读全量目录）                                                        

  **本轮未覆盖（待后续按需补）:** —                                       

  ────────────────────────────────────────                                                  

  **范围维度:** 已抓核心文档                                              

  **本轮覆盖:** memory · context-window · commands · sub-agents · hooks · statusline ·          

    permissions · costs · claude-directory                                                  

  **本轮未覆盖（待后续按需补）:** quickstart / setup / interactive-mode / skills / hooks-guide /

    mcp / channels / plugins / sandboxing / checkpointing / agent-teams / agent-sdk 全系列 /

  

    scheduled-tasks / routines / what's-new

  ────────────────────────────────────────

  **范围维度:** 抓取方式                                                                        

  **本轮覆盖:** 每页用定向 prompt 提取目标字段，不复制原文

  **本轮未覆盖（待后续按需补）:** —                                                             

  ────────────────────────────────────────                            

  **范围维度:** 信息状态                                                                        

  **本轮覆盖:** 来源可追溯（每条结论可回查原页）

  **本轮未覆盖（待后续按需补）:** —                                                             

  ---

  **2. 官方文档主题分类**

  来自 llms.txt 的官方目录（合并同类项后）：

  1. **入门与原理**：Quickstart / Overview / How Claude Code works / Common workflows / Best    

  practices                                                                                 

  2. **安装与认证**：Setup / Auth / Env vars / Troubleshoot install                             

  3. **配置体系**：Settings / Server-managed settings / .claude/ 目录 / Terminal config /       

  Keybindings / **Status line** / Auto mode / Output styles / Model config / Fast mode / Debug  

  config                                                                                    

  4. **CLI 与命令**：CLI reference / **Commands** / Interactive mode                                

  5. **平台与界面**：Web / Desktop / Chrome / Slack / VS Code / JetBrains / Computer use /      

  Remote control / Voice / Scheduled tasks                                                  

  6. **记忆与上下文**：**Memory（CLAUDE.md + auto memory）** / **Context window** / Checkpointing       

  7. **权限与安全**：**Permission modes** / **Permissions** / Security / Sandboxing / Data usage / Zero 

  data retention                                                                            

  8. **Skills/Subagents/Commands**：Skills / **Sub-agents** / Agent teams                           

  9. **Hooks**：Hooks guide / **Hooks reference**                                                   

  10. **MCP**：MCP / Agent SDK MCP                                        

  11. **Channels / Webhooks**：channels / channels-reference                                    

  12. **Plugins**：plugins / plugins-reference / discover-plugins / plugin-marketplaces /

  plugin-dependencies                                                                       

  13. **Agent SDK**：overview / quickstart / agent-loop / Python / TypeScript / hooks / skills /

   subagents / sessions / streaming / structured-outputs / permissions / tool-search /      

  hosting / observability / cost-tracking

  14. **会话工作流**：scheduled-tasks / routines / ultraplan / ultrareview / deep-links         

  15. **企业与云**：admin-setup / analytics / network-config / llm-gateway / Bedrock / Vertex / 

  Foundry                                                                                   

  16. **CI/CD**：GitHub Actions / GitHub Enterprise / GitLab CI/CD                              

  17. **成本与监控**：**Costs** / Monitoring / Analytics                                            

  18. **参考**：Tools reference / Errors / Glossary / Troubleshooting / Changelog / What's new  

  ---                                                                                       

  **3. 与我们知识库工作流最相关的主题 TOP 15**                                                  

  按"知识库长期维护 + 三个月生存战 + 额度可控"打分，从高到低：

  **#:** 1                                                                                      

  **主题:** **Memory（CLAUDE.md + auto memory）**                                                   

  **解决什么:** 跨会话稳定指令                                                                  

  **关键官方机制:** 项目/用户/本地/管理策略四级 CLAUDE.md，按目录树合并；auto memory 写到     

    ~/.claude/projects/<repo>/memory/MEMORY.md（开头 200 行 / 25KB 进上下文）             

  **配置位置:** ./CLAUDE.md ./.claude/CLAUDE.md ~/.claude/CLAUDE.md ./CLAUDE.local.md

  **用法（本 vault）:** 已有 567 行 CLAUDE.md，**待核验：是否拆分到** **.claude/rules/**                

  **减少每会话上下文**

  **风险/边界:** 长 CLAUDE.md 降低遵从率（官方建议 <200 行）                                    

  **入库建议:** 入库                                                      

  ────────────────────────────────────────

  **#:** 2                                                                                      

  **主题:** **Context window /** **/compact**

  **解决什么:** 上下文管理与压缩                                                                

  **关键官方机制:** 200K 窗口；/compact 用结构化总结替换历史；项目根 CLAUDE.md、auto memory、MCP

  

    工具、环境信息**自动重载**；skill 列表**不**重载，只保留已调用 skill

  **配置位置:** /compact [指令]

  **用法（本** **vault）:** 长任务前先 /compact 关注 X；切换主题用 /clear

  **风险/边界:** 嵌套 CLAUDE.md 不自动重载，需触发文件读取；指令型口头补充会丢

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 3                                                                                      

  **主题:** **Slash commands**（速查）

  **解决什么:** 会话内控制                                                                      

  **关键官方机制:** 见 §6                                                 

  **配置位置:** 内置 + Skill 机制

  **用法（本** **vault）:** 减少误用、降低 token

  **风险/边界:** 见 §6

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 4                                                                                      

  **主题:** **Permissions**

  **解决什么:** 拦截危险操作 / 减少打扰                                                         

  **关键官方机制:** 规则评估顺序 deny → ask → allow；Bash(npm run *) Read(./.env)

    WebFetch(domain:x) Agent(Explore)；模式

    default/acceptEdits/plan/auto/dontAsk/bypassPermissions

  **配置位置:** .claude/settings.json .claude/settings.local.json ~/.claude/settings.json

    管理策略

  **用法（本** **vault）:** 为本 vault 配置 Read(**) 全允许、Edit(./90_素材*)/Edit(./99_归档/**)

    限制；Bash(git push *) 需确认

  **风险/边界:** bypassPermissions 仍保留 rm -rf / 回路熔断；通配符约束 URL 不可靠

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 5                                                                                      

  **主题:** **Hooks**

  **解决什么:** 自动化与防护                                                                    

  **关键官方机制:** 事件覆盖 PreToolUse / PostToolUse / UserPromptSubmit / Stop /

    SessionStart/End / PreCompact/PostCompact / InstructionsLoaded 等；类型

    command/http/mcp_tool/prompt/agent

  **配置位置:** settings.json 的 hooks 字段

  **用法（本** **vault）:** 慎入库；本阶段只记录机制，不开 hook

  **风险/边界:** Hooks 拥有用户权限 → 凭据外泄、提示注入、权限旁路均可能

  **入库建议:** 入库（仅文档）

  ────────────────────────────────────────

  **#:** 6                                                                                      

  **主题:** **Sub-agents**

  **解决什么:** 隔离上下文、降本                                                                

  **关键官方机制:** 每个子代理独立 context window；可指定 model: haiku；scope

  项目/用户/CLI；fork

    继承会话

  **配置位置:** .claude/agents/*.md ~/.claude/agents/*.md

  **用法（本** **vault）:** 把"扫描 vault 全量 SKU/陈列文件"等高吞吐任务交给 Explore

    子代理，主会话只看摘要

  **风险/边界:** 子代理本身有 context cost；agent teams 约 7× 普通会话

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 7                                                                                      

  **主题:** **Costs / token reduction**

  **解决什么:** 控成本                                                                          

  **关键官方机制:** /usage(=/cost=/stats) 显示本会话；推荐 /clear 切换任务、Sonnet 优先、Haiku

    用于子代理、CLI 优于 MCP server、/effort low、MAX_THINKING_TOKENS=8000

  **配置位置:** /usage /effort /model

  **用法（本** **vault）:** 写一份"每日 token 预算 SOP"

  **风险/边界:** 估值仅本地估算，**计费以** **Console** **为准（待核验本地** **Pro/Max** **订阅口径）**

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 8                                                                                      

  **主题:** **Status line**

  **解决什么:** 一眼看 token/cost/branch                                                        

  **关键官方机制:** 脚本读 stdin JSON，输出文本；字段含                   

    model、cost、context_window.used_percentage、rate_limits.{five_hour,seven_day}、workspac

  e.git_worktree、session_id、transcript_path

  **配置位置:** ~/.claude/settings.json.statusLine

  **用法（本** **vault）:** 显示「上下文 % + 5 小时额度 % + 当前 worktree」

  **风险/边界:** 脚本慢/挂会拖累界面；refreshInterval 最小 1s

  **入库建议:** 入库（轻量）

  ────────────────────────────────────────

  **#:** 9                                                                                      

  **主题:** **.claude/** **目录结构**

  **解决什么:** 知道东西在哪                                                                    

  **关键官方机制:** 项目级                                                

    .claude/{CLAUDE.md,rules,skills,commands,agents,agent-memory,settings*.json}；用户级

    ~/.claude/{CLAUDE.md,rules,agents,settings.json,plugins,projects/<repo>/{memory,

  *.jsonl,

     tool-results/},file-history/<session>/,history.jsonl}

  **配置位置:** 见左

  **用法（本** **vault）:** 复盘机制要用到 ~/.claude/projects/<repo>/*.jsonl

  **风险/边界:** 全是明文，**包含工具输出、命令输出、粘贴内容**，注意脱敏

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 10                                                                                     

  **主题:** **Logs / transcript**

  **解决什么:** 复盘原料                                                                        

  **关键官方机制:** 会话 transcript = ~/.claude/projects/<project>/<session>.jsonl；大输出 =

    同目录 tool-results/；文件改动快照 = ~/.claude/file-history/<session>/；提示历史 =

    ~/.claude/history.jsonl

  **配置位置:** —

  **用法（本** **vault）:** 月度从 transcript 蒸馏"高频问题/翻车案例"入 15_刻意练习与成长

  **风险/边界:** 含 API key 等敏感内容时不可外发

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 11                                                                                     

  **主题:** **Permission modes（plan）**

  **解决什么:** 大改前先看路径                                                                  

  **关键官方机制:** Shift+Tab 进入 Plan 模式只读分析                      

  **配置位置:** defaultMode

  **用法（本** **vault）:** 涉及"批量改 vault 结构"前默认进 plan

  **风险/边界:** —

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 12                                                                                     

  **主题:** **Init /** **/memory**

  **解决什么:** 维护 CLAUDE.md                                                                  

  **关键官方机制:** /init 已存在文件时给改进建议（不覆盖）；/memory 列出本会话加载的所有

    CLAUDE.md/CLAUDE.local.md/rules，可开关 auto memory

  **配置位置:** —

  **用法（本** **vault）:** 已经走过 /init；用 /memory 定期审阅加载情况

  **风险/边界:** —

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 13                                                                                     

  **主题:** **Skills**（vs CLAUDE.md）

  **解决什么:** 减小常驻上下文                                                                  

  **关键官方机制:** 启动时只列名/单行描述，调用时才加载本体；可用 disable-model-invocation: true

  

    完全隐藏

  **配置位置:** .claude/skills/<name>/SKILL.md

  **用法（本** **vault）:** 把"商品诊断 SOP""DisplayMap 检查""52 周 MD 模板"做成 skill

  **风险/边界:** Skill 在 /compact 后只保留**已调用过**的，未调用的描述不会重新注入

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 14                                                                                     

  **主题:** **.claude/rules/** **路径范围规则**

  **解决什么:** 大库分模块加载指令                                                              

  **关键官方机制:** rules 默认全量加载；带 paths: 前置 frontmatter 的只有命中文件时触发

  **配置位置:** .claude/rules/*.md 支持子目录

  **用法（本** **vault）:** 把 CLAUDE.md 中"陈列""商品诊断""52 周 MD"等模块拆出来按 paths: 加载

  **风险/边界:** 路径触发型 rule 经 /compact 后被总结掉，下次读对应文件再加载

  **入库建议:** 入库

  ────────────────────────────────────────

  **#:** 15                                                                                     

  **主题:** **Checkpointing /** **/rewind**

  **解决什么:** 翻车回滚                                                                        

  **关键官方机制:** 文件改动快照保存于 ~/.claude/file-history/<session>/  

  **配置位置:** /rewind 双击 ESC

  **用法（本** **vault）:** 大改 vault 前先确认 checkpoint 启用

  **风险/边界:** **待核验：知识库** **markdown** **是否完整入快照**

  **入库建议:** 入库

  

  ---

  **4. 上下文 / 记忆 / 压缩机制总结**

  **4.1 启动时进上下文的内容（按官方 context-window 时间线）**

  1. System prompt                                                    

  2. Auto memory MEMORY.md（前 200 行 / 25KB 取小）

  3. 环境信息（cwd、平台、shell、OS、git 状态）                                             

  4. MCP 工具名（schema 默认延迟，仅工具搜索时按需加载，可由 ENABLE_TOOL_SEARCH=auto/false  

  调整）                                                                                    

  5. Skill 名 + 单行描述（含 disable-model-invocation: true 的不列）                        

  6. CLAUDE.md 全量（项目/用户/本地/管理策略，按目录树由根到 cwd 拼接，再拼                 

  CLAUDE.local.md）                                                                         

  7. .claude/rules/*.md 中无 paths: 的规则（与 .claude/CLAUDE.md 同优先级）                 

  **4.2** **/compact** **之后**                                                   

  ┌───────────────────────────────┬─────────────────────────────────────────────────────┐   

  │             机制              │                        行为                         │

  ├───────────────────────────────┼─────────────────────────────────────────────────────┤   

  │ 项目根 CLAUDE.md /            │ **重新从磁盘注入**                                      │

  │ .claude/CLAUDE.md             │                                                     │

  ├───────────────────────────────┼─────────────────────────────────────────────────────┤   

  │ Auto memory MEMORY.md         │ **重新注入**                                            │

  ├───────────────────────────────┼─────────────────────────────────────────────────────┤   

  │ 环境信息 / MCP 工具列表       │ **重新注入**                                            │   

  ├───────────────────────────────┼─────────────────────────────────────────────────────┤

  │ Skill 列表                    │ **不重新注入**；仅保留**已被调用过**的 skill                │   

  │                               │ 本体（且超额会被截断）                              │

  ├───────────────────────────────┼─────────────────────────────────────────────────────┤   

  │ 嵌套子目录 CLAUDE.md / paths: │ **不重新注入**，下次读对应文件时再触发                  │

  │  规则                         │                                                     │   

  ├───────────────────────────────┼─────────────────────────────────────────────────────┤

  │ 会话历史                      │ 替换为结构化总结                                    │   

  └───────────────────────────────┴─────────────────────────────────────────────────────┘   

  **4.3** **/clear** **vs** **/compact** **vs** **/resume**                                                         

  - /clear（别名 /reset /new）：开新会话、清空上下文，**旧会话仍可** **/resume** **找回**               

  - /compact [指令]：保留同一会话，把历史压缩为摘要；可附"重点保留代码示例"等指令；也可在

  CLAUDE.md 里固化压缩偏好                                                                  

  - /resume：恢复旧会话（建议清前先 /rename 命名）                    

  **4.4 上下文可视化**：/context 显示当前占用色块图与优化建议。                                 

  ---                                                                                       

  **5. 日志 / transcript / session 机制总结**                             

  **5.1 落盘位置（基于** **~/.claude/****）**

  ┌─────────────────────────────────────┬───────────────────────────────────────────────┐ 

  │                路径                 │                     内容                      │   

  ├─────────────────────────────────────┼───────────────────────────────────────────────┤ 

  │ projects/<project>/<session>.jsonl  │ 完整会话 transcript：每条消息 / 工具调用 /    │ 

  │                                     │ 工具结果                                      │ 

  ├─────────────────────────────────────┼───────────────────────────────────────────────┤ 

  │ projects/<project>/<session>/tool-r │ 大块工具输出（被本轮 WebFetch                 │ 

  │ esults/                             │ 用到的就是这里）                              │   

  ├─────────────────────────────────────┼───────────────────────────────────────────────┤ 

  │ projects/<project>/memory/MEMORY.md │ 该项目 auto memory                            │   

  │  + 主题文件                         │                                               │   

  ├─────────────────────────────────────┼───────────────────────────────────────────────┤

  │ file-history/<session>/             │ 改动文件的预改快照（用于 /rewind 回滚）       │   

  ├─────────────────────────────────────┼───────────────────────────────────────────────┤   

  │ history.jsonl                       │ 你输入过的所有提示，含时间戳与项目路径（上箭  │

  │                                     │ 头召回用）                                    │   

  └─────────────────────────────────────┴───────────────────────────────────────────────┘   

  <project> 由 git 仓库路径派生；同一仓库的 worktree 与子目录共享一个 auto memory 目录。    

  **5.2 重要属性**                                                                              

  - 全部明文 markdown / jsonl，**任何过工具的内容都会落盘**：文件内容、命令输出、粘贴文本均在内 

  - 仅本机；不跨机器、不上云

  - hooks 也能拿到 transcript_path（用作审计或自动复盘提取）                                

  **5.3 与本 vault 的衔接（建议，不实施）**                                                     

  - 月度从 *.jsonl 蒸馏「高频问题 / 翻车案例 / 通用提问模板」→ 15_刻意练习与成长/           

  - transcript 不入库，只入库蒸馏后的结论                             

  ---                                                                 

  **6. slash commands 速查**                                                                    

  来自官方 commands.md（内置；不含 skill 与第三方）：

  

  ┌──────────────────────────┬────────────────────────────────────┬────────────────────┐  

  │           命令           │                说明                │       何时用       │  

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤  

  │ /clear（别名 /reset      │ 开新会话、清上下文，旧会话保留可   │ 主题切换           │  

  │ /new）                   │ /resume                            │                    │  

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /compact [指令]          │ 总结当前会话以释放上下文，可指定保 │ 长会话变慢前、新长 │    

  │                          │ 留重点                             │ 任务前             │    

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /context                 │ 当前 context 占用色块图与优化提示  │ 怀疑爆窗时         │  

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /usage（=/cost=/stats）  │ 本会话 token、订阅额度条、活跃统计 │ 周期性检查         │ 

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /config（=/settings）    │ 主题/模型/输出风格交互配置         │ —                  │ 

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /status                  │ 状态面板（版本/模型/账户/连接），  │ 排错               │    

  │                          │ 响应中也能用                       │                    │ 

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /model [model]           │ 切模型；带方向键调 effort          │ 难度切换           │    

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤ 

  │ /effort [low|medium|high │ 调推理深度，立即生效               │ 简单任务降到 low   │    

  │ |xhigh|max|auto]         │                                    │ 省 token           │    

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤

  │ /init                    │ 生成 / 改进                        │ 已用过             │    

  │                          │ CLAUDE.md（已存在则给建议）        │                    │    

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /memory                  │ 列出本会话加载的所有 CLAUDE.md /   │ 排查"指令没生效"   │    

  │                          │ rules，开关 auto memory            │                    │    

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤

  │ /permissions             │ 查看/管理权限规则                  │ 加白/降扰          │    

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤

  │ /agents                  │ 管理 subagent                      │ 配子代理           │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /mcp                     │ 查看/禁用 MCP 服务器               │ 减 MCP 噪声        │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /statusline              │ 配置/删除状态栏                    │ —                  │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /add-dir                 │ 给 Claude 加额外可访问目录         │ 跨库工作           │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /rewind                  │ 回滚到上个 checkpoint              │ 翻车               │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /rename                  │ 重命名当前会话（便于以后 /resume） │ 长会话清理前       │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /resume                  │ 恢复旧会话                         │ —                  │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /help                    │ 帮助                               │ —                  │

  ├──────────────────────────┼────────────────────────────────────┼────────────────────┤    

  │ /claude-api [migrate |   │ 加载 Claude API 参考 / 升级模型 ID │ 不适用本 vault     │

  │ managed-agents-onboard]  │                                    │                    │    

  └──────────────────────────┴────────────────────────────────────┴────────────────────┘

  **待核验**：/btw 在官方 commands.md 主表中**未直接列出**；可能是 skill / 别名 /                   

  已废弃，需后续直接在会话内 / 列表确认或抓 interactive-mode.md 与 changelog。本轮不下结论。

  ---                                                                 

  **7. subagents 使用规范**

  **7.1 何时用**

  - 一次性高吞吐"读多写少"工作（扫 vault、跨多门店比对、处理长 Excel/POS 导出）             

  - 重复出现的同类副任务（每周做"陈列规则一致性扫描"）→ 写成 named subagent                 

  - 想限制工具集（只给 Read/Grep，禁 Write）做受控审查                                      

  **7.2 何时不用**                                                                              

  - 信息少、上下文小、回合短的任务（spawn 本身有冷启动成本）                                

  - 需要主会话已有的对话上下文 → 用 **fork**（继承历史）而不是 named subagent

  - 多代理需互相通信、并行 → 用 **agent teams**（注意约 7× token），本阶段不开                  

  **7.3 文件位置 / 关键 frontmatter**                                                           

  - .claude/agents/*.md（项目）/ ~/.claude/agents/*.md（用户）/ CLI --agents JSON（一次性） 

  - 字段（部分，待对照官方 sub-agents.md

  完整字段表逐项核验）：name、description（决定自动派发）、tools、model（推荐 Haiku         

  控本）、memory: project|local|user（持久记忆位置）、initialPrompt   

  **7.4 风险**                                                            

  

  - 子代理本身要加载 CLAUDE.md / MCP / skill 列表，越多越贵

  - 内置 subagent 的 description 决定是否被自动派发，写得宽会被滥用

  - agent-memory/ 与主会话 auto memory 是**两套**目录，注意区分                                 

  ---                                                                                       

  **8. hooks 使用规范**                                                                         

  **8.1 适合自动化的场景**

  - **审计/只读日志**：PostToolUse 写入本地 jsonl，方便复盘                                     

  - **环境注入**：SessionStart 注入分支名/项目状态作为 additionalContext（陈述性事实，不下指令）

  - **输出过滤降本**：PreToolUse 把 npm test/长输出 grep 成失败行（官方 costs 页例子）          

  - **只读校验**：PostToolUse 跑本地 lint，失败则 exit 2 把 stderr 反馈给 Claude                

  **8.2 不适合 / 风险高**                                                                       

  - 任何 HTTP 出站到第三方                                                                  

  - 静默修改 tool_input（路径替换、命令替换）                         

  - 一刀切 permissionDecision: "allow" 旁路所有权限                                         

  - 把"指令性文本"塞进 additionalContext（会变成提示注入）                                  

  - 无超时控制 / 无错误处理（hangs 阻塞 agent loop）                                        

  **8.3 配置位置 / 优先级**                                                                     

  settings.json 的 hooks 字段；解析顺序：用户 → 项目 → 本地 → 管理策略 → 插件 →             

  内置；allowManagedHooksOnly: true 时仅管理策略生效。

  **8.4 决策契约（部分）**                                                                      

  - exit 0：成功；可输出 JSON hookSpecificOutput，additionalContext 注入 Claude             

  - exit 2：阻断；stderr 给 Claude                                    

  - 其他：非阻断错误                                                                        

  - permissionDecision: allow|deny|ask|defer（注：deny rule 永远先于 hook allow 生效；hook

  exit 2 会先于 allow rule 生效）                                                           

  **本轮建议**：先**只学不开**，三个月生存战期内不引入 hook。                                       

  ---                                                                                       

  **9. statusLine 使用规范**                                              

  **9.1 输入字段（官方 schema 节选）**

  cwd / session_id / session_name / transcript_path / model.{id,display_name} /             

  workspace.{current_dir,project_dir,git_worktree,added_dirs} / version / output_style.name 

  / cost.{total_cost_usd,total_duration_ms,total_lines_added/removed} /                     

  context_window.{used_percentage,remaining_percentage,current_usage,context_window_size} /

  effort.level / thinking.enabled /

  rate_limits.{five_hour,seven_day}.{used_percentage,resets_at} / vim.mode / agent

  

  **9.2 适合展示**                                                                              

  - model.display_name                                                                      

  - context_window.used_percentage（最关键）                          

  - rate_limits.five_hour.used_percentage                                                   

  - workspace.git_worktree（如未来引入 worktree）

  - cost.total_cost_usd（注意：订阅用户仅供参考）                                           

  **9.3 边界**                                                                                  

  - 脚本卡住会拖累 UI

  - refreshInterval 最小 1s；缺省只在事件触发时跑（主会话空闲时不会刷新，时间型字段需自己开

  refresh）                                                                                 

  - 不要在 statusLine 里做网络调用 / 写文件

  ---                                                                 

  **10. 权限与安全红线**                                                                        

  **10.1 评估顺序**：deny → ask → allow（任何层 deny 一票否决）

  **10.2 模式速选**                                                                             

  ┌───────────────────┬───────────────────────────────────────────┐                         

  │       模式        │                   用途                    │   

  ├───────────────────┼───────────────────────────────────────────┤

  │ default           │ 首次使用提示（默认）                      │

  ├───────────────────┼───────────────────────────────────────────┤

  │ plan              │ 只读分析，**复盘/规划/扫库优先**              │                         

  ├───────────────────┼───────────────────────────────────────────┤                         

  │ acceptEdits       │ 自动接受工作区内 file edit 与常见文件命令 │                         

  ├───────────────────┼───────────────────────────────────────────┤                         

  │ auto              │ 实验性背景安全分类器自动批                │   

  ├───────────────────┼───────────────────────────────────────────┤                         

  │ dontAsk           │ 未预批一律拒（适合高度受控 SOP）          │

  ├───────────────────┼───────────────────────────────────────────┤                         

  │ bypassPermissions │ 全部跳过；仅在容器/VM 用；rm -rf / 仍熔断 │   

  └───────────────────┴───────────────────────────────────────────┘                         

  **10.3 规则语法（要点）**                                                                     

  - Tool / Tool(specifier)；Bash 通配 * 任意位置；Bash(ls *) 与 Bash(ls*)                   

  不同（前者强制词边界）

  - find -exec/-delete / xargs -flag / watch / setsid 这类**不会**被 Bash(find *) 等覆盖        

  - Read(./.env) / Edit(/src/**/*.ts)（gitignore 风格；/                                    

  是项目根，**不是文件系统根**；要绝对路径用 //）                                               

  - Bash 内置只读集合（ls/cat/grep/find/wc/diff/stat/du/cd + 只读 git）默认免确认           

  - Read/Edit 规则**只对内置工具**生效，**不拦 Bash 子进程的** **cat .env**；要 OS 级用 sandbox         

  **10.4 红线（建议本 vault 配置方向，仅建议不实施）**                                          

  - deny：Edit(/99_归档/**)、Edit(./CLAUDE.md)（防误改主规则）、Bash(git push *)            

  - ask：所有 Bash(rm *)、Bash(mv */99_*)                             

  - allow：Bash(git status) Bash(git diff *) Bash(git log *) 等只读 git；Read 全开          

  - 不要试图用 Bash(curl http://x.com/*) 限 URL — 官方明确说不可靠                          

  - **管理策略级**对个人 vault 不适用；个人级写到 ~/.claude/settings.json                       

  ---                                                                                       

  **11. 降低 token 与额度消耗的操作规范**                                                       

  按官方 costs.md + 我们 vault 场景整理：

  **A. 会话纪律**                                                                               

  1. 切主题先 /clear（/rename 后再清，便于 /resume）                                        

  2. 长任务前先 /compact 关注 X，把当前对话浓缩                       

  3. 简单任务 /effort low；高难复盘 /effort high，做完降回来                                

  4. 所有"扫 vault 全量""跨多门店比对""读长 Excel"任务 → subagent                           

  **B. 模型分层**                                                                               

  - 主会话：Sonnet 兜底；架构/方法论体系级思考用 Opus                                       

  - 子代理：Haiku 优先（在 frontmatter model: haiku）

  **C. 上下文优化**                                                       

  5. CLAUDE.md 控制在 200 行内；当前 567 行**强烈建议**拆 .claude/rules/：                      

    - rules/陈列.md（paths: ["06_陈列规划与DisplayMap/**"]）

    - rules/商品诊断.md（paths:                                                             

  ["04_商品诊断与商品力提升/**","09_门店案例与项目复盘/**/03_商品诊断/**"]）                

    - rules/方法论.md（paths: ["01_科学零售方法论/**"]）                                    

    - rules/反幻觉与逻辑一致性.md（无 paths，全局加载）                                     

  6. 重型 SOP（DisplayMap 检查、52 周 MD 模板、商品诊断流程）→ skill 而非                   

  CLAUDE.md，按需加载                                                                       

  7. 关闭未用的 MCP server（/mcp）；CLI 优于 MCP server（gh、bq、gcloud）                   

  **D. 思考 token**                                                       

  8. 默认 thinking on；简单任务 /effort low；脚本/批量场景考虑 MAX_THINKING_TOKENS=8000     

  **E. 工具产出过滤**                                                                           

  9. （本阶段不开）后续可加 PreToolUse hook 把 npm test / 大日志只留失败行                  

  **F. 监控**                                                                                   

  10. statusLine 显示 context_window.used_percentage + rate_limits.five_hour.used_percentage

  11. 每次会话结束 /usage 一眼

  ---                                                                 

  **12. 建议落盘目录结构（仅建议，本轮不创建）**

  挂在 vault 的 11_系统产品与PRD/ 下新增子目录"Claude Code 官方文档学习包"，不进入

  00_入口与总索引（避免噪声），与"系统产品与 AI 工具"主题对齐：                             

  11_系统产品与PRD/                                                                         

  └── Claude Code 官方文档学习包/                                     

      ├── README.md

      ├── 00_官方文档目录索引_v0.1.md

      ├── 01_上下文与记忆机制总结_v0.1.md                                                   

      ├── 02_日志与transcript机制总结_v0.1.md                                               

      ├── 03_slash命令速查_v0.1.md                                                          

      ├── 04_subagents使用规范_v0.1.md                                                      

      ├── 05_hooks使用规范_v0.1.md                                                          

      ├── 06_statusLine使用规范_v0.1.md                               

      ├── 07_权限与安全红线_v0.1.md                                                         

      ├── 08_token与额度控制规范_v0.1.md                              

      ├── 09_Claude_Code使用手册_v0.1.md          # 三个月生存战的主操作手册                

      ├── 10_待核验问题清单_v0.1.md                                                         

      └── 99_原始素材                                                                       

          └── （选摘片段、URL 与抓取日期，不放原文全量）                                    

  每个文件遵守 vault Markdown 标准（frontmatter、版本号、source_type: reference、confidence:

   medium、关联上下游）。                                                                   

  ---                                                                 

  **13. 待核验问题清单**

  ┌─────┬─────────────────────────────────────┬────────────────┬────────────────────────┐

  │  #  │             待核验事项              │      影响      │        怎么核验        │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │     │                                     │                │ 在会话内键入 /         │   

  │ 1   │ /btw 是否官方命令？官方 commands.md │ 文档准确性     │ 看下拉；或抓           │

  │     │  主表未列                           │                │ interactive-mode.md /  │   

  │     │                                     │                │ 最近 whats-new         │

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤   

  │ 2   │ 订阅用户（Pro/Max）的 /usage        │ 成本判断       │ 抓 costs.md            │   

  │     │ 美元数与实际订阅计费关系            │                │ 完整版与官方账单页     │

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤   

  │ 3   │ Skill 在 /compact                   │ 长会话 skill   │ 抓 skills 文档         │   

  │     │ 后保留规则中的"已调用过"判定窗口    │ 失效           │                        │

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤   

  │     │ Auto memory 跨 worktree 行为（同    │ 我们后续可能用 │ 抓 memory.md 节选验证  │

  │ 4   │ repo 共享是否真是严格按 git         │  worktree      │ + 实测                 │   

  │     │ 仓库根派生）                        │                │                        │

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤   

  │     │ Checkpointing 是否覆盖纯 markdown   │                │                        │

  │ 5   │ 写入（/rewind 能否回滚 vault md     │ 防误删         │ 抓 checkpointing.md    │   

  │     │ 改动）                              │                │                        │

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤   

  │ 6   │ agent-memory 与主 auto memory       │ 子代理记忆体系 │ 抓 sub-agents.md       │

  │     │ 协作边界                            │                │ 完整版                 │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │ 7   │ claudeMdExcludes 在多人 vault       │ 长期治理       │ 抓 memory.md exclude   │   

  │     │ 跨设备时的实际行为                  │                │ 段                     │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │ 8   │ ENABLE_TOOL_SEARCH=auto/false       │ 上下文成本     │ 抓 mcp.md              │   

  │     │ 实际触发阈值与对 MCP 的影响         │                │                        │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │ 9   │ --agents JSON 注入是否在 Claude     │ 跨平台一致性   │ 抓 platforms.md /      │   

  │     │ Code 桌面/Web 都支持                │                │ desktop.md             │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │ 10  │ Hook 类型 agent / prompt 的 token   │ 成本归因       │ 抓 hooks.md 完整版     │   

  │     │ 计费归属（主会话 vs 子代理）        │                │                        │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │ 11  │ disable-model-invocation: true 的   │ skill          │ 抓 skills.md           │   

  │     │ skill 在 /compact 后的行为          │ 触发可控性     │                        │   

  ├─────┼─────────────────────────────────────┼────────────────┼────────────────────────┤

  │ 12  │ routines / scheduled-tasks          │ 成本守护       │ 抓两页                 │   

  │     │ 是否会在我们机器上消耗常驻额度      │                │                        │   

  └─────┴─────────────────────────────────────┴────────────────┴────────────────────────┘

  ---                                                                 

  **14. Claude 深度思考与独立意见**

  **14.1 工程化角度**

  最值得**先固化**（按价值/风险比从高到低）：                                                   

  1. **CLAUDE.md →** **.claude/rules/** **拆分**（最高优先）：当前 567 行 CLAUDE.md 每会话都吃          

  token，且按官方文档"长 CLAUDE.md 降低遵从率"。拆分后既省钱、又让"陈列规则"只在改陈列时加载

  、"反幻觉规则"全局加载，结构更工程化。                                                    

  2. **statusLine 显示 5 小时/7 天额度**：单点投入低，对三个月生存战的额度感知效率提升大。

  3. **Permissions 三段（deny/ask/allow）轻量配置**：deny: Edit(/99_归档/**) 与                 

  Edit(./CLAUDE.md) 是治理硬约束，应该在写代码层面就拦住。                                  

  4. **transcript 落盘机制 + 月度蒸馏 SOP**：transcript                                         

  已经在产生，只是没有"复盘机制"，建立后即可反哺 15_刻意练习与成长/。                       

  **14.2 现在不应该配置**                                                                       

  - **Hooks**：风险密度高（凭据/注入/旁路），三个月生存战内"省                                  

  token"价值不抵学习成本和失误代价。先只读不开。                      

  - **Agent teams**：约 7× token，与"省额度"直接冲突。                                          

  - **MCP 多服务器**：本 vault 目前不依赖远程数据源；CLI（gh、本地 Python）足够。               

  - **bypassPermissions**：危险，永远不开（除非将来真要在容器里跑全自动化）。                   

  - **auto** **模式**：尚为研究预览，本阶段稳定性优先。                                             

  **14.3 是否需要建立 Claude Code 使用手册**                                                    

  需要，且建议是"双层"：                                                                    

  - **层 A：操作速查（卡片）** — 一页 markdown，列 §6 命令速查 + §11 token 操作十条 + §10       

  权限红线，挂在 00_入口与总索引/常用模板入口.md 的同级。             

  - **层 B：完整学习包** — 见 §12 的 11_系统产品与PRD/Claude Code 官方文档学习包/。             

  层 A 是日常用，层 B 是查阅。两者关系类似"咨询交付的客户简报 vs 内部白皮书"。              

  **14.4 是否需要 hooks / subagents / commands 三套专项 SOP**                                   

  - **commands SOP**：值得（轻量、零风险、ROI 高）→ 即 §6 + 决策树                              

  - **subagents SOP**：值得（与"商品诊断扫库"等真实任务直接对齐）→ 简版即可

  - **hooks SOP**：**不值得**先做实施型 SOP；先做"规范说明"+"红线列表"防误开（§8 已包含）           

  **14.5 是否需要把 transcript 纳入复盘机制**                                                   

  强烈建议。理由：                                                                          

  - transcript 已经是免费副产品，不沉淀就是浪费                                             

  - 三个月生存战的"刻意练习"需要客观素材，主观回忆有偏差              

  - 落地路径：每月 1 次脚本扫                                                               

  ~/.claude/projects/*/*.jsonl，蒸馏出"高频问题/翻车次数/平均上下文使用率/常用 slash        

  命令分布"，写入 15_刻意练习与成长/月度复盘/`                                              

  需要警惕：jsonl                                                                           

  含敏感内容（粘贴的客户数据、命令输出），蒸馏脚本必须**只产出统计与去标识案例**，不外传原始

  jsonl。                                                                                   

  ---

  **15. 下一步建议**

  **首选 D + 局部 A**：

  - **D（先不写入正式区）**：本轮预览不入库，避免在未核验前污染知识库                           

  - **A 子集（写一份学习包 README + 待核验清单）**：把本响应中的 §1、§3、§13、§14 抽成

  90_素材暂存与待整理/2026-05-04_Claude_Code官方文档学习包预览_v0.1.md，作为后续正式入库的种

  子；正式入 11_系统产品与PRD/Claude Code 官方文档学习包/ 前先核验 §13 清单中至少 5 条

  **不建议 B（一次拆多文件入库）**：未核验先拆易固化错误结论；                                  

  **不建议 C（仅命令速查）**：丢掉 90% 价值，仅留快查表，远低于本次抓取成本对应的产出。

  **配套两个不在本轮范围、待你授权后做的动作**：                                                

  1. 把 CLAUDE.md 的 §4–§16 拆到 .claude/rules/（属于配置变更，本轮约束不动）               

  2. 在 ~/.claude/settings.json 加 statusLine 与最小 permissions（属于 ~/.claude            

  配置变更，本轮约束不动）                                                      

  — 等你点头再执行任一项。

  ---                                                                 

  **Sources**（本轮直接抓取的官方文档页面）：                                                   

  - https://code.claude.com/docs/llms.txt                                                   

  - https://code.claude.com/docs/en/memory.md

  - https://code.claude.com/docs/en/context-window.md                                       

  - https://code.claude.com/docs/en/commands.md                                             

  - https://code.claude.com/docs/en/sub-agents.md                                           

  - https://code.claude.com/docs/en/hooks.md                                                

  - https://code.claude.com/docs/en/statusline.md                                           

  - https://code.claude.com/docs/en/permissions.md                    

  - https://code.claude.com/docs/en/costs.md