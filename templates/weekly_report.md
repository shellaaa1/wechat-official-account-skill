---
name: 周报模板
category: 汇报总结
theme: clean
style: report
materials: [banner, icon, divider]
variables:
  - name: title
    desc: 文章标题
    default: "本周工作复盘"
  - name: date_range
    desc: 日期范围
    default: "2026.04.22 - 2026.04.28"
  - name: progress
    desc: 本周进展
    default: "完成核心功能开发，并打通关键验证链路。"
  - name: result
    desc: 结果数据
    default: "主要流程已完成本地验证，关键问题已修复。"
  - name: risk
    desc: 风险与问题
    default: "后续需要继续完善异常处理、字段校验和使用文档。"
  - name: plan
    desc: 下周计划
    default: "补充自动化测试，完善模板和素材库。"
  - name: author
    desc: 署名
    default: "AI助手"
---

![周报横幅]({{ material_banner }})

# {{ title }}

**时间**：{{ date_range }}

![周报图标]({{ material_icon }})

## 01 本周核心进展

{{ progress }}

## 02 关键结果

{{ result }}

![分隔图]({{ material_divider }})

## 03 风险与问题

{{ risk }}

## 04 下周计划

{{ plan }}

---
*本文由 {{ author }} 通过 Qwen CLI 生成*
