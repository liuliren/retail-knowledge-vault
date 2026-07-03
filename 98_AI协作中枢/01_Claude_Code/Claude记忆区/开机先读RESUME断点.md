---
name: startup-read-resume-breakpoint
description: 重新切入时先读 _当前断点_RESUME.md 而非重读全库；收口时覆盖更新它
summary: 开机必读_当前断点_RESUME.md而非重读全库，收口时覆盖更新
metadata:
  node_type: memory
  type: feedback
  originSessionId: 70561fae-3dbf-4468-b6ba-286109bfbf5b
---

六哥的记忆模块缺口已补:**开机/重新切入时,先读 `98_AI协作中枢/00_总控/_当前断点_RESUME.md`**(≤1屏:上次到哪/下一步3条/活跃文件指针/parking lot),**不要重读全库或长历史**。已写入 CLAUDE.md §4 必读首位。

**Why:** 记忆面有8层但散,RESUME 是唯一"开机只读"入口,解决"重切就重读大量信息"的痛点。

**How to apply:** ① 开机读 RESUME 接上下文;② 每次工作收口时**覆盖更新 RESUME**(保持精简,详细历史进事件日志);③ 长会话/compact 前可用 `project-handoff` skill。全图见 `98_/00_总控/记忆与SOP化_系统梳理_v0.1.md`。
