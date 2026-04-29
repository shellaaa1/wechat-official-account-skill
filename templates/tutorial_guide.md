---
name: 教程指南
theme: clean
style: tutorial
category: 教程指南
materials: [banner, icon, divider]
variables:
  - name: title
    desc: 教程标题
    default: "从 0 到 1 完成一个实用工作流"
  - name: goal
    desc: 学完目标
    default: "读完本文后，你可以独立完成配置、运行和验证。"
  - name: step_one
    desc: 第一步
    default: "准备环境和必要配置，确认命令可以正常执行。"
  - name: step_two
    desc: 第二步
    default: "创建输入文件，并按模板组织内容。"
  - name: step_three
    desc: 第三步
    default: "运行核心命令，检查输出结果。"
  - name: check
    desc: 检查项
    default: "确认没有报错，输出文件存在，结果符合预期。"
---

![教程横幅]({{ material_banner }})

# {{ title }}

> {{ goal }}

## 准备工作

![教程图标]({{ material_icon }})

在开始之前，先确认你已经准备好运行环境、配置文件和输入内容。

## 步骤 1：准备环境

{{ step_one }}

## 步骤 2：组织内容

{{ step_two }}

## 步骤 3：运行并验证

{{ step_three }}

![分隔图]({{ material_divider }})

## 检查清单

- {{ check }}
- 确认关键配置没有泄露。
- 如果结果异常，优先查看命令输出和本地文件。

## 小结

教程最重要的不是把步骤写多，而是让读者每一步都知道自己在做什么、为什么做、做完如何确认。
