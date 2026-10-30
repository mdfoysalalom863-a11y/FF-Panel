# main.py
# Free Fire Panel - Kivy Overlay App
# APK: buildozer init && buildozer android debug

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.widget import Widget
import threading
import time

# ── Theme Colors ──────────────────────────────────────────────
BG_DARK      = (0.05, 0.05, 0.10, 0.95)
BG_CARD      = (0.10, 0.10, 0.18, 1)
ACCENT_RED   = (0.85, 0.10, 0.10, 1)
ACCENT_GOLD  = (1.00, 0.75, 0.00, 1)
TEXT_WHITE   = (1, 1, 1, 1)
TEXT_GREY    = (0.6, 0.6, 0.6, 1)
SLIDER_ACTIVE = (0.85, 0.10, 0.10, 1)

# ── Hack State ────────────────────────────────────────────────
class HackState:
    damage_mult   = 2.0   # x2
    accuracy_mult = 2.0   # x2
    reload_mult   = 2.0   # x2 speed
    firerate_mult = 2.0   # x2
    active        = False
    vpn_connected = False

state = HackState()


# ── Rounded Card Widget ───────────────────────────────────────
class CardBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        with self.canvas.before:
            Color(*BG_CARD)
            self.rect = RoundedRectangle(pos=self.pos,
                                         size=self.size,
                                         radius=[dp(12)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self.rect.pos  = self.pos
        self.rect.size = self.size


# ── Slider Row ────────────────────────────────────────────────
def make_slider_row(label_text, initial=2.0, min_v=1.0, max_v=5.0,
                    on_change=None):
    row = BoxLayout(orientation='horizontal',
                    size_hint_y=None, height=dp(48),
                    spacing=dp(8))

    lbl = Label(text=label_text,
                size_hint_x=0.38,
                font_size=dp(12),
                color=TEXT_WHITE,
                halign='left',
                valign='middle')
    lbl.bind(size=lbl.setter('text_size'))

    sl = Slider(min=min_v, max=max_v, value=initial,
                size_hint_x=0.40,
                cursor_size=(dp(18), dp(18)))

    val_lbl = Label(text=f'x{initial:.1f}',
                    size_hint_x=0.22,
                    font_size=dp(12),
                    color=ACCENT_GOLD,
                    bold=True)

    def _on_val(instance, val):
        val_lbl.text = f'x{val:.1f}'
        if on_change:
            on_change(val)

    sl.bind(value=_on_val)

    row.add_widget(lbl)
    row.add_widget(sl)
    row.add_widget(val_lbl)
    return row


# ── Main Panel Screen ─────────────────────────────────────────
class PanelScreen(FloatLayout):
    def __init__(self, toggle_callback, **kwargs):
        super().__init__(**kwargs)
        self.toggle_callback = toggle_callback
        self._build_ui()

    def _build_ui(self):
        # dark background
        with self.canvas.before:
            Color(*BG_DARK)
            self.bg = RoundedRectangle(pos=self.pos,
                                       size=self.size,
                                       radius=[dp(16)])
        self.bind(pos=lambda *_: setattr(self.bg, 'pos', self.pos),
                  size=lambda *_: setattr(self.bg, 'size', self.size))

        root = BoxLayout(orientation='vertical',
                         padding=dp(16), spacing=dp(10))

        # ── Header ──
        hdr = BoxLayout(orientation='horizontal',
                        size_hint_y=None, height=dp(50))
        title = Label(text='[b][color=ff2222]FREE FIRE[/color] PANEL[/b]',
                      markup=True, font_size=dp(18),
                      color=TEXT_WHITE, halign='left')
        title.bind(size=title.setter('text_size'))

        self.status_dot = Label(text='● OFFLINE',
                                font_size=dp(11),
                                color=TEXT_GREY,
                                halign='right')
        self.status_dot.bind(size=self.status_dot.setter('text_size'))

        hdr.add_widget(title)
        hdr.add_widget(self.status_dot)
        root.add_widget(hdr)

        # ── VPN Connect Button ──
        self.connect_btn = Button(
            text='▶  CONNECT PANEL',
            size_hint_y=None, height=dp(48),
            background_normal='',
            background_color=ACCENT_RED,
            font_size=dp(14),
            bold=True,
            color=TEXT_WHITE
        )
        self.connect_btn.bind(on_press=self._toggle_connect)
        root.add_widget(self.connect_btn)

        # ── Scrollable sliders ──
        scroll = ScrollView(size_hint=(1, 1))
        inner = BoxLayout(orientation='vertical',
                          spacing=dp(10),
                          size_hint_y=None)
        inner.bind(minimum_height=inner.setter('height'))

        # Damage Card
        dmg_card = CardBox(size_hint_y=None, height=dp(90))
        dmg_card.add_widget(Label(
            text='💥  DAMAGE MULTIPLIER',
            font_size=dp(12), bold=True,
            color=ACCENT_GOLD,
            size_hint_y=None, height=dp(20),
            halign='left'
        ))
        dmg_card.add_widget(make_slider_row(
            'Damage ×', 2.0,
            on_change=lambda v: setattr(state, 'damage_mult', v)
        ))
        inner.add_widget(dmg_card)

        # Accuracy Card
        acc_card = CardBox(size_hint_y=None, height=dp(90))
        acc_card.add_widget(Label(
            text='🎯  ACCURACY BOOST',
            font_size=dp(12), bold=True,
            color=ACCENT_GOLD,
            size_hint_y=None, height=dp(20),
            halign='left'
        ))
        acc_card.add_widget(make_slider_row(
            'Accuracy ×', 2.0,
            on_change=lambda v: setattr(state, 'accuracy_mult', v)
        ))
        inner.add_widget(acc_card)

        # Reload Card
        rel_card = CardBox(size_hint_y=None, height=dp(90))
        rel_card.add_widget(Label(
            text='🔄  RELOAD SPEED',
            font_size=dp(12), bold=True,
            color=ACCENT_GOLD,
            size_hint_y=None, height=dp(20),
            halign='left'
        ))
        rel_card.add_widget(make_slider_row(
            'Reload ×', 2.0,
            on_change=lambda v: setattr(state, 'reload_mult', v)
        ))
        inner.add_widget(rel_card)

        # Fire Rate Card
        fr_card = CardBox(size_hint_y=None, height=dp(90))
        fr_card.add_widget(Label(
            text='🔥  RATE OF FIRE',
            font_size=dp(12), bold=True,
            color=ACCENT_GOLD,
            size_hint_y=None, height=dp(20),
            halign='left'
        ))
        fr_card.add_widget(make_slider_row(
            'Fire Rate ×', 2.0,
            on_change=lambda v: setattr(state, 'firerate_mult', v)
        ))
        inner.add_widget(fr_card)

        scroll.add_widget(inner)
        root.add_widget(scroll)

        # ── Close Panel Button ──
        close_btn = Button(
            text='✕  CLOSE PANEL',
            size_hint_y=None, height=dp(40),
            background_normal='',
            background_color=(0.15, 0.15, 0.25, 1),
            font_size=dp(12),
            color=TEXT_GREY
        )
        close_btn.bind(on_press=lambda _: self.toggle_callback())
        root.add_widget(close_btn)

        self.add_widget(root)

    def _toggle_connect(self, *_):
        state.vpn_connected = not state.vpn_connected
        state.active = state.vpn_connected

        if state.vpn_connected:
            self.connect_btn.text = '⏹  DISCONNECT'
            self.connect_btn.background_color = (0.10, 0.55, 0.10, 1)
            self.status_dot.text  = '● ACTIVE'
            self.status_dot.color = (0.1, 0.9, 0.1, 1)
        else:
            self.connect_btn.text = '▶  CONNECT PANEL'
            self.connect_btn.background_color = ACCENT_RED
            self.status_dot.text  = '● OFFLINE'
            self.status_dot.color = TEXT_GREY


# ── Floating Action Button (overlay over game) ────────────────
class FloatingButton(Widget):
    def __init__(self, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.size_hint     = (None, None)
        self.size          = (dp(54), dp(54))
        self.pos           = (Window.width - dp(70), dp(200))
        self._dragging     = False
        self._drag_offset  = (0, 0)
        self.on_tap        = on_tap
        self._is_open      = False

        with self.canvas:
            Color(*ACCENT_RED)
            self.circle = RoundedRectangle(pos=self.pos,
                                           size=self.size,
                                           radius=[dp(27)])

        self.lbl = Label(
            text='FF',
            bold=True,
            font_size=dp(14),
            color=TEXT_WHITE,
            size=self.size,
            pos=self.pos
        )
        self.add_widget(self.lbl)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.circle.pos  = self.pos
        self.circle.size = self.size
        self.lbl.pos     = self.pos
        self.lbl.size    = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging    = True
            self._drag_offset = (touch.x - self.x, touch.y - self.y)
            self._touch_start = touch.pos
            return True

    def on_touch_move(self, touch):
        if self._dragging:
            nx = touch.x - self._drag_offset[0]
            ny = touch.y - self._drag_offset[1]
            # clamp inside window
            nx = max(0, min(Window.width  - self.width,  nx))
            ny = max(0, min(Window.height - self.height, ny))
            self.pos = (nx, ny)
            return True

    def on_touch_up(self, touch):
        if self._dragging:
            self._dragging = False
            # tap = moved < 10px
            dx = abs(touch.x - self._touch_start[0])
            dy = abs(touch.y - self._touch_start[1])
            if dx < 10 and dy < 10:
                self.on_tap()
            return True

    def set_active(self, active):
        self.canvas.clear()
        with self.canvas:
            Color(*(0.10, 0.55, 0.10, 1) if active else ACCENT_RED)
            self.circle = RoundedRectangle(pos=self.pos,
                                           size=self.size,
                                           radius=[dp(27)])
        self.lbl.text = '⚡' if active else 'FF'
        self._sync()


# ── Root Layout (holds fab + panel) ──────────────────────────
class RootLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._panel_open = False

        # Floating button
        self.fab = FloatingButton(on_tap=self._toggle_panel)
        self.add_widget(self.fab)

        # Panel (hidden initially)
        pw = min(Window.width * 0.88, dp(340))
        ph = min(Window.height * 0.78, dp(560))
        self.panel = PanelScreen(
            toggle_callback=self._toggle_panel,
            size_hint=(None, None),
            size=(pw, ph),
            pos=((Window.width - pw) / 2,
                 (Window.height - ph) / 2),
            opacity=0
        )
        self.add_widget(self.panel)

    def _toggle_panel(self, *_):
        self._panel_open = not self._panel_open
        target_op = 1 if self._panel_open else 0
        anim = Animation(opacity=target_op, duration=0.25)
        anim.start(self.panel)
        self.fab.set_active(state.active)


# ── App Entry ─────────────────────────────────────────────────
class FreefirePanel(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 0)   # transparent window
        self.title = 'FF Panel'
        return RootLayout()


if __name__ == '__main__':
    FreefirePanel().run()
