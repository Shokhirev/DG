import math


class dgMap():

    def __init__(self, w=30, h=24):
        self.w = w
        self.h = h
        self.ents = [[[] for i in range(h)] for j in range(w)]
        self.ticking = []

    def addEnt(self, entity, x, y):
        self.ents[x][y].append(entity)
        entity.position = (x * 32, y * 32, 0)


    def removeEnt(self, entity):
        x, y, z = entity.position
        x = int(x / 32)
        y = int(y / 32)
        self.ents[x][y].remove(entity)
        if entity in self.ticking:
            self.ticking.remove(entity)

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

    def getPath(self, e1, e2):
        gs = [[math.inf for i in range(self.h)] for j in range(self.w)]
        fs = [[math.inf for i in range(self.h)] for j in range(self.w)]
        parent = dict()
        (x1, y1, z) = e1.position
        x1 = int(x1 / 32)
        y1 = int(y1 / 32)
        (x2, y2, z) = e2.position
        x2 = int(x2 / 32)
        y2 = int(y2 / 32)
        oset = {(x1, y1)}
        gs[x1][y1] = 0
        fs[x1][y1] = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        while len(oset) > 0:
            ll = sorted(list(oset), key=lambda x: fs[x[0]][x[1]])
            (nx, ny) = ll[0]
            (lx, ly) = self.getBounded(nx - 1, ny - 1)
            (hx, hy) = self.getBounded(nx + 1, ny + 1)
            for i in range(lx, hx + 1):
                for j in range(ly, hy + 1):
                    if i != nx or j != ny:
                        canMove = True
                        for ent in self.ents[i][j]:
                            if ent.get("impassable") == 1:
                                canMove = False
                        if canMove:
                            if i == x2 and j == y2:
                                parent[(i, j)] = (nx, ny)
                                path = [(x2, y2)]
                                while True:
                                    prev = parent[path[0]]
                                    path.insert(0, prev)
                                    if prev[0] == x1 and prev[1] == y1:
                                        return path
                            tentativeg = gs[nx][ny] + ((nx - i) ** 2 + (ny - j) ** 2) ** 0.5
                            if tentativeg < gs[i][j]:
                                parent[(i, j)] = (nx, ny)
                                gs[i][j] = tentativeg
                                fs[i][j] = tentativeg + ((x2 - i) ** 2 + (y2 - j) ** 2) ** 0.5
                                if (i, j) not in oset:
                                    oset.add((i, j))
            oset.remove((nx, ny))

    def update(self):
        self.resetEnts()
        return self.tick()

    def tick(self):
        toAI=[]
        for ent in self.ticking:
            if ent.get("intelligence") > 0:
                if ent.has('plan'):
                    commands = ent.get("plan").split(".")
                    if len(commands) > 0:
                        nextC = commands[0]
                else:
                    toAI.append(ent)
        return toAI