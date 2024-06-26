import random
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

    def distanceTo(self, ent):
        (x, y, z) = self.position
        (x2, y2, z2) = ent.position
        return (((x - x2) ** 2 + (y2 - y) ** 2) ** 0.5) / 32

    def setStates(self, thestates):
        self.states = thestates

    def set(self, key, val):
        self.states[key] = val

    def get(self, key):
        if key not in self.states.keys():
            return 0
        try:
            return int(self.states[key])
        except (ValueError, TypeError):
            return self.states[key]

    def has(self, key):
        return key in self.states.keys()

    def setVisEnts(self, visEnts):
        self.visibleEnts = visEnts

    def getVisEnts(self):
        return self.visibleEnts


    def equip(self, ent):
        if ent.get("equipable") == 1:
            typeNew = ent.get("slot")
            ent.set("equipped", 1)
            for e in self.inventory:
                if e != ent:
                    typeOld = e.get("slot")
                    if typeOld == typeNew and e.get("equipped") == 1:  # todo: allow for two rings and two-handed logic
                        # switch out (todo: add logic for equip check)
                        e.set("equipped", 0)

    def draw(self):
        super().draw()
        for e in self.inventory:
            if e.get("equipped") == 1:
                x, y, z = self.position
                e.update(x=x, y=y)
                e.draw()

    def use(self,item,target):
        for key in item.states:
            if "causes" in key:
                sp = key.split(" ")
                what = sp[1]
                mult = item.get(key)
                min = item.get("min " + what)
                max = item.get("max " + what)
                val = random.randint(min,max)
                target.set(what,target.get(what)+val*mult)
                if val > 0:
                    target.bleed()

        if target.get("health")<=0:
            target.set("ticks", 0)
            target.dropLoot()


    def bleed(self):
        (x, y, z) = self.position
        self.dgmap.addEntByName("blood", int(x / 32), int(y / 32))


    def getOpinion(self,ent):
        if self.has("alignment") and ent.has("alignment"):
            return abs(self.get("alignment")-ent.get("alignment"))
        else:
            return 50
    def dropLoot(self):
        for e in self.inventory:
            if random.randint(0,100) < 10:
                (x,y,z) = self.position
                self.dgmap.addEnt(e,int(x/32),int(y/32))
                e.set("equipped", 0)


    def describeSelf(self):
        desc="A"
        if self.has("durability"):
            ratio = 100*self.get("durability")/self.get("max durability")
            temp=""
            if ratio < 75:
                temp=" cracked"
            if ratio < 50:
                temp=" damaged"
            if ratio < 25:
                temp=" broken"
            desc+=temp
        if self.has("health"):
            ratio = 100*self.get("health")/self.get("max health")
            temp=" healthy"
            if ratio < 75:
                temp=" hurt"
            if ratio < 50:
                temp=" wounded"
            if ratio < 25:
                temp=" dying"
            desc+=temp
        if self.has("action points"):
            ratio = 100*self.get("action points")/self.get("max action points")
            temp=" energetic"
            if ratio < 75:
                temp=" winded"
            if ratio < 50:
                temp=" tired"
            if ratio < 25:
                temp=" drained"
            desc+=temp
        desc+=" "+self.get("name")
        if self.has("nickname"):
            desc+=" named "+self.get("nickname")
        if self.has("can carry"):
            desc+=f' carrying {len(self.inventory)} things'
        return desc+"."