__version__ = "1.0.0"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import ast
import operator

Window.clearcolor = (0.02, 0.02, 0.02, 1)

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def calculate(expr):
    def run(node):
        if isinstance(node, ast.Expression):
            return run(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            a, b = run(node.left), run(node.right)
            if isinstance(node.op, ast.Div) and b == 0:
                raise ZeroDivisionError
            return OPS[type(node.op)](a, b)
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](run(node.operand))
        raise ValueError("Invalid expression")
    return run(ast.parse(expr, mode="eval"))

class RoundButton(Button):
    def __init__(self, bg, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = "25sp"
        with self.canvas.before:
            Color(*bg)
            self.shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(50)]
            )
        self.bind(pos=self.draw_shape, size=self.draw_shape)

    def draw_shape(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size

class CalculatorApp(App):
    def build(self):
        self.title = "iCalc"
        self.expr = ""
        root = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(28), dp(12), dp(12)],
            spacing=dp(12)
        )

        self.display = Label(
            text="0", font_size="54sp", halign="right",
            valign="middle", color=(1, 1, 1, 1),
            size_hint_y=0.27
        )
        self.display.bind(size=self.align_display)
        root.add_widget(self.display)

        grid = GridLayout(cols=4, spacing=dp(9), size_hint_y=0.73)
        rows = [
            [("AC", "light"), ("+/-", "light"), ("%", "light"), ("÷", "orange")],
            [("7", "dark"), ("8", "dark"), ("9", "dark"), ("×", "orange")],
            [("4", "dark"), ("5", "dark"), ("6", "dark"), ("−", "orange")],
            [("1", "dark"), ("2", "dark"), ("3", "dark"), ("+", "orange")],
            [("⌫", "dark"), ("0", "dark"), (".", "dark"), ("=", "orange")],
        ]
        colors = {
            "light": (0.65, 0.65, 0.65, 1),
            "dark": (0.20, 0.20, 0.20, 1),
            "orange": (1.0, 0.58, 0.0, 1),
        }
        for row in rows:
            for label, kind in row:
                btn = RoundButton(
                    colors[kind], text=label,
                    font_size="23sp"
                )
                btn.bind(on_release=self.press)
                grid.add_widget(btn)
        root.add_widget(grid)
        return root

    def align_display(self, *_):
        self.display.text_size = self.display.size

    def press(self, btn):
        key = btn.text
        if key == "AC":
            self.expr = ""
        elif key == "⌫":
            self.expr = self.expr[:-1]
        elif key == "+/-":
            if self.expr and self.expr[0] == "-":
                self.expr = self.expr[1:]
            elif self.expr:
                self.expr = "-" + self.expr
        elif key == "%":
            try:
                self.expr = str(calculate(self.expr) / 100)
            except Exception:
                pass
        elif key == "=":
            try:
                self.expr = str(calculate(
                    self.expr.replace("×", "*")
                             .replace("÷", "/")
                             .replace("−", "-")
                ))
                if self.expr.endswith(".0"):
                    self.expr = self.expr[:-2]
            except Exception:
                self.expr = "Error"
        else:
            if self.expr == "Error":
                self.expr = ""
            self.expr += key

        self.display.text = self.expr or "0"

if __name__ == "__main__":
    CalculatorApp().run()
