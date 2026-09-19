from dlss5_converter import i18n


def test_zh_cn_exact_translation():
    i18n.set_language("zh_CN")
    assert i18n.tr("Check runtime") == "检查运行环境"


def test_missing_translation_falls_back_to_english():
    i18n.set_language("zh_CN")
    source = "A newly added upstream string"
    assert i18n.tr(source) == source


def test_template_translation():
    i18n.set_language("zh_CN")
    assert i18n.tr("Could not check the runtime: boom") == "无法检查运行环境：boom"


def test_english_is_canonical_source():
    i18n.set_language("en")
    assert i18n.tr("Check runtime") == "Check runtime"


def test_expression_template_translation():
    i18n.set_language("zh_CN")
    source = "2 folder(s) found, 1 with all four. The best is selected."
    assert i18n.tr(source) == "找到 2 个文件夹，其中 1 个包含全部四个文件。已自动选择最佳匹配。"
