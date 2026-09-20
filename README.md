# DLSS5-Image-Converter-zh-CN

[criso2hd-alt/DLSS5-Image-Converter](https://github.com/criso2hd-alt/DLSS5-Image-Converter) 的简体中文客户端本地化 fork。

本仓库在保留英文源码作为 canonical source 的前提下，为客户端增加了非破坏式简体中文 i18n。中文文本独立存放在语言资源中，缺失翻译自动回退英文，尽量降低与上游代码结构的冲突。

## 本 fork 做了什么

- 客户端简体中文本地化
  - 主界面与单张图片工作流
  - 视频与图像序列
  - Effects 与设置
  - 首次运行与教程
  - DLSS 运行环境检查与诊断
  - 风格对比
  - 导出、保存、批处理与进度状态
  - HDR / 显示相关说明
  - Tooltip / 鼠标悬停说明
  - 动态状态文字与带参数的运行时文案
- 新增语言设置：English / 简体中文
- 新增缺失翻译英文 fallback
- 新增动态文本模板翻译
- 新增客户端 i18n 单元测试与覆盖检查
- 修正右侧滚动区域中滚轮误改 Slider / SpinBox / ComboBox 参数的问题
- 减少“对比风格”视图中切换当前活动风格造成的冗余重算

当前简中词库：**478 条**。

详细实现记录见：[docs/ZH_CN_CLIENT_LOCALIZATION.md](docs/ZH_CN_CLIENT_LOCALIZATION.md)

## 与上游的关系

DLSS / NGX / RenoDX 核心处理逻辑与 `native/` 核心流程保持上游实现。本 fork 的主要改动集中在客户端本地化和少量 UI 交互修正。

原项目的功能说明、运行原理、依赖要求与完整文档请以 upstream 为准：

- [Upstream repository](https://github.com/criso2hd-alt/DLSS5-Image-Converter)
- [Upstream README](https://github.com/criso2hd-alt/DLSS5-Image-Converter/blob/main/README.md)
- [Upstream troubleshooting](https://github.com/criso2hd-alt/DLSS5-Image-Converter/blob/main/TROUBLESHOOTING.md)

## 从源码运行

要求 Python 3.12。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\scripts\run.ps1
```

运行 i18n 测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_i18n.py
.\.venv\Scripts\python.exe scripts\check_i18n.py
```

## License

本仓库保留上游的自定义 source-available `LICENSE`。请以仓库根目录的 [LICENSE](LICENSE) 为准。

该许可允许通过 GitHub 的原生 fork 机制查看和维护源码 fork，但禁止重新分发软件，包括打包后的构建、修改版下载、镜像、repack 或 installer。本仓库不提供 portable / 预编译发行包。
