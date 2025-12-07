# 文档导航地图

## 🗺️ 我应该看哪个文档？

### 场景1：我是AI Agent，要生成3D模型

```
开始 → docs/ai/ai_agent_prompt.md （系统提示词）
  ↓
需要查API → docs/ai/api_quick_reference.md （速查表）
```

**只看这2个文档就够了！**

---

### 场景2：我是开发者，第一次使用

```
开始 → docs/dev/usage_guide.md （使用教程）
  ↓
看示例 → examples/new_api_demo.py
  ↓
遇到问题 → docs/ai/api_quick_reference.md （速查表）
```

---

### 场景3：我是开发者，想扩展功能

```
添加节点组？
  → docs/dev/node_group_specifications.md

添加组合模板？
  → docs/dev/api_improvements.md （先看设计原理）
  → src/gnodes_builder/templates.py （模仿现有代码）

修改API？
  → docs/dev/api_priority_guide.md （理解优先级设计）
```

---

### 场景4：我是AI Agent开发者，要配置提示词

```
主提示词 → docs/ai/ai_agent_prompt.md
  ↓
理解为什么这样设计 → docs/dev/api_improvements.md
  ↓
理解优先级规则 → docs/dev/api_priority_guide.md
```

---

## 📋 文档功能速查

| 文档 | 面向 | 内容 | 何时看 |
|-----|------|------|--------|
| [ai/ai_agent_prompt.md](ai/ai_agent_prompt.md) | AI | 系统提示词 | AI配置必读 |
| [ai/api_quick_reference.md](ai/api_quick_reference.md) | AI/Dev | API速查 | 不知道用哪个API |
| [dev/usage_guide.md](dev/usage_guide.md) | Dev | 使用教程 | 首次使用 |
| [dev/api_improvements.md](dev/api_improvements.md) | Dev | 设计说明 | 理解设计原理 |
| [dev/api_priority_guide.md](dev/api_priority_guide.md) | Dev | 优先级指南 | 扩展API时参考 |
| [dev/node_group_specifications.md](dev/node_group_specifications.md) | Dev | 节点组规范 | 添加节点组 |
| [dev/feasibility_analysis.md](dev/feasibility_analysis.md) | Dev | 可行性分析 | 了解技术选型 |

---

## 🎯 典型问题 → 文档映射

| 问题 | 答案在这里 |
|-----|-----------|
| AI该用哪个API？ | [ai/api_quick_reference.md](ai/api_quick_reference.md) 决策表 |
| 椅子朝向怎么算？ | [ai/api_quick_reference.md](ai/api_quick_reference.md) 禁止模式 |
| 怎么创建门框？ | [ai/ai_agent_prompt.md](ai/ai_agent_prompt.md) 任务示例 |
| 为什么要语义化API？ | [dev/api_improvements.md](dev/api_improvements.md) 问题背景 |
| 怎么添加新节点组？ | [dev/node_group_specifications.md](dev/node_group_specifications.md) |
| 工具适合做什么？ | [dev/feasibility_analysis.md](dev/feasibility_analysis.md) |

---

## 📊 文档依赖关系

```
AI Agent 阅读路径：
ai_agent_prompt.md ─→ api_quick_reference.md
        ↑
        │ (配置时参考)
        │
   api_improvements.md (开发者理解设计)

开发者阅读路径：
usage_guide.md ─→ api_quick_reference.md
     ↓
api_improvements.md ─→ api_priority_guide.md
     ↓
node_group_specifications.md
```

---

## ⚡ 速查：常见任务

| 任务 | 文档 | 位置 |
|-----|------|------|
| 配置AI Agent | ai/ai_agent_prompt.md | 全文 |
| 创建椅子 | ai/ai_agent_prompt.md | 任务5 |
| 创建栅栏 | ai/ai_agent_prompt.md | 任务6 |
| API优先级 | ai/api_quick_reference.md | 决策表 |
| 禁止模式 | ai/ai_agent_prompt.md | 禁止模式章节 |
| 设计原理 | dev/api_improvements.md | 解决方案章节 |

