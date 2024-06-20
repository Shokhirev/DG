import math


class dgMap():

    def __init__(self, w=30, h=24):
        self.w = w
        self.h = h
        self.ents = [[[] for i in range(h)] for j in range(w)]

    def addEnt(self, entity, x, y):
        self.ents[x][y].append(entity)
        entity.position = (x * 32, y * 32, 0)

    def removeEnt(self, entity):
        x, y, z = entity.position
        x = int(x / 32)
        y = int(y / 32)
        self.ents[x][y].remove(entity)

    def moveEnt(self, entity, deltax, deltay):
        (x, y, z) = entity.position
        x = int(x / 32)
        y = int(y / 32)
        (newx, newy) = self.getBounded(x + deltax, y + deltay)
        canMove = True
        for ent in self.ents[newx][newy]:
            if ent.get("impassable") == 1:
                canMove = False
                break
        if canMove and (x, y) != (newx, newy):
            self.ents[x][y].remove(entity)
            entity.position = (newx * 32, newy * 32, 0)
            self.ents[newx][newy].append(entity)
            return 0
        else:
            return 1

    def resetEnts(self):
        for i in range(self.w):
            for j in range(self.h):
                for e in self.ents[i][j]:
                    e.setVisEnts(None)

    def getBounded(self, x, y):
        return (round(min(self.w - 1, max(0, x))), round(min(self.h - 1, max(0, y))))

    def getVisible(self, entity):
        visEnts = entity.getVisEnts()
        if visEnts is None:
            res = []
            (x, y, z) = entity.position
            x = int(x / 32)
            y = int(y / 32)
            r = int(entity.get("vision"))

            oMask = [[None for i in range(self.h)] for j in range(self.w)]

            for angle in range(1, 360, 1):
                dx = math.cos(angle * 0.01745329)
                dy = math.sin(angle * 0.01745329)
                ox = x
                oy = y
                casting = True

                for i in range(1, r + 1):
                    if casting:
                        (ex, ey) = self.getBounded(ox, oy)
                        if oMask[ex][ey] is None:
                            oMask[ex][ey] = False
                            for e in self.ents[ex][ey]:
                                if not e.get("invisible") == 1:
                                    res.append(e)
                            if e.get("opaque") == 1:
                                casting = False
                                oMask[ex][ey] = True
                                break
                        else:
                            if oMask[ex][ey]:
                                casting = False
                                break
                    else:
                        break
                    ox += dx
                    oy += dy
            entity.setVisEnts(list(dict.fromkeys(res)))
            return list(dict.fromkeys(res))
        return visEnts



    def update(self):
        self.resetEnts()
