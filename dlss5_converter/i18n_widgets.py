"""Thin PySide wrappers that localize visible client text."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox as _QCheckBox,
    QComboBox as _QComboBox,
    QDialog as _QDialog,
    QFileDialog as _QFileDialog,
    QGroupBox as _QGroupBox,
    QLabel as _QLabel,
    QListWidget as _QListWidget,
    QMainWindow as _QMainWindow,
    QMessageBox as _QMessageBox,
    QProgressBar as _QProgressBar,
    QProgressDialog as _QProgressDialog,
    QPushButton as _QPushButton,
    QStatusBar as _QStatusBar,
    QSpinBox as _QSpinBox,
    QTabWidget as _QTabWidget,
)

from .i18n import tr


def _translated_args(args):
    values = list(args)
    for index, value in enumerate(values):
        if isinstance(value, str):
            values[index] = tr(value)
    return tuple(values)


class _TextMixin:
    def setText(self, text):  # noqa: N802
        return super().setText(tr(text))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QLabel(_TextMixin, _QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*_translated_args(args), **kwargs)


class QPushButton(_TextMixin, _QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*_translated_args(args), **kwargs)


class QCheckBox(_TextMixin, _QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*_translated_args(args), **kwargs)


class QGroupBox(_QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*_translated_args(args), **kwargs)

    def setTitle(self, title):  # noqa: N802
        return super().setTitle(tr(title))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QDialog(_QDialog):
    def setWindowTitle(self, title):  # noqa: N802
        return super().setWindowTitle(tr(title))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QStatusBar(_QStatusBar):
    def showMessage(self, message, timeout=0):  # noqa: N802
        return super().showMessage(tr(message), timeout)


class QMainWindow(_QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Install a localized status bar once. Existing app code can keep calling
        # self.statusBar().showMessage(...) with canonical English strings.
        super().setStatusBar(QStatusBar(self))

    def setWindowTitle(self, title):  # noqa: N802
        return super().setWindowTitle(tr(title))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QListWidget(_QListWidget):
    def addItem(self, item):  # noqa: N802
        if isinstance(item, str):
            item = tr(item)
        return super().addItem(item)


class QProgressBar(_QProgressBar):
    def setFormat(self, text):  # noqa: N802
        return super().setFormat(tr(text))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QSpinBox(_QSpinBox):
    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))

    def wheelEvent(self, event):  # noqa: N802
        # In a scrolling sidebar the wheel is navigation, not an edit gesture.
        # Ignore here so the parent QScrollArea receives it instead of silently
        # changing a value and triggering an expensive neural re-run.
        event.ignore()


class QComboBox(_QComboBox):
    def wheelEvent(self, event):  # noqa: N802
        # Prevent accidental selection changes while scrolling the sidebar.
        event.ignore()

    def addItem(self, *args, **kwargs):  # noqa: N802
        values = list(args)
        for index, value in enumerate(values):
            if isinstance(value, str):
                values[index] = tr(value)
                break
        return super().addItem(*values, **kwargs)

    def addItems(self, texts):  # noqa: N802
        return super().addItems([tr(text) for text in texts])

    def setItemText(self, index, text):  # noqa: N802
        return super().setItemText(index, tr(text))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QTabWidget(_QTabWidget):
    def addTab(self, *args):  # noqa: N802
        values = list(args)
        if values and isinstance(values[-1], str):
            values[-1] = tr(values[-1])
        return super().addTab(*values)

    def setTabText(self, index, text):  # noqa: N802
        return super().setTabText(index, tr(text))

    def setToolTip(self, text):  # noqa: N802
        return super().setToolTip(tr(text))


class QMessageBox(_QMessageBox):
    def __init__(self, *args, **kwargs):
        values = list(args)
        if len(values) >= 3 and isinstance(values[1], str) and isinstance(values[2], str):
            values[1] = tr(values[1])
            values[2] = tr(values[2])
        super().__init__(*values, **kwargs)

    def setWindowTitle(self, title):  # noqa: N802
        return super().setWindowTitle(tr(title))

    def setText(self, text):  # noqa: N802
        return super().setText(tr(text))

    def setInformativeText(self, text):  # noqa: N802
        return super().setInformativeText(tr(text))

    def setDetailedText(self, text):  # noqa: N802
        return super().setDetailedText(tr(text))

    def addButton(self, button, role=None):  # noqa: N802
        if isinstance(button, str):
            return super().addButton(tr(button), role)
        if role is None:
            return super().addButton(button)
        return super().addButton(button, role)

    @staticmethod
    def information(parent, title, text, *args, **kwargs):
        return _QMessageBox.information(parent, tr(title), tr(text), *args, **kwargs)

    @staticmethod
    def warning(parent, title, text, *args, **kwargs):
        return _QMessageBox.warning(parent, tr(title), tr(text), *args, **kwargs)

    @staticmethod
    def critical(parent, title, text, *args, **kwargs):
        return _QMessageBox.critical(parent, tr(title), tr(text), *args, **kwargs)

    @staticmethod
    def question(parent, title, text, *args, **kwargs):
        return _QMessageBox.question(parent, tr(title), tr(text), *args, **kwargs)


class QFileDialog(_QFileDialog):
    @staticmethod
    def getOpenFileName(parent=None, caption="", directory="", filter="", *args, **kwargs):
        return _QFileDialog.getOpenFileName(parent, tr(caption), directory, filter, *args, **kwargs)

    @staticmethod
    def getOpenFileNames(parent=None, caption="", directory="", filter="", *args, **kwargs):
        return _QFileDialog.getOpenFileNames(parent, tr(caption), directory, filter, *args, **kwargs)

    @staticmethod
    def getSaveFileName(parent=None, caption="", directory="", filter="", *args, **kwargs):
        return _QFileDialog.getSaveFileName(parent, tr(caption), directory, filter, *args, **kwargs)

    @staticmethod
    def getExistingDirectory(parent=None, caption="", directory="", *args, **kwargs):
        return _QFileDialog.getExistingDirectory(parent, tr(caption), directory, *args, **kwargs)


class QProgressDialog(_QProgressDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*_translated_args(args), **kwargs)

    def setLabelText(self, text):  # noqa: N802
        return super().setLabelText(tr(text))

    def setCancelButtonText(self, text):  # noqa: N802
        return super().setCancelButtonText(tr(text))

    def setWindowTitle(self, title):  # noqa: N802
        return super().setWindowTitle(tr(title))
