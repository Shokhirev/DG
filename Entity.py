import sys

import pyglet

from Map import dgMap


class Entity(pyglet.sprite.Sprite):
    def __init__(self, img, dgmap: dgMap = None, x=None, y=None):
        super().__init__(img=img)
        self.dgmap = dgmap
        if dgmap is not None:
            self.dgmap.addEnt(entity=self, x=x, y=y)
        self.states = dict()
        self.visibleEnts = None
        self.inventory = []

    def setStates(self,thestates):
        self.states = thestates
    def set(self, key, val):
        self.states[key] = val

    def get(self, key):
        if key not in self.states.keys():
            return 0
        try:
            return int(self.states[key])
        except ValueError:
            return self.states[key]

    def has(self, key):
        return key in self.states.keys()

    def setVisEnts(self, visEnts):
        self.visibleEnts = visEnts

    def getVisEnts(self):
        return self.visibleEnts

    def take(self, ent):
        # todo: add logic for pick up checks
        self.inventory.append(ent)

    def equip(self, ent):
        typeNew = ent.get("type")
        ent.set("equipped", 1)
        for e in self.inventory:
            if e != ent:
                typeOld = e.get("type")
                if typeOld == typeNew and e.get("equipped")==1:  # todo: allow for two rings and two-handed logic
                    # switch out (todo: add logic for equip check)
                    e.set("equipped", 0)


    def draw(self):
        super().draw()
        for e in self.inventory:
            if e.get("equipped") == 1:
                x, y, z = self.position
                e.update(x=x,y=y)
                e.draw()




    def getDescription(self):
        description="You see:"
        for ent in self.dgmap.getVisible(self):
            if not ent == self and ent.get("interesting")==1:
                nick=ent.get("nickname")
                if nick is not 0:
                    description += " "+ ent.get("name")+" named "+nick
                else:
                    description += " "+ent.get("name")
        if description == "You see:":
            description += " nothing of interest near you"
        description+=". Your properties are: "
        for key in self.states.keys():
            description+=key+"="+self.states[key]+" "
        description+="."
        return description