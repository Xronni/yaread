import sys
import os
import re
import time
import json
import math
import random
import urllib.request
import urllib.error
import traceback
import bisect
import tempfile

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
    QSlider, QFileDialog, QComboBox, QLineEdit, QLabel, QSpinBox, QSizePolicy, 
    QFrame, QGraphicsDropShadowEffect, QGraphicsView, QGraphicsScene, 
    QGraphicsTextItem, QToolTip, QCheckBox, QDialog, QTextEdit, QMessageBox, 
    QStyleOptionGraphicsItem, QStyle, QSizeGrip, QSplashScreen
)
from PyQt6.QtCore import (
    QTimer, QThread, pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, 
    QPointF, pyqtProperty, QPoint, QSettings, QVariantAnimation
)
from PyQt6.QtGui import (
    QKeySequence, QShortcut, QFont, QColor, QIcon, QPainter, 
    QTransform, QPixmap, QTextCursor, QTextCharFormat, QPen, 
    QPalette, QTextOption, QTextBlockFormat, QLinearGradient, QRadialGradient
)

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        p1 = os.path.join(meipass, relative_path)
        if os.path.exists(p1): return p1
        p2 = os.path.join(os.path.dirname(sys.executable), relative_path)
        if os.path.exists(p2): return p2
        return p1
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

BASE_DIR = get_resource_path("")

try:
    import ctypes
    myappid = "yateam.yaread.app.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        ctypes.c_wchar_p(myappid)
    )
except Exception:
    pass

app = QApplication(sys.argv)
app.setApplicationName("YaRead")
app.setOrganizationName("YaTeam")

icon_path = get_resource_path("icon.ico")
app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

if os.path.exists(icon_path):
    splash_pixmap = app_icon.pixmap(256, 256)
else:
    splash_pixmap = QPixmap(300, 200)
    splash_pixmap.fill(QColor("#181822"))
    p = QPainter(splash_pixmap)
    p.setPen(QColor("#CDD6F4"))
    p.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
    p.drawText(splash_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "YaRead")
    p.end()

splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
splash.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
splash.show()
app.processEvents()

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import fitz

try:
    import ebooklib
    from ebooklib import epub as ebooklib_epub
    from bs4 import BeautifulSoup as _BS
    HAS_EPUB = True
except ImportError:
    HAS_EPUB = False

try:
    from lxml import etree as _lxml_etree
    HAS_FB2 = True
except ImportError:
    HAS_FB2 = False

try:
    from llama_cpp import Llama
    HAS_LLAMA = True
except ImportError:
    HAS_LLAMA = False

def global_exception_handler(exc_type, exc_value, exc_traceback):
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("CRITICAL ERROR:\n", err_msg)
    try:
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(err_msg)
    except:
        pass
    
    if QApplication.instance():
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("YaRead Critical Error")
        msg_box.setText("Произошла критическая ошибка.\nПодробности записаны в crash.log\n\n" + str(exc_value))
        msg_box.setDetailedText(err_msg)
        msg_box.exec()
    sys.exit(1)

sys.excepthook = global_exception_handler

EMOTION_COLORS = {
    0: "#808080", 1: "#A8D0E6", 2: "#F8E9A1", 3: "#FF4B4B", 4: "#C1E1C1",
    5: "#FFB6B9", 6: "#2A363B", 7: "#FFD3B6", 8: "#99B898", 9: "#E84A5F",
    10: "#000000", 11: "#D4A5A5", 12: "#FF847C"
}

LANG_DICT = {
    "en": {
        "btn_yes": "Yes",
        "btn_no": "No",
        "window_title": "YaRead",
        "btn_open": "Open File",
        "btn_close_file": "Close File",
        "btn_play": "Start (Space)",
        "btn_pause": "Pause (Space)",
        "lbl_model": "AI Model:",
        "ai_pause": "Pause AI",
        "btn_lang": "EN",
        "search_ph": "Search in text...",
        "btn_up": "Prev",
        "btn_down": "Next",
        "lbl_search": "Search:",
        "align": "Alignment:",
        "align_center": "Center",
        "align_left": "Left",
        "align_right": "Right",
        "width": "Width:",
        "auto_scroll": "Auto-scroll",
        "speed": "Speed:",
        "volume": "Volume:",
        "status_reading": "[Reading | Emotion:",
        "status_thinking": "[Reading | AI Thinking...]",
        "status_waiting": "[Reading | Waiting for AI...]",
        "status_pause": "[Paused]",
        "status_preloaded": "AI Preloaded:",
        "status_asking": "[Processing AI Request...]",
        "status_ai_paused": "[AI Paused]",
        "err_model": "[Error: Model not found]",
        "ai_loading": "[AI: Initializing...]",
        "ai_ready": "[AI: Ready]",
        "btn_ask_ai": "Ask AI",
        "btn_cancel_ai": "Cancel AI",
        "ask_ai_title": "AI Explanation",
        "btn_reset": "Reset",
        "msg_reset_title": "Reset Settings",
        "msg_reset_text": "Are you sure you want to reset all settings to defaults?",
        "theme_sepia": "Sepia",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "theme_starry": "Starry Night",
        "drag_drop": "Drag & Drop Your File Here",
        "donate_title": "Donate",
        "btn_donate": "Donate 🍪",
        "emotions": {
            0: "Silence (TOC)", 1: "Story", 2: "Suspense", 3: "Action", 
            4: "Resolution", 5: "Romance", 6: "Sadness", 7: "Joy", 
            8: "Mystery", 9: "Chase", 10: "Horror", 11: "Flashback", 12: "Comedy"
        }
    },
    "ru": {
        "btn_yes": "Да",
        "btn_no": "Нет",
        "window_title": "YaRead",
        "btn_open": "Открыть файл",
        "btn_close_file": "Закрыть",
        "btn_play": "Старт (Пробел)",
        "btn_pause": "Пауза (Пробел)",
        "lbl_model": "ИИ:",
        "ai_pause": "Пауза ИИ",
        "btn_lang": "RU",
        "search_ph": "Найти в тексте...",
        "btn_up": "Пред",
        "btn_down": "След",
        "lbl_search": "Поиск:",
        "align": "Выравнивание:",
        "align_center": "По центру",
        "align_left": "Слева",
        "align_right": "Справа",
        "width": "Ширина:",
        "auto_scroll": "Автопрокрутка",
        "speed": "Скорость:",
        "volume": "Громкость:",
        "status_reading": "[Читаем | Эмоция:",
        "status_thinking": "[Читаем | Нейросеть думает...]",
        "status_waiting": "[Читаем | Ожидание ИИ...]",
        "status_pause": "[Пауза]",
        "status_preloaded": "ИИ предзагрузил:",
        "status_asking": "[Идет обработка запроса...]",
        "status_ai_paused": "[ИИ на паузе]",
        "err_model": "[Ошибка: Модель не найдена]",
        "ai_loading": "[ИИ: Инициализация...]",
        "ai_ready": "[ИИ: Готов]",
        "btn_ask_ai": "Спросить ИИ",
        "btn_cancel_ai": "Отмена ИИ",
        "ask_ai_title": "Справка от ИИ",
        "btn_reset": "Сброс",
        "msg_reset_title": "Сброс настроек",
        "msg_reset_text": "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
        "theme_sepia": "Сепия",
        "theme_dark": "Темная",
        "theme_light": "Светлая",
        "theme_starry": "Звёздная Ночь",
        "drag_drop": "Перетащите ваш файл сюда",
        "donate_title": "Пожертвовать",
        "btn_donate": "Пожертвовать 🍪",
        "emotions": {
            0: "Тишина (Оглавление)", 1: "История", 2: "Саспенс", 3: "Экшен", 
            4: "Развязка", 5: "Романтика", 6: "Грусть", 7: "Радость", 
            8: "Мистика", 9: "Погоня", 10: "Хоррор", 11: "Флешбэк", 12: "Комедия"
        }
    }
}

class StarryBackground(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.stars = []
        self.shooting_stars = []
        self.cached_bg = None

        for _ in range(150):
            self.stars.append({
                'x': random.random(),
                'y': random.random(),
                'size': random.uniform(0.5, 2.2),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(0.5, 2.5),
                'phase': random.uniform(0, 6.283),
                'color': random.choice([
                    (255, 255, 255), (210, 230, 255), (255, 245, 230)
                ])
            })
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)
        self.time_val = 0.0
        self.shooting_timer = random.uniform(2.0, 5.0)

    def _tick(self):
        self.time_val += 0.033
        self.shooting_timer -= 0.033
        if self.shooting_timer <= 0:
            self.shooting_timer = random.uniform(4.0, 10.0)
            self.shooting_stars.append({
                'x': random.uniform(0.1, 0.9),
                'y': random.uniform(0.0, 0.3),
                'vx': random.uniform(0.8, 1.5) * random.choice([-1, 1]),
                'vy': random.uniform(0.5, 1.0),
                'life': 1.0
            })
        for ss in self.shooting_stars[:]:
            ss['life'] -= 0.02
            if ss['life'] <= 0:
                self.shooting_stars.remove(ss)
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.cached_bg = None 

    def _draw_cached_bg(self):
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#03030A"))
        gradient.setColorAt(0.5, QColor("#080816"))
        gradient.setColorAt(1, QColor("#0B0B1A"))
        painter.fillRect(self.rect(), gradient)

        nebula1 = QRadialGradient(self.width() * 0.8, self.height() * 0.2, self.width() * 0.5)
        nebula1.setColorAt(0, QColor(45, 25, 65, 40))
        nebula1.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), nebula1)

        nebula2 = QRadialGradient(self.width() * 0.2, self.height() * 0.8, self.width() * 0.4)
        nebula2.setColorAt(0, QColor(20, 35, 60, 30))
        nebula2.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), nebula2)

        painter.end()
        self.cached_bg = pixmap

    def paintEvent(self, event):
        if self.cached_bg is None or self.cached_bg.size() != self.size():
            self._draw_cached_bg()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.cached_bg)

        for star in self.stars:
            twinkle = (math.sin(self.time_val * star['twinkle_speed'] + star['phase']) + 1) / 2
            alpha = int(star['brightness'] * (0.3 + 0.7 * twinkle) * 255)
            r, g, b = star['color']
            painter.setBrush(QColor(r, g, b, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            x = star['x'] * self.width()
            y = star['y'] * self.height()
            size = star['size'] * (0.8 + 0.2 * twinkle)
            painter.drawEllipse(QPointF(x, y), size, size)

        for ss in self.shooting_stars:
            x = ss['x'] * self.width()
            y = ss['y'] * self.height()
            tail_len = 60
            tx = x - tail_len * ss['vx']
            ty = y - tail_len * ss['vy']
            tail = QLinearGradient(x, y, tx, ty)
            tail.setColorAt(0, QColor(255, 255, 255, int(ss['life'] * 200)))
            tail.setColorAt(1, QColor(255, 255, 255, 0))
            pen = QPen(tail, 2.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(x, y), QPointF(tx, ty))

class TextContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.starry_bg = StarryBackground(self)
        self.starry_bg.hide()
        self.starry_bg.lower()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.starry_bg.setGeometry(self.rect())

    def show_starry(self, enabled):
        if enabled:
            self.starry_bg.show()
            self.starry_bg.lower()
        else:
            self.starry_bg.hide()

class MarqueeLabel(QLabel):
    def __init__(self):
        super().__init__()
        self._text = ""
        self._offset = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scroll_text)
        self.timer.setInterval(16)
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.gap = 50
        self.last_time = 0.0

    def setText(self, text):
        if self._text == text: return
        self._text = text
        self._offset = 0.0
        fm = self.fontMetrics()
        if fm.horizontalAdvance(self._text) > self.width() and self.width() > 0:
            if not self.timer.isActive():
                self.last_time = time.perf_counter()
                self.timer.start()
        else:
            self.timer.stop()
        self.update()

    def scroll_text(self):
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now
        speed = 30.0
        self._offset += speed * dt
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        if self._offset >= text_width + self.gap:
            self._offset -= (text_width + self.gap)
        self.update()

    def paintEvent(self, event):
        if not self._text: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        y_pos = float(fm.ascent() + (self.height() - fm.height()) / 2)
        if text_width > self.width() and self.timer.isActive():
            x = -self._offset
            while x < self.width():
                painter.drawText(QPointF(x, y_pos), self._text)
                x += text_width + self.gap
        else:
            painter.drawText(QPointF(0.0, y_pos), self._text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setText(self._text)

class ColorDot(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(20, 20)
        self._color = QColor("#808080")
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(500)
        self.anim.valueChanged.connect(self._on_anim_step)

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._pulse_tick)
        self.pulse_timer.start(33)
        self.pulse_time = 0.0

    def _pulse_tick(self):
        self.pulse_time += 0.033
        self.update()

    def _on_anim_step(self, color):
        self._color = color
        self.update()

    def set_emotion_color(self, emotion_id):
        target_hex = EMOTION_COLORS.get(emotion_id, "#808080")
        self.anim.stop()
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(QColor(target_hex))
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pulse = (math.sin(self.pulse_time * 2.5) + 1) / 2
        glow_radius = 10 + pulse * 4
        glow_alpha = int(40 + pulse * 60)

        glow = QRadialGradient(self.width()/2, self.height()/2, glow_radius)
        glow_color = QColor(self._color)
        glow_color.setAlpha(glow_alpha)
        glow.setColorAt(0, glow_color)
        
        glow_color2 = QColor(self._color)
        glow_color2.setAlpha(0)
        glow.setColorAt(1, glow_color2)
        
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())

        painter.setBrush(self._color)
        pen = QPen(QColor(0, 0, 0, 30))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawEllipse(2, 2, self.width()-4, self.height()-4)

class WindowControlButton(QPushButton):
    def __init__(self, btn_type, parent=None):
        super().__init__(parent)
        self.btn_type = btn_type
        self.setFixedSize(45, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_hovered = False

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        if self.is_hovered:
            if self.btn_type == 'close':
                painter.fillRect(self.rect(), QColor("#E81123"))
            else:
                painter.fillRect(self.rect(), QColor(128, 128, 128, 40))

        color = QColor("white") if (self.is_hovered and self.btn_type == 'close') else self.palette().text().color()
        pen = QPen(color)
        pen.setWidth(1)
        painter.setPen(pen)

        center_x, center_y = self.width() // 2, self.height() // 2
        
        if self.btn_type == 'min':
            painter.drawLine(center_x - 5, center_y, center_x + 5, center_y)
        elif self.btn_type == 'max':
            if self.window().isMaximized():
                painter.drawRect(center_x - 4, center_y - 2, 6, 6)
                painter.drawLine(center_x - 2, center_y - 4, center_x + 4, center_y - 4)
                painter.drawLine(center_x + 4, center_y - 4, center_x + 4, center_y + 2)
            else:
                painter.drawRect(center_x - 5, center_y - 4, 10, 10)
        elif self.btn_type == 'close':
            painter.drawLine(center_x - 4, center_y - 4, center_x + 4, center_y + 4)
            painter.drawLine(center_x + 4, center_y - 4, center_x - 4, center_y + 4)

class CustomTitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setObjectName("title_bar")
        self._is_dragging = False
        self._drag_start_pos = QPoint()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0)
        layout.setSpacing(10)
        
        self.icon_label = QLabel()
        
        icon_path = get_resource_path("icon.ico").replace('\\', '/')
        if os.path.exists(icon_path):
            self.icon_label.setPixmap(QIcon(icon_path).pixmap(16, 16))
            
        layout.addWidget(self.icon_label)
        
        self.title_label = QLabel("YaRead")
        self.title_label.setObjectName("title_label")
        self.title_label.setFont(QFont("Segoe UI Variable", 10, QFont.Weight.Bold))
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.btn_min = WindowControlButton('min', self)
        self.btn_max = WindowControlButton('max', self)
        self.btn_close = WindowControlButton('close', self)

        layout.addWidget(self.btn_min, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.btn_max, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignTop)

        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximized)
        self.btn_close.clicked.connect(self.parent.close)

    def toggle_maximized(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            if self.parent.isMaximized():
                self.parent.showNormal()
            self.parent.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximized()
            event.accept()

class SelectableTextItem(QGraphicsTextItem):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def paint(self, painter, option, widget):
        opt = QStyleOptionGraphicsItem(option)
        opt.state &= ~QStyle.StateFlag.State_HasFocus
        if hasattr(self.parent_view, 'hl_bg_color'):
            opt.palette.setColor(QPalette.ColorRole.Highlight, self.parent_view.hl_bg_color)
            opt.palette.setColor(QPalette.ColorRole.HighlightedText, self.parent_view.hl_fg_color)
        super().paint(painter, opt, widget)

    def wheelEvent(self, event):
        delta = event.delta()
        self.parent_view.scroll_by(-delta * 0.8)
        event.accept()

    def contextMenuEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            self.parent_view.clear_all_selections(except_item=self)
            super().mousePressEvent(event)
        else:
            self.parent_view.clear_all_selections()
            event.ignore()

    def mouseMoveEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            super().mouseMoveEvent(event)
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            super().mouseReleaseEvent(event)
            cursor = self.textCursor()
            if cursor.hasSelection():
                pos = self.scenePos() + event.pos()
                self.parent_view.show_ask_btn(cursor.selectedText(), pos)
        else:
            event.ignore()

class SmoothTextView(QGraphicsView):
    scroll_changed = pyqtSignal(float, float)
    ask_ai_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.text_items = []
        self.char_offsets = []
        self.chunk_bounds = []
        self.item_y_offsets = []
        self.full_text = ""
        self.search_results = []
        self.search_query_cache = ""
        self.current_search_index = -1
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.verticalScrollBar().valueChanged.connect(self._lock_scrollbar)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setFrameStyle(0)
        
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        self.exact_y = 0.0
        self._render_y = 0.0
        
        self.current_width = 800
        self.current_font = QFont("Georgia", 24)
        self.current_text_color = QColor("#000000")

        self.hl_bg_color = QColor("#FFE066")
        self.hl_fg_color = QColor("#000000")

        self.ask_btn = QPushButton("Ask AI", self)
        self.ask_btn.setObjectName("ask_btn")
        self.ask_btn.hide()
        self.ask_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ask_btn.clicked.connect(self.trigger_ask_ai)
        self.selected_text_cache = ""

    def set_highlight_colors(self, bg_color, fg_color):
        self.hl_bg_color = bg_color
        self.hl_fg_color = fg_color
        if self.search_results and self.search_query_cache:
            self._apply_highlights()
            self.viewport().update()

    def _lock_scrollbar(self, val):
        if val != 0:
            self.verticalScrollBar().setValue(0)

    def clear_all_selections(self, except_item=None):
        for item in self.text_items:
            if item != except_item:
                cursor = item.textCursor()
                if cursor.hasSelection():
                    cursor.clearSelection()
                    item.setTextCursor(cursor)
        self.hide_ask_btn()

    def show_ask_btn(self, text, scene_pos):
        self.selected_text_cache = text.strip()
        if not self.selected_text_cache: return
        view_pos = self.mapFromScene(scene_pos)
        self.ask_btn.move(int(view_pos.x()), int(view_pos.y() + 20))
        self.ask_btn.show()

    def hide_ask_btn(self):
        self.ask_btn.hide()

    def trigger_ask_ai(self):
        self.ask_btn.hide()
        if self.selected_text_cache:
            self.ask_ai_requested.emit(self.selected_text_cache)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.pixelDelta().y()
        self.scroll_by(-delta * 0.8)
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.scroll_by(-50)
        elif event.key() == Qt.Key.Key_Down:
            self.scroll_by(50)
        elif event.key() == Qt.Key.Key_PageUp:
            self.scroll_by(-self.viewport().height())
        elif event.key() == Qt.Key.Key_PageDown:
            self.scroll_by(self.viewport().height())
        else:
            super().keyPressEvent(event)

    def _ensure_wrap_mode(self, item):
        doc = item.document()
        option = doc.defaultTextOption()
        option.setWrapMode(QTextOption.WrapMode.WordWrap)
        doc.setDefaultTextOption(option)

    def setPlainText(self, text, app_ref=None):
        self.scene.clear()
        self.text_items = []
        self.char_offsets = []
        self.chunk_bounds = []
        self.item_y_offsets = []
        self.full_text = text
        self.search_results = []
        self.search_query_cache = ""
        self.current_search_index = -1
        self.hide_ask_btn()
        
        self.exact_y = 0.0
        self._render_y = 0.0
        
        if not text:
            self.scene.setSceneRect(0, 0, self.current_width, 0)
            self.scroll_to_top()
            return
            
        chunk_size = 1200
        current_idx = 0
        text_len = len(text)
        current_y = 0.0
        loop_counter = 0
        
        while current_idx < text_len:
            end_idx = min(current_idx + chunk_size, text_len)
            if end_idx < text_len:
                nl_pos = text.rfind('\n', current_idx, end_idx)
                if nl_pos != -1 and nl_pos > current_idx:
                    end_idx = nl_pos + 1
                else:
                    dot_pos = text.rfind('. ', current_idx, end_idx)
                    if dot_pos != -1 and dot_pos > current_idx:
                        end_idx = dot_pos + 2
                    else:
                        space_pos = text.rfind(' ', current_idx, end_idx)
                        if space_pos != -1 and space_pos > current_idx:
                            end_idx = space_pos + 1
                            
            chunk_text = text[current_idx:end_idx]
            item = SelectableTextItem(self)
            item.setPlainText(chunk_text)
            item.setFont(self.current_font)
            self._ensure_wrap_mode(item)
            item.setTextWidth(self.current_width)
            item.setDefaultTextColor(self.current_text_color)
            item.document().setDocumentMargin(0)
            item.setPos(0, current_y)
            doc_height = item.document().size().height()
            self.scene.addItem(item)
            self.text_items.append(item)
            self.char_offsets.append(current_idx)
            self.chunk_bounds.append((current_idx, end_idx))
            self.item_y_offsets.append(current_y)
            current_y += doc_height
            current_idx = end_idx
            loop_counter += 1
            
            if loop_counter % 25 == 0 and app_ref and hasattr(app_ref, 'progress_label'):
                app_ref.progress_label.setText(f"Loading... {int((current_idx/text_len)*100)}%")
                QApplication.processEvents()
                
        self.scene.setSceneRect(0, 0, self.current_width, current_y)
        self.scroll_to_y(self.exact_y)

    def setFont(self, font):
        self.current_font = font
        for item in self.text_items:
            item.setFont(font)
            self._ensure_wrap_mode(item)
            item.setTextWidth(self.current_width)
        self.update_layout()

    def set_text_color(self, color):
        self.current_text_color = color
        clean_format = QTextCharFormat()
        clean_format.setForeground(color)
        clean_format.setBackground(Qt.GlobalColor.transparent)
        for item in self.text_items:
            item.setDefaultTextColor(color)
            cursor = QTextCursor(item.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(clean_format)
        if self.search_results and self.search_query_cache:
            self._apply_highlights()

    def set_text_width(self, w):
        if self.current_width == w: return
        self.current_width = w
        for item in self.text_items:
            self._ensure_wrap_mode(item)
            item.setTextWidth(w)
        self.update_layout()
        super().setFixedWidth(int(w) + 80)

    def update_layout(self):
        self.item_y_offsets = []
        y_offset = 0.0
        for item in self.text_items:
            item.setPos(0, y_offset)
            self.item_y_offsets.append(y_offset)
            y_offset += item.document().size().height()
        self.scene.setSceneRect(0, 0, self.current_width, y_offset)
        self.scroll_to_y(self.exact_y)

    def scroll_by(self, dy):
        self.scroll_to_y(self.exact_y + dy)
        self.hide_ask_btn()

    def scroll_to_y(self, target_y):
        max_y = max(0, self.scene.sceneRect().height() - self.viewport().height())
        self.exact_y = max(0.0, min(target_y, max_y))
        
        if self.exact_y != self._render_y:
            self._render_y = self.exact_y
            self.setTransform(QTransform().translate(0, -self._render_y))
            
        self.scroll_changed.emit(self.exact_y, max_y)

    def scroll_to_top(self):
        self.scroll_to_y(0)

    def get_text_position(self):
        if not self.item_y_offsets or not self.text_items:
            return 0
        idx = bisect.bisect_right(self.item_y_offsets, self.exact_y) - 1
        if idx < 0: idx = 0
        item = self.text_items[idx]
        local_y = self.exact_y - self.item_y_offsets[idx]
        doc = item.document()
        layout = doc.documentLayout()
        pos = layout.hitTest(QPointF(0, local_y), Qt.HitTestAccuracy.FuzzyHit)
        return self.char_offsets[idx] + pos

    def highlight_search(self, query):
        self.clear_highlights()
        if not query: return 0, 0
        self.search_query_cache = query
        idx = self.full_text.lower().find(query.lower())
        while idx != -1:
            self.search_results.append(idx)
            idx = self.full_text.lower().find(query.lower(), idx + len(query))

        self.search_query_len = len(query)
        self._apply_highlights()
        return len(self.search_results), 0

    def clear_highlights(self):
        clean_format = QTextCharFormat()
        clean_format.setForeground(self.current_text_color)
        clean_format.setBackground(Qt.GlobalColor.transparent)
        for item in self.text_items:
            cursor = QTextCursor(item.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(clean_format)
        self.search_results = []
        self.search_query_cache = ""
        self.current_search_index = -1

    def _apply_highlights(self):
        if not self.search_results: return
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(self.hl_bg_color)
        highlight_format.setForeground(self.hl_fg_color)

        for match_idx in self.search_results:
            item_idx = bisect.bisect_right(self.char_offsets, match_idx) - 1
            if item_idx >= 0:
                item = self.text_items[item_idx]
                local_idx = match_idx - self.char_offsets[item_idx]
                cursor = QTextCursor(item.document())
                cursor.setPosition(local_idx)
                cursor.setPosition(local_idx + self.search_query_len, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(highlight_format)

    def go_to_next_search(self):
        if not self.search_results: return 0, 0
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.scroll_to_char_index(self.search_results[self.current_search_index])
        return len(self.search_results), self.current_search_index + 1

    def go_to_prev_search(self):
        if not self.search_results: return 0, 0
        if self.current_search_index <= 0:
            self.current_search_index = len(self.search_results) - 1
        else:
            self.current_search_index -= 1
        self.scroll_to_char_index(self.search_results[self.current_search_index])
        return len(self.search_results), self.current_search_index + 1

    def scroll_to_char_index(self, target_idx):
        if not self.char_offsets: return
        idx = bisect.bisect_right(self.char_offsets, target_idx) - 1
        if idx < 0: idx = 0
        item = self.text_items[idx]
        local_idx = target_idx - self.char_offsets[idx]
        total_len = max(1, len(item.toPlainText()))
        ratio = local_idx / total_len
        target_y = self.item_y_offsets[idx] + (item.document().size().height() * ratio)
        viewport_height = self.viewport().height()
        self.scroll_to_y(target_y - (viewport_height / 3))

class LlamaWorker(QThread):
    emotion_detected = pyqtSignal(int, int, int)
    ask_ai_result = pyqtSignal(str)
    error_occurred = pyqtSignal(str, int)
    finished_chunk = pyqtSignal(int, int)
    status_update = pyqtSignal(str)

    def __init__(self, lang="en", base_dir=""):
        super().__init__()
        self.queue = []
        self.llm = None
        self.ai_mode = "local"
        self.model_path_or_name = ""
        self.api_key = ""
        self.current_loaded_model = ""
        self.running = True
        self.lang = lang
        self.base_dir = base_dir

    def update_config(self, mode, model_val, key):
        self.ai_mode = mode
        self.model_path_or_name = model_val
        self.api_key = key

    def set_lang(self, lang):
        self.lang = lang

    def add_task(self, task_type, text_chunk, chunk_index=0, doc_id=0):
        if task_type == "ask":
            self.queue.insert(0, (task_type, text_chunk, chunk_index, doc_id))
        else:
            self.queue.append((task_type, text_chunk, chunk_index, doc_id))

    def _call_api(self, system_prompt, user_text, temperature=0.0, max_tokens=15):
        if self.ai_mode == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            data = {
                "contents": [{"parts": [{"text": system_prompt + "\n\n" + user_text}]}], 
                "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                candidates = res.get('candidates', [])
                if not candidates:
                    err = res.get('promptFeedback', 'No candidates returned.')
                    raise Exception(f"Gemini API Error: {err}")
                parts = candidates[0].get('content', {}).get('parts', [])
                if not parts:
                    finish_reason = candidates[0].get('finishReason', 'UNKNOWN')
                    raise Exception(f"Gemini API Error: 'parts' missing (FinishReason: {finish_reason})")
                return parts[0].get('text', '')
        else:
            url = "https://api.openai.com/v1/chat/completions"
            model_name = "gpt-4o-mini"
            if self.ai_mode == "openrouter":
                url = "https://openrouter.ai/api/v1/chat/completions"
                model_name = "google/gemini-2.5-flash"
            elif self.ai_mode == "deepseek":
                url = "https://api.deepseek.com/chat/completions"
                model_name = "deepseek-chat"
                
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            data = {
                "model": model_name, 
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}], 
                "temperature": temperature, 
                "max_tokens": max_tokens 
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                choices = res.get('choices', [])
                if not choices:
                    raise Exception(f"API Error: no choices returned. Full response: {res}")
                return choices[0].get('message', {}).get('content', '')

    def run(self):
        n_threads = max(1, int((os.cpu_count() or 4) * 0.40))
        os.environ["OMP_NUM_THREADS"] = str(n_threads)
        os.environ["OPENBLAS_NUM_THREADS"] = str(n_threads)
        os.environ["MKL_NUM_THREADS"] = str(n_threads)

        while self.running:
            if not self.queue:
                time.sleep(0.1)
                continue
                
            if self.ai_mode == "local":
                if not HAS_LLAMA:
                    self.error_occurred.emit("llama-cpp-python not installed", 0)
                    self.queue.clear()
                    time.sleep(1)
                    continue
                    
                actual_path = self.model_path_or_name
                if not os.path.isabs(actual_path):
                    if getattr(sys, 'frozen', False):
                        exe_dir = os.path.dirname(sys.executable)
                    else:
                        exe_dir = os.path.dirname(os.path.abspath(__file__))
                    actual_path = os.path.join(exe_dir, "models", actual_path)

                if self.llm is None or self.current_loaded_model != actual_path:
                    if not os.path.exists(actual_path):
                        self.status_update.emit(LANG_DICT[self.lang]["err_model"])
                        time.sleep(2)
                        continue
                    self.status_update.emit(LANG_DICT[self.lang]["ai_loading"])
                    try:
                        self.llm = Llama(
                            model_path=actual_path,
                            n_ctx=1024, n_threads=n_threads,
                            n_threads_batch=n_threads,
                            n_gpu_layers=-1, flash_attn=True,
                            verbose=False 
                        )
                        self.current_loaded_model = actual_path
                        self.status_update.emit(LANG_DICT[self.lang]["ai_ready"])
                    except Exception as e:
                        self.error_occurred.emit(f"AI Init Error: {e}", 0)
                        time.sleep(2)
                        continue
                        
            try:
                task = self.queue.pop(0)
            except IndexError:
                continue
                
            task_type, text_chunk, chunk_index, doc_id = task
            
            if task_type == "ask":
                lang_str = "Russian" if self.lang == "ru" else "English"
                sys_prompt = f"You are an expert encyclopedia. The user provides a text selection. Provide a high-quality, concise, but comprehensive explanation or definition in {lang_str}. Do NOT just translate. Give encyclopedic context or explain its deep meaning. Ensure your response is fully completed and does not cut off abruptly."
                try:
                    if self.ai_mode == "local":
                        resp = self.llm.create_chat_completion(
                            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": f"Text: {text_chunk}"}],
                            temperature=0.2, max_tokens=800 
                        )
                        result = resp["choices"][0]["message"]["content"]
                    else:
                        result = self._call_api(sys_prompt, f"Text: {text_chunk}", temperature=0.2, max_tokens=800)
                    self.ask_ai_result.emit(result)
                except urllib.error.HTTPError as e:
                    if e.code in [502, 503, 504, 429]:
                        self.ask_ai_result.emit(f"API Overloaded (Error {e.code}). Try again.")
                    else:
                        self.ask_ai_result.emit(f"API Error: {e.code}")
                except Exception as e:
                    self.ask_ai_result.emit(f"Error: {e}")
                continue
                
            sys_prompt = "You are a film composer. Output only JSON."
            user_prompt = """Analyze the narrative text and select ONE emotion (1-12) that BEST describes the scene.
If the text is just normal exposition, calm dialogue, or has no strong emotion, YOU MUST select 1.
1-Story/Narrative, 2-Suspense, 3-Action/Climax, 4-Resolution, 5-Romance, 6-Sadness, 7-Joy, 8-Mystery, 9-Chase, 10-Horror, 11-Flashback, 12-Comedy.
REPLY STRICTLY IN JSON FORMAT: {"emotion_id": X}
Text: """ + text_chunk
            try:
                if self.ai_mode == "local":
                    response = self.llm.create_chat_completion(
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                        temperature=0.0, max_tokens=15 
                    )
                    response_text = response["choices"][0]["message"]["content"]
                else:
                    response_text = self._call_api(sys_prompt, user_prompt, temperature=0.0, max_tokens=15)
                    
                emotion_id = 0
                json_match = re.search(r'"emotion_id"\s*:\s*(\d+)', response_text, re.IGNORECASE)
                if json_match:
                    emotion_id = int(json_match.group(1))
                else:
                    numbers = re.findall(r'\b(1[0-2]|[1-9])\b', response_text)
                    if numbers:
                        emotion_id = int(numbers[-1])
                        
                if 1 <= emotion_id <= 12:
                    self.emotion_detected.emit(chunk_index, emotion_id, doc_id)
                else:
                    self.error_occurred.emit("AI Format Error", doc_id)
            except urllib.error.HTTPError as e:
                if e.code in [502, 503, 504, 429]:
                    self.error_occurred.emit("[API Overloaded, retrying...]", doc_id)
                    self.queue.insert(0, task)
                    time.sleep(2.5)
                else:
                    self.error_occurred.emit(f"API Error {e.code}", doc_id)
            except Exception as e:
                self.error_occurred.emit(f"AI Error: {str(e)}", doc_id)
                
            self.finished_chunk.emit(chunk_index, doc_id)

class FadeOverlay(QWidget):
    def __init__(self, parent, old_pixmap):
        super().__init__(parent)
        self.pixmap = old_pixmap
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setGeometry(parent.rect())
        self._opacity = 1.0

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        painter.drawPixmap(0, 0, self.pixmap)

class JumpSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.pos().x()) / self.width()
            self.setValue(int(val))
            self.sliderPressed.emit()
            self.sliderMoved.emit(int(val))
        super().mousePressEvent(event)

class RecentFilesDialog(QDialog):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.setWindowTitle(LANG_DICT[parent_app.lang].get("window_title", "YaRead") + " - Recent Files")
        self.setMinimumSize(500, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        t = self.parent_app.get_theme_data(self.parent_app.theme_combo.currentIndex())
        self.setStyleSheet(f"background-color: {t['bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        title_label = QLabel("Recent Files" if parent_app.lang == "en" else "Последние открытые")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {t['text']};")
        main_layout.addWidget(title_label)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(5)
        main_layout.addWidget(self.list_container)
        
        self.refresh_list()
            
        main_layout.addStretch()
        
        other_text = "Open another file..." if parent_app.lang == "en" else "Загрузить другой файл..."
        other_btn = QPushButton(other_text)
        other_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        other_btn.setMinimumHeight(40)
        other_btn.setStyleSheet(f"QPushButton {{ background-color: {t['btn']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 5px 15px; font-weight: bold; }} QPushButton:hover {{ background-color: {t['btn_hover']}; }}")
        other_btn.clicked.connect(self.open_other)
        main_layout.addWidget(other_btn)

    def refresh_list(self):
        t = self.parent_app.get_theme_data(self.parent_app.theme_combo.currentIndex())
        
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        recent_list = getattr(self.parent_app, 'recent_files', [])
        
        if not recent_list:
            empty_msg = "It's empty here" if self.parent_app.lang == "en" else "Здесь пока пусто"
            empty_label = QLabel(empty_msg)
            empty_label.setFont(QFont("Segoe UI", 12))
            empty_label.setStyleSheet(f"color: {t['text']}; padding: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty_label)
        else:
            for item in recent_list:
                row_widget = QWidget()
                item_layout = QHBoxLayout(row_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(5)
                
                btn = QPushButton()
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setMinimumHeight(85)
                btn.setStyleSheet(f"QPushButton {{ background-color: {t['panel']}; border: 1px solid {t['border']}; border-radius: 8px; text-align: left; }} QPushButton:hover {{ background-color: {t['btn_hover']}; }}")
                
                btn_layout = QVBoxLayout(btn)
                btn_layout.setContentsMargins(10, 10, 10, 10)
                btn_layout.setSpacing(5)
                
                name_label = QLabel(item.get("title", "Unknown"))
                name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                name_label.setStyleSheet(f"color: {t['text']}; background: transparent; border: none;")
                name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                
                path_label = QLabel(item.get("filepath", ""))
                path_label.setFont(QFont("Segoe UI", 9))
                path_label.setStyleSheet(f"color: {t['accent']}; background: transparent; border: none;")
                path_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                
                p = item.get('percentage', 0.0)
                d = item.get('date', '')
                info_text = f"Read: {p:.1f}% | Opened: {d}" if self.parent_app.lang == "en" else f"Прочитано: {p:.1f}% | Открыто: {d}"
                info_label = QLabel(info_text)
                info_label.setFont(QFont("Segoe UI", 10))
                info_label.setStyleSheet(f"color: {t['text']}; background: transparent; border: none;")
                info_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                
                btn_layout.addWidget(name_label)
                btn_layout.addWidget(path_label)
                btn_layout.addWidget(info_label)
                
                btn.clicked.connect(lambda checked, fp=item.get("filepath"), pct=item.get("percentage", 0.0): self.open_file(fp, pct))
                
                item_layout.addWidget(btn, stretch=1)
                
                del_btn = QPushButton("✕")
                del_btn.setFixedSize(40, 85)
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.setStyleSheet(f"QPushButton {{ background-color: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; font-size: 16px; font-weight: bold; }} QPushButton:hover {{ background-color: #FF4B4B; color: white; border: 1px solid #FF4B4B; }}")
                del_btn.clicked.connect(lambda checked, fp=item.get("filepath"): self.remove_file(fp))
                
                item_layout.addWidget(del_btn)
                
                self.list_layout.addWidget(row_widget)
        
    def open_file(self, filepath, restore_pct):
        self.accept()
        if not os.path.exists(filepath):
            msg = "The file no longer exists:" if self.parent_app.lang == "en" else "Файл больше не существует:"
            QMessageBox.warning(self.parent_app, "YaRead", f"{msg}\n{filepath}")
            return
        self.parent_app.load_pdf(filepath=filepath, restore_pct=restore_pct)
        
    def open_other(self):
        self.accept()
        self.parent_app.load_pdf(filepath=None)

    def remove_file(self, filepath):
        if getattr(self.parent_app, 'current_pdf_path', '') == filepath:
            t = LANG_DICT.get(self.parent_app.lang, LANG_DICT["en"])
            title = "Warning" if self.parent_app.lang == "en" else "Внимание"
            msg = ("This file is currently open. If you remove it from history, it will be closed. Continue?" 
                   if self.parent_app.lang == "en" 
                   else "Этот файл сейчас открыт. Если удалить его из истории, он будет закрыт. Продолжить?")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(msg)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            msg_box.button(QMessageBox.StandardButton.Yes).setText(t.get("btn_yes", "Yes"))
            msg_box.button(QMessageBox.StandardButton.No).setText(t.get("btn_no", "No"))
            
            theme_data = self.parent_app.get_theme_data(self.parent_app.theme_combo.currentIndex())
            msg_box.setStyleSheet(f"""
                QMessageBox {{ background-color: {theme_data['bg']}; color: {theme_data['text']}; }}
                QLabel {{ color: {theme_data['text']}; }}
                QPushButton {{ background-color: {theme_data['btn']}; color: {theme_data['text']}; border: 1px solid {theme_data['border']}; border-radius: 4px; padding: 5px 15px; }}
                QPushButton:hover {{ background-color: {theme_data['btn_hover']}; }}
            """)
            
            reply = msg_box.exec()
            if reply == QMessageBox.StandardButton.Yes:
                self.parent_app.close_file()
            else:
                return

        import json
        for i, item in enumerate(self.parent_app.recent_files):
            if item.get("filepath") == filepath:
                self.parent_app.recent_files.pop(i)
                break
        self.parent_app.settings.setValue("recent_files", json.dumps(self.parent_app.recent_files))
        self.refresh_list()

class YaReadApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = get_resource_path("")

        self.settings = QSettings("YaTeam", "YaRead")
        self.lang = self.settings.value("lang", "en", type=str)
        try:
            recent_str = self.settings.value("recent_files", "[]", type=str)
            self.recent_files = json.loads(recent_str)
        except Exception:
            self.recent_files = []
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Window | 
            Qt.WindowType.WindowSystemMenuHint | 
            Qt.WindowType.WindowMinimizeButtonHint | 
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowTitleHint
        )
        self.resize(1200, 850)
        self.setMinimumSize(850, 600)

        self.is_playing = False
        self.is_asking_ai = False
        self.full_text = ""
        self.current_pdf_path = ""
        self.current_doc_id = 0
        self.block_slider_update = False
        self.text_chunks = []
        self.emotion_map = {}
        self.current_chunk = -1
        self.analyzing_chunks = set()
        self.emotion_history = []
        self.current_active_emotion = 0
        self.target_volumes = {i: 0.0 for i in range(1, 13)}
        self.current_volumes = {i: 0.0 for i in range(1, 13)}
        self.channels = {}

        self.llama_worker = LlamaWorker(lang=self.lang, base_dir=self.base_dir)
        self.llama_worker.emotion_detected.connect(self.on_emotion_detected)
        self.llama_worker.ask_ai_result.connect(self.show_ask_result)
        self.llama_worker.error_occurred.connect(self.on_ai_error)
        self.llama_worker.finished_chunk.connect(self.on_ai_finished)
        self.llama_worker.status_update.connect(self.on_ai_status)

        self.setAcceptDrops(True)
        self.init_audio()
        self.init_ui()
        self.apply_language()
        self.load_settings()
        self._update_worker_config()
        self.llama_worker.start()

        self.scroll_timer = QTimer(self)
        self.scroll_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.scroll_timer.setInterval(16)
        self.scroll_timer.timeout.connect(self.smooth_scroll)
        self.last_frame_time = 0.0
        
        self.tracker_timer = QTimer(self)
        self.tracker_timer.setInterval(200)
        self.tracker_timer.timeout.connect(self.track_position)

        self.ai_queue_timer = QTimer(self)
        self.ai_queue_timer.setInterval(500)
        self.ai_queue_timer.timeout.connect(self.process_ai_queue)

        self.fade_timer = QTimer(self)
        self.fade_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.fade_timer.setInterval(30)
        self.fade_timer.timeout.connect(self.process_audio_fade)
        self.fade_timer.start()

        QTimer.singleShot(100, self.auto_load_last_pdf)

    def _make_arrow_icon(self, color, direction):
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(color))
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        if direction == 'down':
            p.drawLine(4, 6, 8, 10)
            p.drawLine(8, 10, 12, 6)
        else:
            p.drawLine(4, 10, 8, 6)
            p.drawLine(8, 6, 12, 10)
        p.end()
        return pix

    def _ensure_arrow_icons(self, color):
        d = os.path.join(tempfile.gettempdir(), "yaread_icons")
        os.makedirs(d, exist_ok=True)
        key = QColor(color).name().replace('#', '')
        paths = {}
        for direction in ('up', 'down'):
            path = os.path.join(d, f"arrow_{direction}_{key}.png")
            if not os.path.exists(path):
                self._make_arrow_icon(color, direction).save(path, "PNG")
            paths[direction] = path.replace('\\', '/')
        return paths

    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:
            if hasattr(self, 'title_bar'):
                self.title_bar.btn_max.update()
        super().changeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            ext = event.mimeData().urls()[0].toLocalFile().lower()
            if ext.endswith('.pdf') or ext.endswith('.epub') or ext.endswith('.fb2') or ext.endswith('.html') or ext.endswith('.htm'):
                event.accept()
                return
        event.ignore()

    def dropEvent(self, event):
        filepath = event.mimeData().urls()[0].toLocalFile()
        self.load_pdf(filepath=filepath)

    def reset_ai_analysis(self):
        self.current_doc_id += 1
        self.emotion_map.clear()
        self.analyzing_chunks.clear()
        self.emotion_history.clear()
        self.current_chunk = -1
        if hasattr(self, 'llama_worker'):
            self.llama_worker.queue.clear()
        if hasattr(self, 'emotion_dot'):
            self.emotion_dot.set_emotion_color(0)
        self.update_status_title()
        for i in range(1, 13):
            self.target_volumes[i] = 0.0
        if getattr(self, 'is_playing', False):
            self.track_position(force_update=True)

    def on_ai_settings_changed(self):
        self._update_worker_config()
        if getattr(self, 'full_text', ""):
            self.reset_ai_analysis()

    def _update_worker_config(self):
        if not hasattr(self, 'ai_mode_combo') or not hasattr(self, 'model_input') or not hasattr(self, 'api_key_input') or not hasattr(self, 'llama_worker'):
            return
        mode = "local"
        idx = self.ai_mode_combo.currentIndex()
        if idx == 1: mode = "openai"
        elif idx == 2: mode = "openrouter"
        elif idx == 3: mode = "gemini"
        elif idx == 4: mode = "deepseek"
        self.llama_worker.update_config(mode, self.model_input.text(), self.api_key_input.text())

    def load_settings(self):
        if not hasattr(self, 'theme_combo'): return
        self.theme_combo.blockSignals(True)
        self.font_combo.blockSignals(True)
        self.size_spinbox.blockSignals(True)
        self.align_combo.blockSignals(True)
        self.width_slider.blockSignals(True)
        self.speed_slider.blockSignals(True)
        self.volume_slider.blockSignals(True)
        self.auto_scroll_cb.blockSignals(True)
        self.ai_mode_combo.blockSignals(True)
        self.ai_pause_cb.blockSignals(True)

        self.theme_combo.setCurrentIndex(self.settings.value("theme_idx", 1, type=int))
        self.font_combo.setCurrentText(self.settings.value("font_text", "Georgia", type=str))
        
        saved_font_size = self.settings.value("font_size", 24, type=int)
        if saved_font_size <= 0:
            saved_font_size = 24
        self.size_spinbox.setValue(max(14, saved_font_size))
        
        self.align_combo.setCurrentIndex(self.settings.value("align_idx", 0, type=int))
        self.width_slider.setValue(self.settings.value("text_width", 800, type=int))
        self.speed_slider.setValue(self.settings.value("speed", 40, type=int))
        self.volume_slider.setValue(self.settings.value("volume", 60, type=int))
        
        auto_scroll_val = self.settings.value("auto_scroll", True)
        self.auto_scroll_cb.setChecked(True if auto_scroll_val in (True, 'true', 'True') else False)
        
        ai_pause_val = self.settings.value("ai_pause", True)
        self.ai_pause_cb.setChecked(True if ai_pause_val in (True, 'true', 'True') else False)

        self.ai_mode_combo.setCurrentIndex(self.settings.value("ai_mode_idx", 0, type=int))
        saved_model = self.settings.value("ai_model", "", type=str)
        if saved_model: self.model_input.setText(saved_model)
        saved_key = self.settings.value("api_key", "", type=str)
        if saved_key: self.api_key_input.setText(saved_key)
        
        self.toggle_api_fields()

        self.theme_combo.blockSignals(False)
        self.font_combo.blockSignals(False)
        self.size_spinbox.blockSignals(False)
        self.align_combo.blockSignals(False)
        self.width_slider.blockSignals(False)
        self.speed_slider.blockSignals(False)
        self.volume_slider.blockSignals(False)
        self.auto_scroll_cb.blockSignals(False)
        self.ai_mode_combo.blockSignals(False)
        self.ai_pause_cb.blockSignals(False)

        self.apply_theme(animate=False)
        self.apply_font_and_layout()

    def save_settings(self):
        self.settings.setValue("lang", self.lang)
        if hasattr(self, 'theme_combo'):
            self.settings.setValue("theme_idx", self.theme_combo.currentIndex())
            self.settings.setValue("font_text", self.font_combo.currentText())
            self.settings.setValue("font_size", self.size_spinbox.value())
            self.settings.setValue("align_idx", self.align_combo.currentIndex())
            self.settings.setValue("text_width", self.width_slider.value())
            self.settings.setValue("speed", self.speed_slider.value())
            self.settings.setValue("volume", self.volume_slider.value())
            self.settings.setValue("auto_scroll", self.auto_scroll_cb.isChecked())
            self.settings.setValue("ai_pause", self.ai_pause_cb.isChecked())
            self.settings.setValue("ai_mode_idx", self.ai_mode_combo.currentIndex())
            self.settings.setValue("ai_model", self.model_input.text())
            self.settings.setValue("api_key", self.api_key_input.text())
            
        if getattr(self, 'current_pdf_path', "") and getattr(self, 'full_text', ""):
            self.settings.setValue("last_pdf_path", self.current_pdf_path)
            self.settings.setValue("last_scroll_y", self.text_viewer.exact_y)
            for item in self.recent_files:
                if item.get("filepath") == self.current_pdf_path:
                    if hasattr(self, 'text_viewer'):
                        max_y = max(0, self.text_viewer.scene.sceneRect().height() - self.text_viewer.viewport().height())
                        item["percentage"] = (self.text_viewer.exact_y / max_y * 100.0) if max_y > 0 else 0.0
                        item["scroll_y"] = self.text_viewer.exact_y
                    elif hasattr(self, 'book_slider'):
                        item["percentage"] = self.book_slider.value() / 10.0
                    break
        else:
            self.settings.setValue("last_pdf_path", "")
            self.settings.setValue("last_scroll_y", 0.0)
            
        self.settings.setValue("recent_files", json.dumps(self.recent_files))

    def auto_load_last_pdf(self):
        last_path = self.settings.value("last_pdf_path", "", type=str)
        
        pct = 0.0
        for item in self.recent_files:
            if item.get("filepath") == last_path:
                pct = item.get("percentage", 0.0)
                break
                
        if last_path and os.path.exists(last_path):
            self.load_pdf(filepath=last_path, restore_pct=pct)

    def update_recent_file(self, filepath):
        import datetime
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        
        old_pct = 0.0
        old_ry = 0.0
        for i, item in enumerate(self.recent_files):
            if item.get("filepath") == filepath:
                old_pct = item.get("percentage", 0.0)
                old_ry = item.get("scroll_y", 0.0)
                self.recent_files.pop(i)
                break
                
        self.recent_files.insert(0, {
            "title": os.path.basename(filepath),
            "filepath": filepath,
            "percentage": old_pct,
            "scroll_y": old_ry,
            "date": now_str
        })
        
        self.recent_files = self.recent_files[:5]
        self.settings.setValue("recent_files", json.dumps(self.recent_files))

    def show_recent_files_dialog(self):
        dialog = RecentFilesDialog(self)
        dialog.exec()

    def _extract_text(self, filepath):

        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pdf':
            doc = fitz.open(filepath)
            parts = []
            for page in doc:
                raw = page.get_text()
                parts.append(re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', '', raw))
            return '\n\n'.join(parts)

        elif ext == '.epub':
            if not HAS_EPUB:
                raise ImportError(
                    "ebooklib and beautifulsoup4 are required for EPUB support.\n"
                    "Install with: pip install ebooklib beautifulsoup4"
                )
            book = ebooklib_epub.read_epub(filepath, options={'ignore_ncx': True})
            parts = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = _BS(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n')
                text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', '', text)
                text = re.sub(r'\n{3,}', '\n\n', text)
                parts.append(text.strip())
            return '\n\n'.join(p for p in parts if p)

        elif ext == '.fb2':
            if not HAS_FB2:
                raise ImportError(
                    "lxml is required for FB2 support.\n"
                    "Install with: pip install lxml"
                )
            with open(filepath, 'rb') as fh:
                data = fh.read()
            tree = _lxml_etree.fromstring(data)
            ns = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
            parts = []
            bodies = tree.findall('.//fb:body', ns)
            if not bodies:
                bodies = tree.findall('.//body')
            for body in bodies:
                for elem in body.iter():
                    if elem.text:
                        parts.append(elem.text.strip())
                    if elem.tail:
                        parts.append(elem.tail.strip())
            text = '\n'.join(p for p in parts if p)
            text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', '', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text

        elif ext in ('.html', '.htm'):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                html_data = fh.read()
            try:
                from bs4 import BeautifulSoup as _BS
                soup = _BS(html_data, 'html.parser')
                text = soup.get_text(separator='\n')
            except ImportError:
                text = re.sub(r'<style.*?>.*?</style>', '', html_data, flags=re.IGNORECASE | re.DOTALL)
                text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
                text = re.sub(r'<[^>]+>', '\n', text)
                import html as html_lib
                text = html_lib.unescape(text)
            
            text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', '', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()

        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def init_audio(self):
        music_dir = get_resource_path("music")
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            pygame.mixer.set_num_channels(12)
            for i in range(1, 13):
                filepath = os.path.join(music_dir, f"{i}.mp3")
                channel = pygame.mixer.Channel(i - 1)
                self.channels[i] = channel
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    channel.play(sound, loops=-1)
                    channel.set_volume(0.0)
        except Exception as e:
            print(f"[ERROR] Audio init failed: {e}")

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        return shadow

    def init_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("main_bg")
        self.setCentralWidget(self.main_widget)
        
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(12, 8, 12, 8)
        content_layout.setSpacing(8)

        self.top_panel = QFrame()
        self.top_panel.setObjectName("panel")
        self.top_panel.setGraphicsEffect(self.create_shadow())
        self.top_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        
        top_layout = QHBoxLayout(self.top_panel)
        top_layout.setContentsMargins(18, 8, 12, 8)
        top_layout.setSpacing(10)
        
        self.btn_open = QPushButton()
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.clicked.connect(self.show_recent_files_dialog)
        self.btn_open.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.btn_close_file = QPushButton()
        self.btn_close_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close_file.clicked.connect(self.close_file)
        self.btn_close_file.setVisible(False)
        self.btn_close_file.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.btn_play = QPushButton()
        self.btn_play.setObjectName("btn_play")
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_play.setEnabled(False)
        self.btn_play.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        top_layout.addWidget(self.btn_open)
        top_layout.addWidget(self.btn_close_file)

        separator_file = QFrame()
        separator_file.setFrameShape(QFrame.Shape.VLine)
        separator_file.setObjectName("separator")
        top_layout.addWidget(separator_file)

        self.btn_lang = QPushButton()
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self.toggle_language)
        self.btn_lang.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["", "", "", ""])
        self.theme_combo.setMinimumWidth(110)
        self.theme_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.theme_combo.currentIndexChanged.connect(lambda: self.apply_theme(animate=True))
        
        self.btn_reset = QPushButton()
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_to_defaults)
        self.btn_reset.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.btn_donate = QPushButton("Donate 🍪")
        self.btn_donate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_donate.clicked.connect(self.show_donate_dialog)
        self.btn_donate.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        top_layout.addWidget(self.btn_lang)
        top_layout.addWidget(self.theme_combo)
        top_layout.addWidget(self.btn_reset)
        top_layout.addWidget(self.btn_donate)

        separator_ai = QFrame()
        separator_ai.setFrameShape(QFrame.Shape.VLine)
        separator_ai.setObjectName("separator")
        top_layout.addWidget(separator_ai)

        self.lbl_model = QLabel()
        self.lbl_model.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.ai_mode_combo = QComboBox()
        self.ai_mode_combo.addItems(["Local .GGUF", "OpenAI API", "OpenRouter API", "Gemini API", "DeepSeek API"])
        self.ai_mode_combo.setMinimumWidth(130)
        self.ai_mode_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ai_mode_combo.currentIndexChanged.connect(self.toggle_api_fields)
        self.ai_mode_combo.currentIndexChanged.connect(self.on_ai_settings_changed)

        self.model_input = QLineEdit("qwen2.5-7b-instruct-q4_k_m.gguf")
        self.model_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.model_input.setMinimumWidth(100)
        self.model_input.editingFinished.connect(self.on_ai_settings_changed)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.api_key_input.setMinimumWidth(100)
        self.api_key_input.hide()
        self.api_key_input.editingFinished.connect(self.on_ai_settings_changed)

        self.ai_pause_cb = QCheckBox()
        self.ai_pause_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_pause_cb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ai_pause_cb.toggled.connect(self.update_status_title)

        self.btn_cancel_ai = QPushButton()
        self.btn_cancel_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel_ai.clicked.connect(self.cancel_ai_request)
        self.btn_cancel_ai.hide()
        self.btn_cancel_ai.setObjectName("cancel_btn")

        top_layout.addWidget(self.lbl_model)
        top_layout.addWidget(self.ai_mode_combo)
        top_layout.addWidget(self.model_input)
        top_layout.addWidget(self.api_key_input)
        top_layout.addWidget(self.ai_pause_cb)
        top_layout.addWidget(self.btn_cancel_ai)
        
        self.emotion_dot = ColorDot()
        self.emotion_dot.hide()
        top_layout.addWidget(self.emotion_dot)

        self.info_status_label = MarqueeLabel()
        self.info_status_label.setObjectName("info_status")
        top_layout.addWidget(self.info_status_label)

        self.progress_label = QLabel("0.0%")
        self.progress_label.setObjectName("progress")
        self.progress_label.setFixedWidth(50)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_layout.addWidget(self.progress_label)
        
        content_layout.addWidget(self.top_panel)

        self.search_panel = QFrame()
        self.search_panel.setObjectName("search_panel")
        self.search_panel.setMaximumHeight(0)
        self.search_panel.setGraphicsEffect(self.create_shadow())
        search_layout = QHBoxLayout(self.search_panel)
        search_layout.setContentsMargins(15, 8, 15, 8)
        
        self.search_input = QLineEdit()
        self.search_debounce_timer = QTimer()
        self.search_debounce_timer.setSingleShot(True)
        self.search_debounce_timer.setInterval(400)
        self.search_debounce_timer.timeout.connect(self._execute_search)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.search_next)
        
        self.lbl_search_count = QLabel("0 / 0")
        self.lbl_search_count.setFixedWidth(60)
        self.lbl_search_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_search_prev = QPushButton()
        self.btn_search_prev.clicked.connect(self.search_prev)
        
        self.btn_search_next = QPushButton()
        self.btn_search_next.clicked.connect(self.search_next)
        
        self.btn_search_close = QPushButton("X")
        self.btn_search_close.setObjectName("btn_close")
        self.btn_search_close.setFixedSize(26, 26)
        self.btn_search_close.clicked.connect(self.close_search)
        
        self.lbl_search = QLabel()
        search_layout.addWidget(self.lbl_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.lbl_search_count)
        search_layout.addWidget(self.btn_search_prev)
        search_layout.addWidget(self.btn_search_next)
        search_layout.addWidget(self.btn_search_close)
        content_layout.addWidget(self.search_panel)

        self.text_container = TextContainer()
        self.text_layout = QHBoxLayout(self.text_container)
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.text_layout.setSpacing(0)
        
        self.text_viewer = SmoothTextView()
        self.text_viewer.scroll_changed.connect(self.update_progress_ui)
        self.text_viewer.ask_ai_requested.connect(self.request_ask_ai)
        
        self.drop_overlay = QLabel()
        self.drop_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_overlay.setObjectName("drop_overlay")
        
        self.text_layout.addWidget(self.text_viewer)
        self.text_layout.addWidget(self.drop_overlay)
        self.text_viewer.hide()
        content_layout.addWidget(self.text_container, stretch=1)

        self.book_slider = JumpSlider(Qt.Orientation.Horizontal)
        self.book_slider.setObjectName("book_slider")
        self.book_slider.setRange(0, 1000)
        self.book_slider.setValue(0)
        self.book_slider.setEnabled(False)
        self.book_slider.sliderPressed.connect(self.on_slider_pressed)
        self.book_slider.sliderMoved.connect(self.on_slider_moved)
        self.book_slider.sliderReleased.connect(self.on_slider_released)
        content_layout.addWidget(self.book_slider)

        self.bottom_panel = QFrame()
        self.bottom_panel.setObjectName("panel")
        self.bottom_panel.setGraphicsEffect(self.create_shadow())
        self.bottom_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        
        bottom_layout = QHBoxLayout(self.bottom_panel)
        bottom_layout.setContentsMargins(18, 8, 12, 8)
        bottom_layout.setSpacing(10)

        bottom_layout.addWidget(self.btn_play)

        separator_play = QFrame()
        separator_play.setFrameShape(QFrame.Shape.VLine)
        separator_play.setObjectName("separator")
        bottom_layout.addWidget(separator_play)

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Georgia", "Palatino Linotype", "Book Antiqua", "Times New Roman", "Arial", "Consolas"])
        self.font_combo.currentTextChanged.connect(self.apply_font_and_layout)
        self.font_combo.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(14, 48)
        self.size_spinbox.setValue(24)
        self.size_spinbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.size_spinbox.valueChanged.connect(self.apply_font_and_layout)

        self.lbl_align = QLabel()
        self.align_combo = QComboBox()
        self.align_combo.setMinimumWidth(100)
        self.align_combo.addItems(["Center", "Left", "Right"])
        self.align_combo.currentTextChanged.connect(self.update_margins)
        self.align_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.lbl_width = QLabel()
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(400, 1600)
        self.width_slider.setValue(800)
        self.width_slider.setFixedWidth(100)
        self.width_slider.sliderReleased.connect(self.apply_font_and_layout)

        bottom_layout.addWidget(self.font_combo)
        bottom_layout.addWidget(self.size_spinbox)
        bottom_layout.addWidget(self.lbl_align)
        bottom_layout.addWidget(self.align_combo)
        bottom_layout.addWidget(self.lbl_width)
        bottom_layout.addWidget(self.width_slider)

        separator_scroll = QFrame()
        separator_scroll.setFrameShape(QFrame.Shape.VLine)
        separator_scroll.setObjectName("separator")
        bottom_layout.addWidget(separator_scroll)

        self.auto_scroll_cb = QCheckBox()
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_scroll_cb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.lbl_speed = QLabel()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 200)
        self.speed_slider.setValue(40)
        self.speed_slider.setFixedWidth(100)
        
        bottom_layout.addWidget(self.auto_scroll_cb)
        bottom_layout.addWidget(self.lbl_speed)
        bottom_layout.addWidget(self.speed_slider)

        separator_vol = QFrame()
        separator_vol.setFrameShape(QFrame.Shape.VLine)
        separator_vol.setObjectName("separator")
        bottom_layout.addWidget(separator_vol)

        self.lbl_volume = QLabel()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.update_master_volume)

        bottom_layout.addWidget(self.lbl_volume)
        bottom_layout.addWidget(self.volume_slider)
        
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        bottom_layout.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(self.bottom_panel)
        layout.addLayout(content_layout)

        QShortcut(QKeySequence(Qt.Key.Key_Space), self).activated.connect(self.toggle_playback)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.toggle_search)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.close_search)

        self.search_animation = QPropertyAnimation(self.search_panel, b"maximumHeight")
        self.search_animation.setDuration(300)
        self.search_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def show_donate_dialog(self):
        t_dict = LANG_DICT.get(self.lang, LANG_DICT["en"])
        dialog = QDialog(self)
        dialog.setWindowTitle(t_dict.get("donate_title", "Donate"))
        dialog.setMinimumSize(400, 480)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout(dialog)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        t = self.get_theme_data(self.theme_combo.currentIndex())
        dialog.setStyleSheet(f"background-color: {t['bg']};")
        
        qr_path = get_resource_path("qr.png")
        qr_label = QLabel()
        if os.path.exists(qr_path):
            pixmap = QPixmap(qr_path)
            qr_label.setPixmap(pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            qr_label.setText("[QR Code not found]")
            qr_label.setStyleSheet(f"color: {t['text']}; font-size: 16px;")
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qr_label)
        
        btn = QPushButton(t_dict.get("btn_donate", "Donate 🍪"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton {{ background-color: {t['btn']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 12px 20px; font-weight: bold; font-size: 14px; margin-top: 15px; }} QPushButton:hover {{ background-color: {t['btn_hover']}; }}")
        
        def open_link():
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl("https://boosty.to/xronni/single-payment/donation/809763/target?share=target_link"))
            
        btn.clicked.connect(open_link)
        layout.addWidget(btn)
        
        dialog.exec()

    def reset_to_defaults(self):
        t = LANG_DICT[self.lang]
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(t["msg_reset_title"])
        msg_box.setText(t["msg_reset_text"])
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        msg_box.button(QMessageBox.StandardButton.Yes).setText(t.get("btn_yes", "Yes"))
        msg_box.button(QMessageBox.StandardButton.No).setText(t.get("btn_no", "No"))
        
        theme_data = self.get_theme_data(self.theme_combo.currentIndex())
        msg_box.setStyleSheet(f"""
            QMessageBox {{ background-color: {theme_data['bg']}; color: {theme_data['text']}; }}
            QLabel {{ color: {theme_data['text']}; }}
            QPushButton {{ background-color: {theme_data['btn']}; color: {theme_data['text']}; 
                           border: 1px solid {theme_data['border']}; padding: 6px 16px; border-radius: 6px; }}
            QPushButton:hover {{ background-color: {theme_data['btn_hover']}; border: 1px solid {theme_data['accent']}; }}
        """)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            self.theme_combo.blockSignals(True)
            self.font_combo.blockSignals(True)
            self.size_spinbox.blockSignals(True)
            self.align_combo.blockSignals(True)
            self.width_slider.blockSignals(True)
            self.speed_slider.blockSignals(True)
            self.volume_slider.blockSignals(True)
            self.auto_scroll_cb.blockSignals(True)
            self.ai_mode_combo.blockSignals(True)
            self.ai_pause_cb.blockSignals(True)

            self.theme_combo.setCurrentIndex(1)
            self.font_combo.setCurrentText("Georgia")
            self.size_spinbox.setValue(24)
            self.align_combo.setCurrentIndex(0)
            self.width_slider.setValue(800)
            self.speed_slider.setValue(40)
            self.volume_slider.setValue(60)
            self.auto_scroll_cb.setChecked(True)
            self.ai_pause_cb.setChecked(True)
            self.ai_mode_combo.setCurrentIndex(0)
            self.model_input.setText("qwen2.5-7b-instruct-q4_k_m.gguf")
            self.api_key_input.setText("")
            self.toggle_api_fields()
            
            self.theme_combo.blockSignals(False)
            self.font_combo.blockSignals(False)
            self.size_spinbox.blockSignals(False)
            self.align_combo.blockSignals(False)
            self.width_slider.blockSignals(False)
            self.speed_slider.blockSignals(False)
            self.volume_slider.blockSignals(False)
            self.auto_scroll_cb.blockSignals(False)
            self.ai_mode_combo.blockSignals(False)
            self.ai_pause_cb.blockSignals(False)

            self.apply_font_and_layout()
            self.apply_theme(animate=True)
            self.update_master_volume()
            self._update_worker_config()

    def toggle_api_fields(self):
        if not hasattr(self, 'ai_mode_combo') or not hasattr(self, 'api_key_input') or not hasattr(self, 'model_input'):
            return
        idx = self.ai_mode_combo.currentIndex()
        if idx == 0:
            self.api_key_input.hide()
            self.model_input.show()
        else:
            self.api_key_input.show()
            self.model_input.hide()

    def cancel_ai_request(self):
        self.is_asking_ai = False
        self.btn_cancel_ai.hide()
        if hasattr(self, 'llama_worker'):
            self.llama_worker.queue = [task for task in self.llama_worker.queue if task[0] != "ask"]
        self.update_status_title()

    def request_ask_ai(self, text):
        self.is_asking_ai = True
        self.btn_cancel_ai.show()
        if hasattr(self, 'llama_worker'):
            self.llama_worker.add_task("ask", text)
        self.update_status_title()

    def show_ask_result(self, result_text):
        if not self.is_asking_ai:
            return
        self.is_asking_ai = False
        self.btn_cancel_ai.hide()
        self.update_status_title()
        if getattr(self, 'is_playing', False):
            self.track_position(force_update=True)
            
        dialog = QDialog(self)
        dialog.setWindowTitle(LANG_DICT[self.lang]["ask_ai_title"])
        dialog.setMinimumSize(550, 450)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(result_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Arial", 11))
        t = self.get_theme_data(self.theme_combo.currentIndex())
        text_edit.setStyleSheet(f"background-color: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius:8px; padding:12px;")
        dialog.setStyleSheet(f"background-color: {t['bg']};")
        layout.addWidget(text_edit)
        
        dialog.setWindowOpacity(0.0)
        fade_anim = QPropertyAnimation(dialog, b"windowOpacity")
        fade_anim.setDuration(250)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        fade_anim.start()
        dialog.exec()

    def toggle_language(self):
        self.lang = "ru" if self.lang == "en" else "en"
        if hasattr(self, 'llama_worker'):
            self.llama_worker.set_lang(self.lang)
        self.apply_language()

    def apply_language(self):
        if not hasattr(self, 'title_bar') or not hasattr(self, 'btn_open'):
            return
        t = LANG_DICT[self.lang]
        self.title_bar.title_label.setText(t["window_title"])
        self.btn_open.setText(t["btn_open"])
        self.btn_close_file.setText(t["btn_close_file"])
        
        drop_html = f"<div style='text-align: center;'><div style='font-size:72px; margin-bottom:14px; opacity:0.7;'>📖</div><div style='font-size:20px; font-weight: 700; letter-spacing: 0.3px; opacity:0.85; font-family: Segoe UI Variable, Segoe UI, sans-serif;'>{t['drag_drop']}</div><div style='font-size:12px; margin-top:10px; opacity:0.45; font-family: Segoe UI, sans-serif;'>PDF · EPUB · FB2 · HTML</div></div>"
        self.drop_overlay.setText(drop_html)
        
        if self.is_playing:
            self.btn_play.setText(t["btn_pause"])
        else:
            self.btn_play.setText(t["btn_play"])
            
        self.btn_lang.setText(t["btn_lang"])
        self.btn_reset.setText(t["btn_reset"])
        self.lbl_model.setText(t["lbl_model"])
        self.ai_pause_cb.setText(t["ai_pause"])
        self.btn_cancel_ai.setText(t.get("btn_cancel_ai", "Cancel AI"))
        self.search_input.setPlaceholderText(t["search_ph"])
        self.btn_search_prev.setText(t["btn_up"])
        self.btn_search_next.setText(t["btn_down"])
        self.lbl_search.setText(t["lbl_search"])
        self.lbl_align.setText(t["align"])
        self.lbl_width.setText(t["width"])
        self.auto_scroll_cb.setText(t["auto_scroll"])
        self.lbl_speed.setText(t["speed"])
        self.lbl_volume.setText(t["volume"])
        self.text_viewer.ask_btn.setText(t["btn_ask_ai"])
        if hasattr(self, 'btn_donate'):
            self.btn_donate.setText(t.get("btn_donate", "Donate 🍪"))
        
        current_theme_idx = max(0, self.theme_combo.currentIndex())
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItems([t["theme_sepia"], t["theme_dark"], t["theme_light"], t["theme_starry"]])
        self.theme_combo.setCurrentIndex(current_theme_idx)
        self.theme_combo.blockSignals(False)

        current_align_idx = self.align_combo.currentIndex()
        self.align_combo.blockSignals(True)
        self.align_combo.clear()
        self.align_combo.addItems([t["align_center"], t["align_left"], t["align_right"]])
        self.align_combo.setCurrentIndex(current_align_idx)
        self.align_combo.blockSignals(False)
        self.update_status_title()

    def apply_font_and_layout(self):
        if not hasattr(self, 'font_combo') or not hasattr(self, 'text_viewer'):
            return
        font = QFont(self.font_combo.currentText(), self.size_spinbox.value())
        self.text_viewer.setFont(font)
        self.update_margins()

    def update_margins(self):
        if not hasattr(self, 'width_slider') or not hasattr(self, 'align_combo') or not hasattr(self, 'text_viewer'):
            return
        if not self.centralWidget():
            return
            
        available_width = self.centralWidget().width() - 40
        if available_width <= 0: available_width = 1000
        text_width = self.width_slider.value()
        align_idx = self.align_combo.currentIndex()

        if text_width > available_width - 80:
            text_width = available_width - 80
            
        self.text_viewer.set_text_width(text_width)
        self.text_layout.setContentsMargins(0, 0, 0, 0)

        if align_idx == 0:
            self.text_layout.setAlignment(self.text_viewer, Qt.AlignmentFlag.AlignHCenter)
        elif align_idx == 1:
            self.text_layout.setAlignment(self.text_viewer, Qt.AlignmentFlag.AlignLeft)
            self.text_layout.setContentsMargins(40, 0, 0, 0)
        elif align_idx == 2:
            self.text_layout.setAlignment(self.text_viewer, Qt.AlignmentFlag.AlignRight)
            self.text_layout.setContentsMargins(0, 0, 40, 0)

        block_fmt = QTextBlockFormat()
        if align_idx == 0:
            block_fmt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif align_idx == 1:
            block_fmt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        elif align_idx == 2:
            block_fmt.setAlignment(Qt.AlignmentFlag.AlignRight)

        for item in self.text_viewer.text_items:
            cursor = QTextCursor(item.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.mergeBlockFormat(block_fmt)

    def get_theme_data(self, idx):
        themes = [
            {"bg": "#F4ECD8", "text": "#3D2B1F", "panel": "#EAE0CC", "btn": "#DDD2BC", "btn_hover": "#CEBFA8", "accent": "#C07A38", "border": "#D0C4AE", "title_bg": "#DDD2BC", "highlight": "#E8C97A", "highlight_text": "#3D2B1F", "info_text": "rgba(61,43,31,0.55)"},
            {"bg": "#121212", "text": "#FFFFFF", "panel": "#181818", "btn": "#282828", "btn_hover": "#3E3E3E", "accent": "#1DB954", "border": "#333333", "title_bg": "#000000", "highlight": "#1DB954", "highlight_text": "#000000", "info_text": "rgba(255,255,255,0.5)"},
            {"bg": "#F6F6F6", "text": "#1A1A1A", "panel": "#FFFFFF", "btn": "#EFEFEF", "btn_hover": "#E3E3E3", "accent": "#1DB954", "border": "#E8E8E8", "title_bg": "#EFEFEF", "highlight": "#1DB954", "highlight_text": "#FFFFFF", "info_text": "rgba(26,26,26,0.5)"},
            {"bg": "#0A0A14", "text": "#E8EEFF", "panel": "#11112A", "btn": "#1A1A36", "btn_hover": "#252548", "accent": "#7C6FE8", "border": "#1E1E3C", "title_bg": "#05050E", "highlight": "#F0C060", "highlight_text": "#05050E", "info_text": "rgba(232,238,255,0.5)"}
        ]
        return themes[idx if 0 <= idx < 4 else 0]

    def apply_theme(self, animate=False):
        if not hasattr(self, 'theme_combo') or not hasattr(self, 'main_widget'):
            return
            
        old_pixmap = None
        if animate:
            old_pixmap = self.grab()
            self.overlay = FadeOverlay(self, old_pixmap)
            self.overlay.resize(self.size())
            self.overlay.show()
            self.overlay.raise_()
            
        theme_idx = self.theme_combo.currentIndex()
        is_starry = (theme_idx == 3)
        t = self.get_theme_data(theme_idx)
        
        arrows = self._ensure_arrow_icons(t['text'])
        
        if hasattr(self, 'text_container'):
            self.text_container.show_starry(is_starry)
            
        view_bg = "transparent" if is_starry else t['bg']
        self.text_viewer.set_highlight_colors(QColor(t['highlight']), QColor(t['highlight_text']))
        self.text_viewer.set_text_color(QColor(t['text']))

        palette = self.text_viewer.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(t['highlight']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(t['highlight_text']))
        self.text_viewer.setPalette(palette)
        
        self.text_viewer.viewport().setAutoFillBackground(not is_starry)

        app_style = f"""
        QGraphicsView {{ background-color: {view_bg}; border: none; selection-background-color: {t['highlight']}; selection-color: {t['highlight_text']}; }}
        QWidget#main_bg {{ background-color: {t['bg']}; }}
        QFrame#title_bar {{ background-color: {t['title_bg']}; border: none; border-bottom: 1px solid rgba(128,128,128,0.1); }}
        QLabel#title_label {{ color: {t['text']}; padding-left: 6px; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-weight: 700; font-size: 12px; letter-spacing: 0.4px; }}
        QPushButton#ask_btn {{ background-color: {t['accent']}; color: #000000; border-radius: 16px; padding: 6px 16px; font-weight: 700; font-size: 12px; border: none; }}
        QPushButton#ask_btn:hover {{ background-color: {t['btn_hover']}; color: {t['text']}; border: none; }}
        QPushButton#cancel_btn {{ background-color: transparent; border: 1px solid rgba(220,50,50,0.5); color: rgba(220,50,50,0.85); border-radius: 16px; padding: 5px 12px; }}
        QPushButton#cancel_btn:hover {{ background-color: rgba(220,50,50,0.12); border: 1px solid #FF4B4B; color: #FF4B4B; }}
        QFrame#panel, QFrame#search_panel {{ background-color: {t['panel']}; border-radius:10px; border:1px solid {t['border']}; }}
        QFrame#separator {{ color: {t['border']}; }}
        QLabel {{ color: {t['text']}; font-weight: 500; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 12px; background: transparent; }}
        QLabel#info_status {{ color: {t.get('info_text', t['text'])}; font-weight: 400; font-size: 11px; padding-left: 4px; }}
        QLabel#progress {{ color: {t['accent']}; font-weight: 700; font-size: 13px; letter-spacing: 0.3px; }}
        QLabel#drop_overlay {{ color: {t['text']}; font-weight: 400; background-color: {t['bg']}; border: 2px dashed {t['border']}; border-radius: 16px; margin: 40px; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; }}
        QPushButton {{ background-color: {t['btn']}; color: {t['text']}; border: none; padding: 7px 18px; border-radius: 20px; font-weight: 700; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 12px; }}
        QPushButton:hover {{ background-color: {t['btn_hover']}; color: {t['accent']}; }}
        QPushButton:pressed {{ background-color: {t['accent']}; color: #000000; }}
        QPushButton#btn_play {{ background-color: {t['accent']}; color: #000000; border-radius: 20px; padding: 7px 22px; font-weight: 700; border: none; }}
        QPushButton#btn_play:hover {{ background-color: {t['btn_hover']}; color: {t['text']}; }}
        QPushButton#btn_play:disabled {{ background-color: {t['btn']}; color: {t['border']}; }}
        QPushButton#btn_close {{ padding: 0px; margin: 0px; border-radius: 13px; font-weight: 700; font-size: 12px; border: none; background: transparent; }}
        QPushButton#btn_close:hover {{ background-color: rgba(255,75,75,0.15); color: #FF4B4B; }}
        QComboBox, QLineEdit {{ background-color: {t['btn']}; color: {t['text']}; border: none; padding: 6px 12px; border-radius: 20px; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; }}
        QComboBox:hover {{ background-color: {t['btn_hover']}; }}
        QLineEdit:focus {{ background-color: {t['btn_hover']}; border: 1px solid {t['accent']}; }}
        QComboBox QAbstractItemView {{ background-color: {t['panel']}; color: {t['text']}; selection-background-color: {t['accent']}; selection-color: {t['highlight_text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 4px; outline: none; }}
        QSpinBox {{ background-color: {t['btn']}; color: {t['text']}; border: none; padding: 6px 8px; border-radius: 20px; min-width: 48px; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 12px; font-weight: 700; }}
        QSpinBox:hover, QSpinBox:focus {{ background-color: {t['btn_hover']}; border: 1px solid {t['accent']}; }}
        QSlider::groove:horizontal {{ background: {t['border']}; height: 4px; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {t['accent']}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ background: {t['text']}; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }}
        QSlider::handle:horizontal:hover {{ background: {t['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
        QSlider#book_slider {{ min-height: 18px; }}
        QSlider#book_slider:disabled {{ opacity: 0.4; }}
        QSlider#book_slider::groove:horizontal {{ background: {t['border']}; height: 4px; border-radius: 2px; }}
        QSlider#book_slider::sub-page:horizontal {{ background: {t['accent']}; border-radius: 2px; }}
        QSlider#book_slider::handle:horizontal {{ background: {t['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
        QCheckBox {{ color: {t['text']}; font-weight: 500; spacing: 6px; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 12px; }}
        QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 8px; border: 2px solid {t['border']}; background-color: {t['btn']}; }}
        QCheckBox::indicator:checked {{ background-color: {t['accent']}; border: 2px solid {t['accent']}; }}
        QComboBox::drop-down {{ border: none; width: 24px; }}
        QComboBox::down-arrow {{ image: url("{arrows['down']}"); width: 12px; height: 12px; }}
        QSpinBox::up-button {{ subcontrol-origin: border; subcontrol-position: top right; width: 18px; border-left: 1px solid {t['border']}; border-top-right-radius: 20px; background-color: {t['btn']}; }}
        QSpinBox::down-button {{ subcontrol-origin: border; subcontrol-position: bottom right; width: 18px; border-left: 1px solid {t['border']}; border-bottom-right-radius: 20px; background-color: {t['btn']}; }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: {t['btn_hover']}; }}
        QSpinBox::up-arrow {{ image: url("{arrows['up']}"); width: 10px; height: 10px; }}
        QSpinBox::down-arrow {{ image: url("{arrows['down']}"); width: 10px; height: 10px; }}
        """
        self.main_widget.setStyleSheet(app_style)

        if animate and old_pixmap:
            self.anim = QPropertyAnimation(self.overlay, b"opacity")
            self.anim.setDuration(300)
            self.anim.setStartValue(1.0)
            self.anim.setEndValue(0.0)
            self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.anim.finished.connect(self.overlay.deleteLater)
            self.anim.start()

    def toggle_search(self):
        if not hasattr(self, 'search_panel'): return
        if self.search_panel.height() == 0:
            self.search_animation.setStartValue(0)
            self.search_animation.setEndValue(45)
            self.search_animation.start()
            self.search_input.setFocus()
            self.search_input.selectAll()
        else:
            self.close_search()

    def close_search(self):
        self.search_animation.setStartValue(self.search_panel.height())
        self.search_animation.setEndValue(0)
        self.search_animation.start()
        self.search_input.clear()
        self.text_viewer.clear_highlights()
        self.lbl_search_count.setText("0 / 0")
        self.text_viewer.setFocus()

    def on_search_text_changed(self):
        if hasattr(self, 'search_debounce_timer'):
            self.search_debounce_timer.start()

    def _execute_search(self):
        query = self.search_input.text()
        total, current = self.text_viewer.highlight_search(query)
        self._update_search_label(total, current)

    def search_next(self):
        total, current = self.text_viewer.go_to_next_search()
        self._update_search_label(total, current)

    def search_prev(self):
        total, current = self.text_viewer.go_to_prev_search()
        self._update_search_label(total, current)

    def _update_search_label(self, total, current):
        if total == 0:
            self.lbl_search_count.setText("0 / 0")
        else:
            self.lbl_search_count.setText(f"{current} / {total}")

    def update_progress_ui(self, current_y, max_y):
        if not hasattr(self, 'progress_label') or not hasattr(self, 'book_slider'):
            return
        if max_y > 0:
            pct = (current_y / max_y) * 100
            pct_str = f"{pct:.1f}%"
            if self.progress_label.text() != pct_str:
                self.progress_label.setText(pct_str)
            if not getattr(self, 'block_slider_update', False):
                slider_val = int((current_y / max_y) * 1000)
                if self.book_slider.value() != slider_val:
                    self.book_slider.blockSignals(True)
                    self.book_slider.setValue(slider_val)
                    self.book_slider.blockSignals(False)
        else:
            if self.progress_label.text() != "0.0%":
                self.progress_label.setText("0.0%")
            if not getattr(self, 'block_slider_update', False) and self.book_slider.value() != 0:
                self.book_slider.setValue(0)
                
        current_path = getattr(self, 'current_pdf_path', "")
        if current_path and hasattr(self, 'recent_files'):
            for item in self.recent_files:
                if item.get("filepath") == current_path:
                    item["percentage"] = (current_y / max_y * 100.0) if max_y > 0 else 0.0
                    item["scroll_y"] = getattr(self.text_viewer, 'exact_y', 0.0)
                    break

        if not getattr(self, 'is_playing', False):
            self.track_position()

    def on_slider_pressed(self):
        self.block_slider_update = True

    def on_slider_moved(self, value):
        if self.text_viewer.scene.sceneRect().height() > 0:
            max_y = max(0, self.text_viewer.scene.sceneRect().height() - self.text_viewer.viewport().height())
            target_y = (value / 1000.0) * max_y
            self.text_viewer.scroll_to_y(target_y)
            pct = (value / 1000.0) * 100
            slider_width = self.book_slider.width()
            handle_x = int((value / 1000.0) * (slider_width - 20)) + 10
            global_pos = self.book_slider.mapToGlobal(QPoint(handle_x, -25))
            QToolTip.showText(global_pos, f"{pct:.1f}%", self.book_slider)

    def on_slider_released(self):
        self.block_slider_update = False
        self.track_position()

    def is_technical_text(self, text):
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        if len(lines) < 3: return False
        
        toc_indicators = 0
        for line in lines:
            if line.count('.') > 5 or '...' in line or '---' in line:
                toc_indicators += 1
            elif re.search(r'\d+$', line) and len(line) < 100:
                toc_indicators += 1
            elif re.search(r'^(глава|chapter|часть|part|оглавление|содержание|введение|заключение|prologue|epilogue)\b', line, re.IGNORECASE):
                toc_indicators += 1
                
        if toc_indicators / len(lines) >= 0.4: return True
        return False

    def close_file(self):
        if getattr(self, 'is_playing', False):
            self.toggle_playback()
        self.current_pdf_path = ""
        self.full_text = ""
        self.text_chunks = []
        self.emotion_map.clear()
        self.analyzing_chunks.clear()
        self.current_chunk = -1
        self.text_viewer.setPlainText("", app_ref=None)
        self.drop_overlay.show()
        self.text_viewer.hide()
        self.btn_play.setEnabled(False)
        self.btn_close_file.setVisible(False)
        self.book_slider.setValue(0)
        self.book_slider.setEnabled(False)
        self.progress_label.setText("0.0%")
        self.is_asking_ai = False
        
        self.ai_queue_timer.stop()
        self.tracker_timer.stop()
        self.scroll_timer.stop()
        
        if hasattr(self, 'btn_cancel_ai'):
            self.btn_cancel_ai.hide()
        if hasattr(self, 'info_status_label'):
            self.info_status_label.setText("")
        if hasattr(self, 'emotion_dot'):
            self.emotion_dot.set_emotion_color(0)
            self.emotion_dot.hide()
            
        self.current_doc_id += 1
        
        if hasattr(self, 'llama_worker'):
            self.llama_worker.queue.clear()
            
        for i in range(1, 13):
            self.target_volumes[i] = 0.0
            self.current_volumes[i] = 0.0
            if i in self.channels and self.channels[i]:
                self.channels[i].set_volume(0.0)
                
        if hasattr(self, 'title_bar'):
            self.title_bar.title_label.setText(LANG_DICT[self.lang]["window_title"])

    def load_pdf(self, filepath=None, restore_pct=0.0):

        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "Supported Files (*.pdf *.epub *.fb2 *.html *.htm);;"
                "PDF Files (*.pdf);;"
                "EPUB Files (*.epub);;"
                "FB2 Files (*.fb2);;"
                "HTML Files (*.html *.htm)"
            )
            if not filepath:
                return
        try:
            if hasattr(self, 'title_bar'):
                self.title_bar.title_label.setText(f"{LANG_DICT[self.lang]['window_title']} - [Loading...]")
                
            self.current_doc_id += 1
            self.btn_open.setEnabled(False)
            self.drop_overlay.hide()
            self.text_viewer.show()

            if hasattr(self, 'emotion_dot'):
                self.emotion_dot.show()

            if getattr(self, 'is_playing', False):
                self.is_playing = False
                
            self.scroll_timer.stop()
            self.tracker_timer.stop()
            self.ai_queue_timer.stop()
            self.current_active_emotion = 0
            
            for i in range(1, 13):
                self.target_volumes[i] = 0.0
                self.current_volumes[i] = 0.0
                if i in self.channels:
                    self.channels[i].set_volume(0.0)

            self.emotion_map.clear()
            self.analyzing_chunks.clear()
            self.emotion_history.clear()
            self.current_chunk = -1
            
            if hasattr(self, 'llama_worker'):
                self.llama_worker.queue.clear()
            if hasattr(self, 'emotion_dot'):
                self.emotion_dot.set_emotion_color(0)
                
            self.current_pdf_path = filepath
            self.btn_close_file.setVisible(True)
            self.btn_play.setEnabled(False)
            self.btn_play.setText(LANG_DICT[self.lang]["btn_play"])

            self.full_text = self._extract_text(filepath)
                
            self.text_viewer.setPlainText(self.full_text, app_ref=self)
            self.text_chunks = self.text_viewer.chunk_bounds
            self.text_viewer.scroll_to_top()
            self.book_slider.setValue(0)
            self.book_slider.setEnabled(True)
            self.apply_theme(animate=False)
            self.apply_font_and_layout()
            
            if restore_pct > 0.0:
                max_y = max(0, self.text_viewer.scene.sceneRect().height() - self.text_viewer.viewport().height())
                target_y = (restore_pct / 100.0) * max_y
                self.text_viewer.scroll_to_y(target_y)
                
            self.btn_open.setEnabled(True)
            self.btn_play.setEnabled(True)
            self.ai_queue_timer.start()
            
            file_name = os.path.basename(filepath)
            if hasattr(self, 'title_bar'):
                self.title_bar.title_label.setText(f"{LANG_DICT[self.lang]['window_title']} - {file_name}")
            self.update_status_title()
            
            self.update_recent_file(filepath)
            
        except Exception as e:
            print(f"[ERROR] File load error: {e}")
            self.btn_open.setEnabled(True)
            self.drop_overlay.show()
            self.text_viewer.hide()
            if hasattr(self, 'emotion_dot'):
                self.emotion_dot.hide()
            ext = os.path.splitext(filepath)[1].upper() if filepath else ''
            QMessageBox.critical(
                self, "YaRead",
                f"Failed to open {ext} file:\n{e}"
            )

    def toggle_playback(self):
        if not self.full_text:
            return
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.setText(LANG_DICT[self.lang]["btn_pause"])
            self.last_frame_time = time.perf_counter()
            self.scroll_timer.start()
            self.tracker_timer.start()
            self.track_position(force_update=True, instant=False)
        else:
            self.btn_play.setText(LANG_DICT[self.lang]["btn_play"])
            self.scroll_timer.stop()
            self.tracker_timer.stop()
            self.update_status_title()
            for i in range(1, 13):
                self.target_volumes[i] = 0.0

    def smooth_scroll(self):
        current_time = time.perf_counter()
        dt = current_time - self.last_frame_time
        if dt > 0.1: dt = 0.032
        self.last_frame_time = current_time
        
        if self.auto_scroll_cb.isChecked():
            speed_px_per_sec = self.speed_slider.value()
            dy = speed_px_per_sec * dt
            self.text_viewer.scroll_by(dy)
            
            max_y = max(0, self.text_viewer.scene.sceneRect().height() - self.text_viewer.viewport().height())
            if self.text_viewer.exact_y >= max_y and max_y > 0:
                self.toggle_playback()

    def track_position(self, force_update=False, instant=False):
        if getattr(self, 'is_asking_ai', False):
            return
        if not hasattr(self, 'text_viewer') or not getattr(self, 'text_chunks', []):
            return
            
        start_pos = self.text_viewer.get_text_position()
        new_chunk_idx = -1
        for i, (start, end) in enumerate(self.text_chunks):
            if start <= start_pos < end:
                new_chunk_idx = i
                break
                
        if new_chunk_idx == -1 and start_pos >= self.text_chunks[-1][1]:
            new_chunk_idx = len(self.text_chunks) - 1
            
        chunk_changed = (new_chunk_idx != getattr(self, 'current_chunk', -1) and new_chunk_idx != -1)
        
        if chunk_changed:
            self.current_chunk = new_chunk_idx
            if new_chunk_idx in self.emotion_map:
                detected_emo = self.emotion_map[new_chunk_idx]
                if detected_emo != 0:
                    self.emotion_history.append(detected_emo)
                    if len(self.emotion_history) > 3:
                        self.emotion_history.pop(0)
                        
        if not getattr(self, 'is_playing', False):
            return
            
        if self.current_chunk not in self.emotion_map:
            self.set_emotion(0, force=force_update, instant=instant)
        else:
            detected_emo = self.emotion_map[self.current_chunk]
            if detected_emo == 0:
                best_emo = 0
            else:
                best_emo = detected_emo
                if len(self.emotion_history) >= 2 and self.emotion_history[-1] == self.emotion_history[-2]:
                    best_emo = self.emotion_history[-1]
                elif len(self.emotion_history) >= 3 and self.emotion_history.count(detected_emo) >= 2:
                    best_emo = detected_emo
            self.set_emotion(best_emo, force=force_update, instant=instant)
            
        self.update_status_title()

    def process_ai_queue(self):
        if getattr(self, 'is_asking_ai', False) or (hasattr(self, 'ai_pause_cb') and self.ai_pause_cb.isChecked()):
            return
        if not getattr(self, 'text_chunks', []):
            return
        if not hasattr(self, 'llama_worker') or len(self.llama_worker.queue) >= 2:
            return
            
        total_chunks = len(self.text_chunks)
        target_chunk = -1
        priorities = []
        
        if getattr(self, 'current_chunk', -1) >= 0:
            priorities = [self.current_chunk, self.current_chunk + 1, self.current_chunk + 2]
        else:
            priorities = [0, 1, 2]
            
        for chunk in priorities:
            if 0 <= chunk < total_chunks and chunk not in self.emotion_map and chunk not in self.analyzing_chunks:
                target_chunk = chunk
                break
                
        if target_chunk == -1:
            for chunk in range(total_chunks):
                if chunk not in self.emotion_map and chunk not in self.analyzing_chunks:
                    target_chunk = chunk
                    break
                    
        if target_chunk != -1:
            self.trigger_ai_analysis(target_chunk)

    def trigger_ai_analysis(self, chunk_idx):
        start_char, end_char = self.text_chunks[chunk_idx]
        raw_chunk = self.full_text[start_char:end_char].strip()

        if self.is_technical_text(raw_chunk):
            self.emotion_map[chunk_idx] = 0
            self.update_status_title()
            if getattr(self, 'is_playing', False) and getattr(self, 'current_chunk', -1) == chunk_idx:
                self.track_position()
            return
            
        if len(raw_chunk) > 800:
            processed_chunk = raw_chunk[:400] + "\n...[ПРОПУСК]...\n" + raw_chunk[-400:]
        else:
            processed_chunk = raw_chunk
            
        if len(processed_chunk) < 20:
            self.emotion_map[chunk_idx] = 1
            return
            
        self.analyzing_chunks.add(chunk_idx)
        if hasattr(self, 'llama_worker'):
            self.llama_worker.add_task("emotion", processed_chunk, chunk_idx, self.current_doc_id)
        self.update_status_title()

    def on_emotion_detected(self, chunk_idx, emotion_id, doc_id):
        if doc_id != getattr(self, 'current_doc_id', 0):
            return
        self.emotion_map[chunk_idx] = emotion_id
        if getattr(self, 'is_playing', False) and getattr(self, 'current_chunk', -1) == chunk_idx:
            self.track_position(force_update=True)

    def on_ai_error(self, error_msg, doc_id):
        if doc_id != getattr(self, 'current_doc_id', 0) and doc_id != 0:
            return
        print(f"[AI WARNING] {error_msg}")
        if hasattr(self, 'info_status_label'):
            self.info_status_label.setText(f"[{error_msg}]")

    def on_ai_status(self, msg):
        if hasattr(self, 'info_status_label'):
            self.info_status_label.setText(msg)

    def on_ai_finished(self, chunk_idx, doc_id):
        if doc_id != getattr(self, 'current_doc_id', 0):
            return
        if chunk_idx in self.analyzing_chunks:
            self.analyzing_chunks.remove(chunk_idx)
        self.update_status_title()

    def update_status_title(self):
        if not hasattr(self, 'text_chunks') or not self.text_chunks:
            return
            
        total_chunks = len(self.text_chunks)
        analyzed_count = min(len(self.emotion_map), total_chunks)
        t = LANG_DICT[self.lang]
        status = ""
        
        if getattr(self, 'is_asking_ai', False):
            status = t['status_asking']
            if hasattr(self, 'emotion_dot'):
                self.emotion_dot.set_emotion_color(0)
        elif hasattr(self, 'ai_pause_cb') and self.ai_pause_cb.isChecked():
            status = t['status_ai_paused']
            if hasattr(self, 'emotion_dot'):
                self.emotion_dot.set_emotion_color(0)
        else:
            if getattr(self, 'is_playing', False):
                if getattr(self, 'current_chunk', -1) in self.emotion_map:
                    em_id = getattr(self, 'current_active_emotion', 0) if getattr(self, 'current_active_emotion', 0) != 0 else self.emotion_map[self.current_chunk]
                    em_name = t['emotions'].get(em_id, str(em_id))
                    status = f"{t['status_reading']} {em_name}]"
                    if hasattr(self, 'emotion_dot'):
                        self.emotion_dot.set_emotion_color(em_id)
                elif getattr(self, 'current_chunk', -1) in self.analyzing_chunks:
                    status = t['status_thinking']
                    if hasattr(self, 'emotion_dot'):
                        self.emotion_dot.set_emotion_color(0)
                else:
                    status = t['status_waiting']
                    if hasattr(self, 'emotion_dot'):
                        self.emotion_dot.set_emotion_color(0)
            else:
                status = t['status_pause']
                if hasattr(self, 'emotion_dot'):
                    self.emotion_dot.set_emotion_color(0)
                    
        progress = f"({t['status_preloaded']} {analyzed_count}/{total_chunks})"
        if hasattr(self, 'info_status_label'):
            self.info_status_label.setText(f"{status} {progress}")

    def update_master_volume(self):
        if not hasattr(self, 'volume_slider'): return
        master_vol = self.volume_slider.value() / 100.0
        if getattr(self, 'current_active_emotion', 0) != 0:
            self.target_volumes[self.current_active_emotion] = master_vol

    def set_emotion(self, emotion_id, force=False, instant=False):
        if emotion_id == getattr(self, 'current_active_emotion', -1) and not force:
            return
            
        master_vol = self.volume_slider.value() / 100.0 if emotion_id != 0 else 0.0
        for i in range(1, 13):
            self.target_volumes[i] = master_vol if i == emotion_id else 0.0
            if instant:
                self.current_volumes[i] = self.target_volumes[i]
                if i in self.channels and self.channels[i]:
                    self.channels[i].set_volume(self.current_volumes[i])

        self.current_active_emotion = emotion_id

    def process_audio_fade(self):
        for i in range(1, 13):
            target = self.target_volumes[i]
            current = self.current_volumes[i]
            channel = self.channels.get(i)

            if not channel: continue
            
            if abs(current - target) > 0.001:
                if current > target: 
                    current = max(current - 0.025, target)
                else: 
                    current = min(current + 0.008, target)
                self.current_volumes[i] = current
                channel.set_volume(current)

    def closeEvent(self, event):
        self.save_settings()
        if hasattr(self, 'fade_timer'): self.fade_timer.stop()
        if hasattr(self, 'scroll_timer'): self.scroll_timer.stop()
        if hasattr(self, 'tracker_timer'): self.tracker_timer.stop()
        if hasattr(self, 'ai_queue_timer'): self.ai_queue_timer.stop()
        
        if hasattr(self, 'llama_worker') and self.llama_worker is not None:
            self.llama_worker.running = False
            self.llama_worker.quit()
            if not self.llama_worker.wait(1500):
                self.llama_worker.terminate()
                self.llama_worker.wait()
                
        pygame.mixer.quit()
        event.accept()

if __name__ == '__main__':
    window = YaReadApp()

    if not app_icon.isNull():
        window.setWindowIcon(app_icon)

    window.setWindowOpacity(0.0)
    
    splash.finish(window)
    window.show()

    try:
        import ctypes
        hwnd = int(window.winId())
        ICON_SMALL, ICON_BIG = 0, 1
        WM_SETICON = 0x0080
        hicon = ctypes.windll.user32.LoadImageW(
            None,
            icon_path if os.path.exists(icon_path) else None,
            1,
            0, 0,
            0x0010 | 0x0040 
        )
        if hicon:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
    except Exception as e:
        print(f"[WARN] Taskbar icon WinAPI fallback failed: {e}")

    fade_in = QPropertyAnimation(window, b"windowOpacity")
    fade_in.setDuration(350)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
    fade_in.start()

    sys.exit(app.exec())