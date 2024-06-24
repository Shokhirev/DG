import random

import languagemodels as lm
import pyglet

from pyglet.window import key

from Map import dgMap
from button import button
from Entity import Entity
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
lm.config["device"] = "auto"
lm.config["max_ram"] = "8gb"


class game:
    def __init__(self):
        imageTiles = pyglet.resource.image('tiles.png')
        imageMap = {(15, 9): "grass",
                    (4, 80): "player",
                    (4, 81): "npc",
                    (0, 7): "wall",
                    (30, 46): "sword",
                    (9, 51): "blood",
                    (1, 60): "goblin",
                    (47, 82): "robe"}  # from top left
        self.images = dict()
        for k, v in imageMap.items():
            (x, y) = k
            subImg = imageTiles.get_region(x * 32, (94 - y) * 32, 32, 32)
            self.images[v] = subImg

        defsFile = pyglet.resource.file('defs.txt')
        self.defs = dict()
        cdef = dict()
        while True:
            line = defsFile.readline()
            if not line:
                break
            line = str(line).split('\\r')[0].split('b\'')[1]

            if ":" in line:
                split = line.split(':')
                if len(cdef) > 0:
                    self.defs[cdef['name']] = cdef
                cdef = dict()
                # assume the type is already in the defs
                if len(split[1]) > 0 and split[1] in self.defs.keys():
                    cdef.update(self.defs[split[1]])
                cdef['name'] = split[0]
                cdef['type'] = split[1]
            else:
                if "\\t" in line:
                    split = line.split('\\t')
                    cdef[split[0]] = split[1]

        self.defs[cdef['name']] = cdef  # put the last



    def genGame(self):
        self.maps = self.generateMaps(1)
        self.currentMap = self.maps[0]
        self.player = dg.getEntity(name="player", x=20, y=20, dgmap=self.currentMap)
        robe = dg.getEntity2(name="robe", owner=self.player)
        self.player.inventory.append(robe)
        self.player.equip(robe)
        goblin = dg.getEntity(name="goblin", x=18, y=18, dgmap=self.currentMap)
        sword = dg.getEntity(name="sword", x=17, y=17, dgmap=self.currentMap)

    def generateMaps(self, param):
        res = dict()
        for i in range(param):
            m = dgMap(self, w=40, h=22)
            for x in range(m.w):
                for y in range(m.h):
                    grass = self.getEntity(name="grass", dgmap=m, x=x, y=y)
                    r = random.randint(0, 100)
                    if r < 20:
                        wall = self.getEntity(name="wall", dgmap=m, x=x, y=y)
            res[i] = m
        return res

    def getEntity(self, name, x, y, dgmap):
        ent = Entity(img=self.images[name], x=x, y=y, dgmap=dgmap)
        ent.setStates(self.defs[name])
        if ent.get("ticks") == 1:
            dgmap.ticking.append(ent)
        if ent.has("intelligence"):
            ent.set("nickname",lm.do(f'Generate a name for a {ent.get("name")} whose favorite number is {random.randint(0,100)}'))
            print(ent.get("nickname"))
        return ent

    def getEntity2(self, name, owner):
        ent = Entity(img=self.images[name])
        ent.setStates(self.defs[name])
        owner.inventory.append(ent)
        return ent

    def getEntsToDraw(self):
        return self.currentMap.getVisible(self.player)

    def addToAIQueue(self,entList):
        for smart in entList:
            nearbyEnts = dg.currentMap.getVisible(smart)
            items = []
            things = []
            description = "You see:"
            for ent in nearbyEnts:
                if not ent == smart and ent.get("interesting") == 1:
                    nick = ent.get("nickname")
                    statement = ent.get("saying")
                    if isinstance(nick, str):
                        description += " A " + ent.get("name") + " named " + nick
                    else:
                        description += " A " + ent.get("name")
                    opinion = smart.getOpinion(ent)
                    if opinion < 10:
                        description += " that you love"
                    elif opinion < 50:
                        description += " that you like"
                    elif opinion > 80:
                        description += " that you dislike"
                    elif opinion > 120:
                        description += " that you hate"
                    if isinstance(statement, str):
                        description += f', saying {statement}'
                    if ent.distanceTo(smart) < 1.5:
                        description += " within reach. "
                    else:
                        description += " far away. "
                    things.append(ent)
            if description == "You see:":
                description += " nothing of interest near you. "
            description += "You have: "
            for ent in smart.inventory:
                description += ent.describeSelf()
                items.append(ent)
            if len(smart.inventory) == 0:
                description += "Nothing of value."
            description += ". You are " + smart.describeSelf()
            desc = "You are a character in a 2D game." + description + "Select what you would like to do next using a simple sentence. " \
                                                                       "You can go to things that are not near. You can use things you have. " \
                                                                       "You can equip things you have. You should " \
                                                                       "equip before you move, help, or attack. If " \
                                                                       "you think you will survive, you should attack " \
                                                                       "those you dislike and try helping those you " \
                                                                       "like. You should try to pick up and keep things that might be of value. "
            options = ["wander"]
            targets = dict()
            targets["wander"] = None
            for item in smart.inventory:
                if item.has("useable") or (item.has("equipable") and item.get("equipped")==1):
                    options.append("use " + item.get("name")+" on yourself")
                    targets[options[-1]] = (item, smart)
                    for thing in things:
                        options.append("use " + item.get("name") + " on "+thing.get("name"))
                        targets[options[-1]] = (item, thing)
                if item.has("equipable"):
                    if item.get("equipped") == 0:
                        options.append("equip " + item.get("name"))
                        targets[options[-1]] = item
                    # else:
                    #    options.append("unequip " + item.get("name"))
                    #    targets[options[-1]] = item
                options.append("drop " + item.get("name"))
                targets[options[-1]] = item
            for ent in nearbyEnts:
                if not ent == smart and ent.get("interesting") == 1:
                    if ent.distanceTo(smart) >= 1.5:
                        options.append("go to " + ent.get("name"))
                        targets[options[-1]] = ent
                    else:
                        if ent.has("carryable") and ent.get("carryable") == 1:
                            options.append("get " + ent.get("name"))
                            targets[options[-1]] = ent
            print(desc)
            print(options)
            res = lm.do(prompt=desc, choices=options)
            smart.set("plan", res)
            smart.set("plan target", targets[res])
            print(f'{smart.get("nickname")} has a plan: {res}')

    def processKeyPress(self, symbol, modifiers):
        if self.player.get("ticks") ==1:
            if symbol == key.RIGHT:
                self.currentMap.moveEnt(self.player, 1, 0)
                self.addToAIQueue(self.currentMap.update())
            elif symbol == key.LEFT:
                self.currentMap.moveEnt(self.player, -1, 0)
                self.addToAIQueue(self.currentMap.update())
            elif symbol == key.UP:
                self.currentMap.moveEnt(self.player, 0, 1)
                self.addToAIQueue(self.currentMap.update())
            elif symbol == key.DOWN:
                self.currentMap.moveEnt(self.player, 0, -1)
                self.addToAIQueue(self.currentMap.update())
            return True
        else:
            return False


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

death = pyglet.text.Label("You Died!", font_name="Calibri", font_size=80, x=window.width // 2, y=window.height // 2,
                          anchor_x="center",color=(200,50,50,200))
# Buttons
class start_btn(button):
    def clicked(self):
        window.state = 2
        dg.genGame()

class exit_btn(button):
    def clicked(self):
        pyglet.app.exit()


start_b = start_btn(label="Start", x=window.width // 2, y=200, w=200, h=50)
exit_b = exit_btn(label="Exit", x=window.width // 2, y=100, w=200, h=50)

# Game stuff
dg = game()
window.state = 0  # 0=title, 1=menu, 2=game
drawFPS = True

# Logic
batch = pyglet.graphics.Batch()  # for particle effects and other shiz that we don't need logic for.



def drawTitle():
    window.clear()
    title.draw()
    subtitle.draw()

def drawDeath():
    death.draw()

def drawMenu():
    window.clear()
    start_b.draw_self()
    exit_b.draw_self()


def drawGame():
    window.clear()
    todraw = dg.getEntsToDraw()
    for ent in todraw:
        ent.draw()
    batch.draw()
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
        else:
            res = dg.processKeyPress(symbol,modifiers)
            if not res:
                window.state = 3 #death


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
    elif window.state == 3:
        drawGame()
        drawDeath()


pyglet.app.run()
