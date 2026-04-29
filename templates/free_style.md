---
name: 自由写作
category: 通用
theme: minimal
style: essay
materials: [icon, divider]
variables:
  - name: title
    desc: 标题
    default: "写给正在变化的日常"
  - name: lead
    desc: 开头
    default: "很多变化并不是突然发生的，而是在一次次微小选择中慢慢成形。"
  - name: body
    desc: 正文
    default: "在这里写下你的观察、感受和判断。"
  - name: ending
    desc: 结尾
    default: "真正重要的，是在变化中保留判断力，也保留继续行动的能力。"
---

# {{ title }}

![文章图标]({{ material_icon }})

{{ lead }}

## 正文

{{ body }}

![分隔图]({{ material_divider }})

## 最后

{{ ending }}
