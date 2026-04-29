# 微信公众号运营助手

这是一个本地命令行技能，用于协助 AI CLI 完成微信公众号素材上传、模板渲染、公众号 HTML 排版、草稿创建、发布、菜单、用户和数据统计。

## 安装

```bash
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，填入公众号凭证。

## 常用命令

```bash
python bin/wechat --help
python bin/wechat template list
python bin/wechat template render weekly_report --var title="AI 周报"
python bin/wechat convert --file article.md --theme modern > article.html
python bin/wechat image generate --prompt "一张科技感公众号封面，蓝紫渐变，抽象 AI 芯片" --filename cover.png
python bin/wechat image cover --prompt "一张科技感公众号封面，蓝紫渐变，抽象 AI 芯片"
python bin/wechat image illustrate --file article.md --max-images 3 --upload
python bin/wechat upload image --file cover.png
python bin/wechat draft create --title "AI 周报" --content-file article_illustrated.md --cover-media-id MEDIA_ID
```

## 图片生成配置

图片生成接口兼容 OpenAI `/images/generations` 响应格式，支持返回 `url` 或 `b64_json`。

```env
IMAGE_API_BASE_URL=https://api.openai.com/v1
IMAGE_API_ENDPOINT=/images/generations
IMAGE_API_KEY=your_openai_compatible_api_key
IMAGE_MODEL=gpt-image-1
IMAGE_SIZE=1024x1024
IMAGE_RESPONSE_FORMAT=
IMAGE_API_EXTRA_JSON=
```

- `image generate`：只生成图片到本地 `generated_images/`。
- `image cover`：生成图片后自动上传到微信素材库，返回 `media_id`，可直接用于 `draft create`。
- `image illustrate`：读取 Markdown 文章，按二级/三级标题提取正文段落，自动生成插图并插入到新 Markdown；加 `--upload` 会先上传微信素材库，再插入微信图片 URL。

## 离线可用能力

未配置 `.env` 时仍可使用：

- `template list`
- `template show`
- `template render`
- `convert`

需要微信凭证的能力：

- 素材上传
- 草稿创建/查询/发布
- 菜单管理
- 用户管理
- 数据统计

需要图片 API 凭证的能力：

- AI 图片生成
- AI 封面生成并上传
