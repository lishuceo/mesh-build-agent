# 开发者文档

这个目录包含**给人类开发者看的**技术文档。

## 📚 文档列表

### 1. [usage_guide.md](usage_guide.md) ⭐ 使用教程
**用途**：完整的工具使用指南

**包含内容**：
- 快速开始
- 三种使用方式对比（Level 1/2/3）
- 选择决策树
- 常见场景最佳实践
- 调试技巧
- 性能建议
- 常见错误

**适合**：第一次使用本工具的开发者

---

### 2. [api_improvements.md](api_improvements.md) ⭐ 设计说明
**用途**：解释为什么要添加语义化API和组合模板

**包含内容**：
- 问题背景（椅子旋转错误的case）
- 解决方案设计
- API设计原则
- 效果对比（70行 vs 1行）

**适合**：想理解设计思路的开发者

---

### 3. [api_priority_guide.md](api_priority_guide.md)
**用途**：详细的API优先级说明

**包含内容**：
- API重复问题分析
- 优先级规则
- 决策树
- 使用建议

**适合**：扩展API时参考

---

### 4. [node_group_specifications.md](node_group_specifications.md)
**用途**：节点组设计规范

**包含内容**：
- S.I.O 协议定义
- 节点组命名规范
- 接口设计标准

**适合**：添加新节点组时参考

---

### 5. [feasibility_analysis.md](feasibility_analysis.md)
**用途**：方案可行性分析

**包含内容**：
- 技术方案选型
- 优劣势分析
- 对比其他方案

**适合**：了解项目背景

---

## 🔧 开发者常见任务

### 任务1：添加新节点组

1. 阅读 `node_group_specifications.md`
2. 在 `scripts/create_node_library.py` 中添加创建函数
3. 更新 `docs/ai/ai_agent_prompt.md` 的节点组列表
4. 重新生成节点库

### 任务2：添加新的组合模板

1. 阅读 `api_improvements.md` 了解设计原则
2. 在 `src/gnodes_builder/templates.py` 中添加函数
3. 更新 `src/gnodes_builder/__init__.py` 导出
4. 更新 `docs/ai/ai_agent_prompt.md` 的模板列表

### 任务3：优化现有API

1. 阅读 `api_priority_guide.md` 了解优先级设计
2. 在 `src/gnodes_builder/builder.py` 中修改
3. 更新文档

---

## 📊 文档结构对比

```
docs/
├── ai/              ← AI Agent 专用（面向使用）
│   ├── README.md
│   ├── ai_agent_prompt.md      (系统提示词)
│   └── api_quick_reference.md  (API速查表)
│
└── dev/             ← 开发者专用（面向开发）
    ├── README.md
    ├── usage_guide.md           (使用教程)
    ├── api_improvements.md      (设计说明)
    ├── api_priority_guide.md    (优先级指南)
    ├── node_group_specifications.md
    └── feasibility_analysis.md
```

---

## 与 AI 文档的区别

| 维度 | AI Agent 文档 | 开发者文档 |
|-----|--------------|-----------|
| 目标读者 | AI | 人类 |
| 内容重点 | 怎么用 | 为什么、怎么改 |
| 风格 | 指令式、列表 | 解释性、分析 |
| 详细度 | 精简、直接 | 详细、有背景 |
| 更新频率 | API变化时 | 设计变化时 |

