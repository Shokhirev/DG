import random

import pyglet
from pyglet.window import key

from Map import dgMap
from button import button
from Entity import Entity


def getEntity(name, x, y, dgmap):
    ent = Entity(img=images[name], x=x, y=y, dgmap=dgmap)
    ent.setStates(defs[name])
    return ent


def getEntity2(name, owner):
    ent = Entity(img=images[name])
    ent.setStates(defs[name])
    owner.take(ent)
    return ent


# Pyglet stuff
display = pyglet.canvas.Display()
screen = display.get_default_screen()
screen_width = screen.width
screen_height = screen.height
window = pyglet.window.Window(fullscreen=False, resizable=True, width=screen_width // 2, height=screen_height // 2)
fps_display = pyglet.window.FPSDisplay(window=window)
keys = key.KeyStateHandler()
window.push_handlers(keys)
# event_logger = pyglet.window.event.WindowEventLogger()
# window.push_handlers(event_logger)
pyglet.resource.path = ['images', 'definitions']
pyglet.resource.reindex()

# Labels
title = pyglet.text.Label("DungeonGen", font_name="Calibri", font_size=80, x=window.width // 2, y=window.height // 2,
                          anchor_x="center")
subtitle = pyglet.text.Label("An AI dungeon by Max Shok 2024", font_name="Calibri", font_size=20, x=window.width // 2,
                             y=window.height // 2 - 80, anchor_x="center")


# Buttons
class start_btn(button):
    def clicked(self):
        window.state = 2


class exit_btn(button):
    def clicked(self):
        pyglet.app.exit()


start_b = start_btn(label="Start", x=window.width // 2, y=200, w=200, h=50)
exit_b = exit_btn(label="Exit", x=window.width // 2, y=100, w=200, h=50)

# Game stuff
window.state = 0  # 0=title, 1=menu, 2=game
drawFPS = True

imageTiles = pyglet.resource.image('tiles.png')
imageMap = {(15, 9): "grass",
            (4, 80): "player",
            (0, 7): "wall",
            (47, 82): "robe"}  # from top left
images = dict()
for k, v in imageMap.items():
    (x, y) = k
    subImg = imageTiles.get_region(x * 32, (94 - y) * 32, 32, 32)
    images[v] = subImg

defsFile = pyglet.resource.file('defs.txt')
defs = dict()
cdef = dict()
while True:
    line = defsFile.readline()
    if not line:
        break
    line = str(line).split('\\r')[0].split('b\'')[1]

    if ":" in line:
        split = line.split(':')
        if len(cdef) > 0:
            defs[cdef['name']] = cdef
        cdef = dict()
        # assume the type is already in the defs
        if len(split[1]) > 0 and split[1] in defs.keys():
            cdef.update(defs[split[1]])
        cdef['name'] = split[0]
        cdef['type'] = split[1]
    else:
        if "\\t" in line:
            split = line.split('\\t')
            cdef[split[0]] = split[1]

defs[cdef['name']] = cdef  # put the last


# Maps
def generateMaps(param):
    res = dict()
    for i in range(param):
        m = dgMap(w=40, h=22)
        for x in range(m.w):
            for y in range(m.h):
                grass = getEntity(name="grass", dgmap=m, x=x, y=y)
                r = random.randint(0, 100)
                if r < 20:
                    wall = getEntity(name="wall", dgmap=m, x=x, y=y)
        res[i] = m
    return res


# Logic
batch = pyglet.graphics.Batch()  # for particle effects and other shiz that we don't need logic for.
maps = generateMaps(1)
currentMap = maps[0]



player = getEntity(name="player", x=20, y=20, dgmap=currentMap)
robe = getEntity2(name="robe", owner=player)
player.take(robe)
player.equip(robe)


def drawTitle():
    window.clear()
    title.draw()
    subtitle.draw()


def drawMenu():
    window.clear()
    start_b.draw_self()
    exit_b.draw_self()


def drawGame():
    window.clear()
    batch.draw()
    todraw = currentMap.getVisible(player)
    for ent in todraw:
        ent.draw()
    if drawFPS:
        fps_display.draw()


@window.event
def on_key_press(symbol, modifiers):
    if window.state == 0:  # Title
        window.state = 1  # menu
    elif window.state == 2:  # game
        if symbol == key.ESCAPE:
            window.state = 1
            return pyglet.event.EVENT_HANDLED
        elif symbol == key.RIGHT:
            currentMap.moveEnt(player, 1, 0)
            currentMap.update()
        elif symbol == key.LEFT:
            currentMap.moveEnt(player, -1, 0)
            currentMap.update()
        elif symbol == key.UP:
            currentMap.moveEnt(player, 0, 1)
            currentMap.update()
        elif symbol == key.DOWN:
            currentMap.moveEnt(player, 0, -1)
            currentMap.update()


@window.event
def on_mouse_motion(x, y, dx, dy):
    if window.state == 1:
        start_b.mouse(x, y)
        exit_b.mouse(x, y)


@window.event
def on_mouse_release(x, y, dx, dy):
    if window.state == 1:
        start_b.release(x, y)
        exit_b.release(x, y)


@window.event
def on_mouse_press(x, y, dx, dy):
    if window.state == 1:
        start_b.press(x, y)
        exit_b.press(x, y)


@window.event
def on_draw():
    if window.state == 0:
        drawTitle()
    elif window.state == 1:
        drawMenu()
    elif window.state == 2:
        drawGame()


pyglet.app.run()
