import pyglet.text
from pyglet import shapes


class button:
    def __init__(self, label="Button", x=0, y=0, w=10, h=10):
        self.rectangle = shapes.Rectangle(x, y, width=w, height=h,color=(25,25,25))
        self.rectangle.anchor_x = w // 2
        self.rectangle.anchor_y = h // 2
        self.label = pyglet.text.Label(label, font_name="Calibri", font_size=20, x=x, y=y,anchor_x="center",anchor_y="center",color=(200,200,200,255))

    def draw_self(self):
        self.rectangle.draw()
        self.label.draw()

    def press(self, mx, my):
        if (mx, my) in self.rectangle:
            self.rectangle.color = (50, 150, 50)

    def release(self, mx, my):
        if (mx, my) in self.rectangle:
            self.clicked()
            self.rectangle.color = (25, 25, 25)


    def mouse(self, mx, my):
        if (mx, my) in self.rectangle:
            self.rectangle.color = (50, 50, 50)
        else:
            self.rectangle.color = (25, 25, 25)
