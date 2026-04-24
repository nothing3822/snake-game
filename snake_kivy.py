"""
SNAKE GAME - Python Kivy
Android compatible - Build with Buildozer
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from random import randint

# Colors
BG_COLOR = get_color_from_hex('#0a0a0f')
GRID_COLOR = get_color_from_hex('#0f0f1a')
HEAD_COLOR = get_color_from_hex('#00ff88')
BODY_COLOR = get_color_from_hex('#00cc66')
FOOD_COLOR = get_color_from_hex('#ff3366')
TEXT_COLOR = get_color_from_hex('#00ff88')

GRID_SIZE = 20
COLS = 20
ROWS = 20

class SnakeGame(Widget):
    def __init__(self, on_game_over, **kwargs):
        super().__init__(**kwargs)
        self.on_game_over = on_game_over
        self.cell_w = 0
        self.cell_h = 0
        self.snake = []
        self.food = None
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.speed = 0.15
        self.running = False
        self._clock = None
        self._touch_start = None
        self.bind(size=self._on_size)

    def _on_size(self, *args):
        self.cell_w = self.width / COLS
        self.cell_h = self.height / ROWS
        if self.running:
            self.draw()

    def start(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.speed = 0.15
        self.running = True
        self._spawn_food()
        if self._clock:
            self._clock.cancel()
        self._clock = Clock.schedule_interval(self._tick, self.speed)
        self.draw()

    def _spawn_food(self):
        while True:
            pos = (randint(0, COLS-1), randint(0, ROWS-1))
            if pos not in self.snake:
                self.food = pos
                break

    def _tick(self, dt):
        if not self.running:
            return
        self.direction = self.next_direction
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        # Wall collision
        if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS:
            self._game_over()
            return

        # Self collision
        if new_head in self.snake:
            self._game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += self.level * 10
            self._spawn_food()
            # Level up
            if self.score >= self.level * 50:
                self.level += 1
                self.speed = max(0.06, 0.15 - (self.level - 1) * 0.015)
                if self._clock:
                    self._clock.cancel()
                self._clock = Clock.schedule_interval(self._tick, self.speed)
        else:
            self.snake.pop()

        self.draw()

    def draw(self):
        self.canvas.clear()
        cw = self.cell_w
        ch = self.cell_h
        ox = self.x
        oy = self.y

        with self.canvas:
            # Background
            Color(*GRID_COLOR)
            Rectangle(pos=(ox, oy), size=(self.width, self.height))

            # Grid dots
            Color(1, 1, 1, 0.04)
            for x in range(COLS):
                for y in range(ROWS):
                    cx = ox + x * cw + cw/2 - 1
                    cy = oy + y * ch + ch/2 - 1
                    Rectangle(pos=(cx, cy), size=(2, 2))

            # Food
            Color(*FOOD_COLOR)
            fx = ox + self.food[0] * cw + 2
            fy = oy + self.food[1] * ch + 2
            Ellipse(pos=(fx, fy), size=(cw-4, ch-4))

            # Snake body
            total = len(self.snake)
            for i, seg in enumerate(reversed(self.snake)):
                idx = total - 1 - i
                ratio = 1 - (idx / total) * 0.6
                if idx == 0:
                    Color(*HEAD_COLOR)
                    pad = 1
                else:
                    Color(0, ratio * 0.8, ratio * 0.4, ratio)
                    pad = 2
                sx = ox + seg[0] * cw + pad
                sy = oy + seg[1] * ch + pad
                Rectangle(pos=(sx, sy), size=(cw - pad*2, ch - pad*2))

            # Eyes on head
            Color(0.04, 0.04, 0.06)
            hx, hy = self.snake[0]
            ex = ox + hx * cw
            ey = oy + hy * ch
            dx, dy = self.direction
            ep = 3
            if dx == 1:   # right
                Rectangle(pos=(ex+cw*0.65, ey+ch*0.2), size=(ep, ep))
                Rectangle(pos=(ex+cw*0.65, ey+ch*0.65), size=(ep, ep))
            elif dx == -1: # left
                Rectangle(pos=(ex+cw*0.2, ey+ch*0.2), size=(ep, ep))
                Rectangle(pos=(ex+cw*0.2, ey+ch*0.65), size=(ep, ep))
            elif dy == 1:  # up
                Rectangle(pos=(ex+cw*0.2, ey+ch*0.65), size=(ep, ep))
                Rectangle(pos=(ex+cw*0.65, ey+ch*0.65), size=(ep, ep))
            else:          # down
                Rectangle(pos=(ex+cw*0.2, ey+ch*0.2), size=(ep, ep))
                Rectangle(pos=(ex+cw*0.65, ey+ch*0.2), size=(ep, ep))

    def _game_over(self):
        self.running = False
        if self._clock:
            self._clock.cancel()
        self.on_game_over(self.score, self.level)

    def on_touch_down(self, touch):
        self._touch_start = (touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if not self._touch_start or not self.running:
            return True
        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch_start[1]
        if abs(dx) < 20 and abs(dy) < 20:
            return True

        if abs(dx) > abs(dy):
            nd = (1, 0) if dx > 0 else (-1, 0)
        else:
            nd = (0, 1) if dy > 0 else (0, -1)

        # Prevent reverse
        if nd[0] != -self.direction[0] or nd[1] != -self.direction[1]:
            self.next_direction = nd

        self._touch_start = None
        return True


class SnakeApp(App):
    def build(self):
        Window.clearcolor = BG_COLOR
        self.title = 'SNAKE'
        self.best = 0
        self.root_layout = FloatLayout()
        self._build_ui()
        return self.root_layout

    def _build_ui(self):
        self.root_layout.clear_widgets()
        layout = FloatLayout()

        # Title
        title = Label(
            text='[b]SNAKE[/b]',
            markup=True,
            font_size='28sp',
            color=HEAD_COLOR,
            size_hint=(1, None),
            height=50,
            pos_hint={'x': 0, 'top': 1}
        )
        layout.add_widget(title)

        # Score bar
        self.score_label = Label(
            text='SCORE: 0   BEST: 0   LVL: 1',
            font_size='11sp',
            color=TEXT_COLOR,
            size_hint=(1, None),
            height=30,
            pos_hint={'x': 0, 'top': 0.92}
        )
        layout.add_widget(self.score_label)

        # Game widget
        self.game = SnakeGame(
            on_game_over=self._on_game_over,
            size_hint=(None, None),
            size=(min(Window.width, Window.height) - 20,
                  min(Window.width, Window.height) - 20),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        layout.add_widget(self.game)

        # D-pad controls
        pad_size = 55
        pad_y = 0.12
        pad_cx = 0.5

        directions = [
            ('▲', pad_cx - 0.08, pad_y + 0.09, (0, 1)),
            ('▼', pad_cx - 0.08, pad_y - 0.01, (0, -1)),
            ('◀', pad_cx - 0.18, pad_y + 0.04, (-1, 0)),
            ('▶', pad_cx + 0.02, pad_y + 0.04, (1, 0)),
        ]

        for text, rx, ry, d in directions:
            btn = Button(
                text=text,
                font_size='18sp',
                size_hint=(None, None),
                size=(pad_size, pad_size),
                pos_hint={'center_x': rx + 0.08, 'center_y': ry},
                background_color=(0, 0, 0, 0),
                color=TEXT_COLOR,
                background_normal='',
            )
            btn.direction = d
            btn.bind(on_press=self._on_dpad)
            layout.add_widget(btn)

        # Start overlay
        self.overlay = FloatLayout(
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )

        with self.overlay.canvas.before:
            Color(0.04, 0.04, 0.06, 0.9)
            self.overlay_rect = Rectangle(size=Window.size, pos=(0, 0))

        self.overlay_title = Label(
            text='[b]SNAKE[/b]',
            markup=True,
            font_size='32sp',
            color=HEAD_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
        self.overlay.add_widget(self.overlay_title)

        self.overlay_msg = Label(
            text='SWIPE OR USE\nD-PAD TO MOVE\n\nEAT FOOD TO GROW\nDON\'T HIT THE WALLS!',
            font_size='13sp',
            color=(0.7, 0.7, 0.8, 1),
            halign='center',
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.overlay.add_widget(self.overlay_msg)

        self.start_btn = Button(
            text='START',
            font_size='16sp',
            size_hint=(0.45, None),
            height=50,
            pos_hint={'center_x': 0.5, 'center_y': 0.32},
            background_color=(0, 0.8, 0.4, 1),
            color=(0.04, 0.04, 0.06, 1),
            bold=True
        )
        self.start_btn.bind(on_press=self._start_game)
        self.overlay.add_widget(self.start_btn)

        layout.add_widget(self.overlay)

        # Keyboard support
        Window.bind(on_key_down=self._on_key)

        self.root_layout.add_widget(layout)
        self.main_layout = layout

    def _on_dpad(self, btn):
        if not self.game.running:
            return
        nd = btn.direction
        d = self.game.direction
        if nd[0] != -d[0] or nd[1] != -d[1]:
            self.game.next_direction = nd

    def _on_key(self, window, key, *args):
        key_map = {273: (0,1), 274: (0,-1), 276: (-1,0), 275: (1,0)}
        if key in key_map and self.game.running:
            nd = key_map[key]
            d = self.game.direction
            if nd[0] != -d[0] or nd[1] != -d[1]:
                self.game.next_direction = nd

    def _start_game(self, *args):
        self.overlay.opacity = 0
        self.overlay.disabled = True
        self.game.start()
        # Update score periodically
        Clock.schedule_interval(self._update_score, 0.1)

    def _update_score(self, dt):
        if not self.game.running:
            return False
        s = self.game.score
        l = self.game.level
        b = self.best
        self.score_label.text = f'SCORE: {s}   BEST: {b}   LVL: {l}'

    def _on_game_over(self, score, level):
        if score > self.best:
            self.best = score
        self.overlay.opacity = 1
        self.overlay.disabled = False
        self.overlay_title.text = '[b]GAME OVER[/b]'
        self.overlay_msg.text = f'SCORE: {score}\n\nBEST: {self.best}\n\nLEVEL: {level}'
        self.start_btn.text = 'RETRY'
        self.score_label.text = f'SCORE: {score}   BEST: {self.best}   LVL: {level}'


if __name__ == '__main__':
    SnakeApp().run()
