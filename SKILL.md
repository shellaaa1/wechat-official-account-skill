# 微信公众号运营助手

你已获得微信公众号管理能力。可通过运行 `python bin/wechat <command>` 完成以下操作。

## 命令速查

| 需求 | 命令 |
|------|------|
| 查看可用模板 | `python bin/wechat template list` |
| 查看模板详情 | `python bin/wechat template show <name>` |
| 渲染模板生成草稿 | `python bin/wechat template render <name> --var title="标题"` |
| 将 Markdown 转为公众号 HTML | `python bin/wechat convert --file <md> --theme modern` |
| 上传图片 | `python bin/wechat upload image --file <path>` |
| 生成图片 | `python bin/wechat image generate --prompt "封面提示词"` |
| 生成并上传封面 | `python bin/wechat image cover --prompt "公众号封面提示词"` |
| 根据文章生成插图 | `python bin/wechat image illustrate --file article.md --upload` |
| 创建草稿 | `python bin/wechat draft create --title ... --content-file ... --cover-media-id ...` |
| 查询草稿 | `python bin/wechat draft list` |
| 发布草稿 | `python bin/wechat draft publish <draft_media_id>` |
| 设置菜单 | `python bin/wechat menu create --file menu.json` |
| 查看粉丝 | `python bin/wechat user list` |
| 获取数据报告 | `python bin/wechat stats article --begin 2026-04-01 --end 2026-04-28` |

## 工作流示例

当用户说“用周报模板发一篇本周进度”时：

1. 调用 `template list` 确认模板名称。
2. 向用户询问缺失变量值，如标题、进度、计划、作者。
3. 调用 `template render` 生成 Markdown。
4. 根据文章内容判断是否需要正文插图；需要时调用 `image illustrate --file <md> --upload`，生成带插图的新 Markdown。
5. 如用户没有提供封面图，可根据文章主题调用 `image cover --prompt "..."` 生成并上传封面，得到 `media_id`。
6. 如用户已提供本地图片，调用 `upload image` 上传封面图，得到 `media_id`。
7. 执行 `draft create` 创建草稿；如果已生成插图，`--content-file` 应使用 `*_illustrated.md`。
8. 用户确认后再调用 `draft publish` 发布。
9. 返回发布结果。

## 注意事项

- 真实微信 API 操作前需确保 `.env` 已正确配置。
- 使用 AI 图片生成前需配置 `IMAGE_API_KEY`，兼容 OpenAI `/images/generations` 格式的接口可通过 `IMAGE_API_BASE_URL` 切换。
- 不要输出 `.env` 中的 `WECHAT_APP_SECRET` 或 `IMAGE_API_KEY`。
- 图片必须上传到微信后才能作为封面或正文稳定使用。
- 变量值包含特殊 shell 字符时要正确加引号。
