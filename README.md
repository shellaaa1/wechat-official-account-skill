# 微信公众号运营助手

一个本地命令行工具，用于辅助完成公众号文章写作、自动配图、排版、素材上传、草稿创建、发布、菜单管理、用户管理和数据统计。

## 功能特性

- 📝 **模板渲染**：8 种内置模板，快速生成文章框架
- 🎨 **自动素材**：根据标签自动匹配本地素材库
- 🖼️ AI 图片生成：支持 OpenAI 兼容接口，自动生成封面和插图
- 📤 **素材上传**：一键上传图片到微信素材库
- 📋 **草稿管理**：创建、查询、删除、发布草稿
- 🎯 **菜单管理**：自定义公众号菜单
- 👥 **用户管理**：查看用户列表、设置备注
- 📊 **数据统计**：获取图文分析数据

## 快速开始

### 安装依赖

```bash
cd wechat-official-account-skill
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
# 微信公众号配置（必填）
WECHAT_APP_ID=你的公众号AppID
WECHAT_APP_SECRET=你的公众号AppSecret

# 图片生成 API 配置
IMAGE_API_BASE_URL=https://api.openai.com/v1
IMAGE_API_KEY=你的API密钥
IMAGE_MODEL=gpt-image-1
```

### 测试连接

```bash
# 测试微信 API
python bin/wechat draft list --count 1

# 测试图片生成
python bin/wechat image generate --prompt "一张科技感封面图"
```

## 常用命令

```bash
# 查看帮助
python bin/wechat --help

# 模板操作
python bin/wechat template list              # 查看所有模板
python bin/wechat template show tech_article # 查看模板详情
python bin/wechat template render tech_article --var title="标题" --output article.md

# 图片生成
python bin/wechat image generate --prompt "提示词" --filename cover.png
python bin/wechat image cover --prompt "封面提示词"              # 生成并上传封面
python bin/wechat image illustrate --file article.md --upload   # 根据文章生成插图

# 素材上传
python bin/wechat upload image --file cover.png

# 草稿管理
python bin/wechat draft create --title "标题" --content-file article.md --cover-media-id MEDIA_ID
python bin/wechat draft list --count 10
python bin/wechat draft publish DRAFT_MEDIA_ID

# 菜单管理
python bin/wechat menu get
python bin/wechat menu create --file menu.json

# 用户管理
python bin/wechat user list
python bin/wechat user info OPENID

# 数据统计
python bin/wechat stats article --begin 2026-04-01 --end 2026-04-30
```

## 内置模板

| 模板 ID | 名称 | 适用场景 |
|---------|------|----------|
| `weekly_report` | 周报模板 | 工作总结、项目进展 |
| `tech_article` | 技术文章 | 技术实践、经验分享 |
| `product_launch` | 产品发布 | 功能上线、新品发布 |
| `free_style` | 自由写作 | 随笔、观点、短文 |
| `developer_deep_dive` | 技术深度文 | 架构拆解、深度复盘 |
| `industry_observation` | 热点解读 | 行业趋势、热点分析 |
| `tutorial_guide` | 教程指南 | 步骤教程、操作指南 |
| `business_case` | 商业案例 | 增长案例、产品分析 |

## 完整工作流示例

```bash
# 1. 使用模板生成文章
python bin/wechat template render tech_article \
  --var title="从模板到素材：公众号自动排版实践" \
  --output articles/my_article.md

# 2. 生成正文插图
python bin/wechat image illustrate \
  --file articles/my_article.md \
  --max-images 3 \
  --upload

# 3. 生成封面
python bin/wechat image cover \
  --prompt "公众号封面，科技感，蓝紫渐变，无文字"

# 4. 创建草稿（使用返回的 media_id）
python bin/wechat draft create \
  --title "从模板到素材：公众号自动排版实践" \
  --content-file articles/my_article_illustrated.md \
  --cover-media-id MEDIA_ID \
  --author "AI助手"

# 5. 确认无误后发布
python bin/wechat draft publish DRAFT_MEDIA_ID
```

## 素材库结构

```
assets/library/
├── backgrounds/   # 背景素材
├── banners/       # 横幅图片
├── covers/        # 封面图
├── dividers/      # 分隔图
├── icons/         # 图标
├── illustrations/ # 插图
└── index.yaml     # 素材索引
```

## 离线可用

未配置微信凭证时，以下功能仍可使用：

- 模板列表和详情查看
- 模板渲染生成 Markdown
- Markdown 转 HTML

## 安全提醒

1. ⚠️ 不要将 `.env` 文件提交到版本控制
2. ⚠️ 不要在聊天中泄露 `WECHAT_APP_SECRET` 和 `IMAGE_API_KEY`
3. ⚠️ 发布文章前务必人工审核内容
4. ⚠️ 删除草稿、发布草稿属于高风险操作

## 文档

- [使用文档](docs/使用文档.md) - 详细使用说明
- [开发文档](docs/开发文档.md) - 开发者指南

## 许可证

MIT License
