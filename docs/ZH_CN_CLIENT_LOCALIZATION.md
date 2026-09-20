# 简体中文客户端实现说明

当前成品代码位于 `main`；实现历史保留在 `i18n/zh-cn`。

本实现基于上游 v0.3.3 客户端代码，对 **DLSS5 Image Converter 的客户端界面**进行了简体中文本地化，并补充了与中文客户端实际使用直接相关的少量交互修正。

## 范围

本分支只处理客户端。

已处理：

- 主界面与单张图片工作流
- 视频页面
- 图像序列页面
- Effects 页面
- 设置页面
- 首次运行与教程
- DLSS 运行环境检查与诊断信息
- 风格对比界面
- 导出、保存、批处理与进度状态
- HDR / 显示相关说明
- Tooltip / 鼠标悬停说明
- 动态状态文字与带参数的运行时文案

未处理：

- README 翻译
- TROUBLESHOOTING 翻译
- 原生 DLSS / NGX / RenoDX 渲染逻辑
- `native/` 中的核心处理流程

## 本地化实现

### 1. 非破坏式 i18n

英文源码仍然作为客户端的 canonical source，没有把上游 UI 字符串直接替换成中文。

新增：

- `dlss5_converter/i18n.py`
- `dlss5_converter/i18n_widgets.py`
- `dlss5_converter/assets/locales/zh_CN.json`

客户端继续可以保留类似：

```python
QPushButton("Check runtime")
```

运行时通过本地化层显示为：

```text
检查运行环境
```

如果某条英文没有对应中文翻译，会自动回退到英文，不会显示空字符串或阻止客户端启动。

### 2. 简中词库

当前 `zh_CN.json` 包含 **494 条客户端翻译词条**。

词条包括：

- 固定按钮与标签
- 窗口标题
- Tooltip
- 对话框
- 运行环境错误信息
- 进度与状态文字
- 带占位符的动态文本
- 风格、HDR、深度、导出与细节恢复说明

技术文件名、错误码和必要的技术缩写保持原样，例如：

- `nvngx_dlss.dll`
- `nvngx_dlssnr.dll`
- RenoDX
- ReShade
- DLSS / DLAA
- NGX

### 3. 动态文本翻译

本地化层支持带占位符的动态文字，包括原源码中的 f-string 形式。

例如运行时产生：

```text
2 folder(s) found, 1 with all four. The best is selected.
```

可以匹配并显示对应中文，而不要求为了翻译去重写业务逻辑。

### 4. Qt 客户端包装层

`i18n_widgets.py` 对常见 PySide6 控件增加了显示时翻译，包括：

- QLabel
- QPushButton
- QCheckBox
- QGroupBox
- QDialog
- QMainWindow
- QComboBox
- QTabWidget
- QMessageBox
- QFileDialog
- QProgressDialog
- QProgressBar
- QSpinBox
- QStatusBar
- QListWidget

项目自定义控件中的 Tooltip、紧凑参数按钮、图像说明文字等也接入了同一翻译层。

### 5. 语言设置

`AppSettings` 新增 `language` 设置。

当前支持：

- English
- 简体中文

设置会写入原有配置系统并持久化。

简中分支默认使用 `zh_CN`，英文仍可在客户端设置中选择。

### 6. 打包兼容

简中词库位于：

```text
dlss5_converter/assets/locales/zh_CN.json
```

这样可以复用项目已有的 assets 打包规则，不需要修改原有 PyInstaller release pipeline 才能把语言资源带入客户端。

## 客户端交互修正

本分支同时包含两项实际使用中发现的客户端交互修正。

### 滚轮不再误改参数

在右侧滚动区域中，鼠标滚轮现在只用于页面滚动。

滚轮不会再意外修改：

- Slider
- SpinBox
- ComboBox

因此不会因为正常上下滚动页面而改变神经参数并触发昂贵的重新处理。

### 风格对比中的冗余重算

在“对比风格”视图中，切换右侧当前活动风格只用于决定之后普通转换或批处理使用哪个 NRStyle。

该操作不再无意义地重新计算已经生成的全部风格对比结果。

## 测试与检查

新增：

- `tests/test_i18n.py`
- `scripts/check_i18n.py`
- `.github/workflows/i18n-check.yml`

检查内容包括：

- 简中固定词条翻译
- 缺失翻译自动回退英文
- 动态占位符翻译
- 英文 canonical source 行为
- Python 语法检查
- 客户端翻译覆盖扫描

GitHub Actions 工作流名称：

```text
i18n client checks
```

其中翻译覆盖扫描为阻断检查：静态扫描器检测到客户端可见字符串缺少简中词条时会返回非零状态。最终合并前的客户端 i18n workflow 已通过。

## 主要文件

```text
dlss5_converter/
├─ app.py
├─ settings.py
├─ widgets.py
├─ onboarding.py
├─ i18n.py
├─ i18n_widgets.py
└─ assets/
   └─ locales/
      └─ zh_CN.json

scripts/
└─ check_i18n.py

tests/
└─ test_i18n.py

.github/
└─ workflows/
   └─ i18n-check.yml
```

## 本地源码运行

客户端使用 Python 3.12。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\scripts\run.ps1
```

运行翻译测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_i18n.py
```

运行客户端翻译覆盖检查：

```powershell
.\.venv\Scripts\python.exe scripts\check_i18n.py
```
