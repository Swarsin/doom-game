import pygame
import sys
import time
import math
import random
import numpy as np
import asyncio

pygame.init()
# constants
info = pygame.display.Info()
res = info.current_w, info.current_h
square = 9
mapsize = 450
fps = 120
clock = pygame.time.Clock()
colourblack = (10,10,10)
colourlist = [["black",(0,0,0)],["cyan",(0,255,255)],["red",(255,0,0)],["flashlight",(150, 150, 150)],["grey",(150,150,150)]]
texture = [(75,75,75),(75,75,0),(0,75,75),(75,0,75)] # Wall colours for different wall values
DiagonalMultiplier = 2**0.5 #finds root 2, which when multiplied by a value (inputted as a hypotenuse), it can find the adjacent/opposite.


class circularqueue:
    def __init__(self):
        self.stack = ["","","","","","","","","",""]
        self.endpointer = -1
        self.frontpointer = "empty"
        self.datafilled = 0
        self.stackfull = False

    def delete(self):
        if self.datafilled == 0: #check so that the user cannot delete anything
            return False
        else:
            if self.endpointer == 9 and self.datafilled >= 1:
                self.endpointer = -1
            returneditem = self.stack[self.endpointer+1]
            self.stack[self.endpointer+1] = "" #deletes the item
            self.datafilled -= 1 #when the data is removed, the data filled number is lowered
            self.endpointer += 1 #end pointer is lowered
            return returneditem

    def add(self,item):
        if self.frontpointer == "empty":
            if self.datafilled == 10: #checks if stack is full as you cannot add to something which is already full
                self.stackfull = True
                return
            else:
                userinp = item
                if self.frontpointer == self.endpointer + 1:
                    pass
                else:
                    if self.frontpointer == 9:
                        self.frontpointer = 0
            self.frontpointer = 0
            self.stack[self.frontpointer] = userinp
            self.datafilled += 1
        else:
            if self.datafilled == 10: #checks if stack is full as you cannot add to something which is already full
                self.stackfull = True
                return
            else:
                userinp = item
                if self.frontpointer == self.endpointer - 1:
                    return
                else:
                    if self.frontpointer == 9 and not self.frontpointer == self.endpointer + 1:
                        self.frontpointer = -1
            self.stack[self.frontpointer+1] = userinp
            self.frontpointer += 1 #as the stack is filled, the endpointer and datafilled number increases
            self.datafilled += 1


# raycasting gameloop
class raygame:

    def __init__(self):
        self.gridsize = (mapsize/square)
        self.gridedge = self.gridsize / 15
        self.gameloop = True
        self.gridconvert = mapsize/square
        self.raydisplay = pygame.display.set_mode(res)
        self.gamemap = raycastmap()
        self.gamemap.MapGeneration()
        self.enemyspawnqueue = circularqueue()
        self.enemyobjlist = []
        self.totalenemy = 0
        self.levelcomplete = False
        self.enemyspawngeneration(3)
        print(self.totalenemy,self.enemyspawnqueue.datafilled)
        self.starrysky = pygame.image.load("starrysky.png").convert()
        self.starrysky = pygame.transform.scale(self.starrysky,((res[0]-mapsize),res[1]/2))
        self.ghost = pygame.image.load("ghost.png").convert()
        self.ghost = pygame.transform.scale(self.ghost,((res[0]-mapsize),res[1]))
        print(self.gamemap.map)
        self.player1 = player((start[0]*(self.gridsize))+(self.gridsize/2),(start[1]*(self.gridsize))+(self.gridsize/2),self) # generates player
        #pygame.init()
        pygame.display.set_caption("Retro Raycaster Game")
        while self.gameloop == True:
            self.GameCycle()
            self.Backdrop()
            self.MapDisplay()
            self.player1.ui()
            self.DrawDisplay()
            if self.levelcomplete == True:
                pass
            clock.tick(fps)
            
    def MapDisplay(self):
        maze = self.gamemap.map
        pygame.draw.rect(self.raydisplay,(5, 5, 5),(0,0,mapsize,mapsize))
        for row in range(self.gamemap.map.shape[0]):
            for column in range(self.gamemap.map.shape[1]):
                if maze[row][column] != 0:
                    i = maze[row][column]
                    i = texture[i-1]
                    pygame.draw.rect(self.raydisplay,i,(column * self.gridsize + (self.gridedge / 2), row * self.gridsize + (self.gridedge / 2), self.gridsize - self.gridedge, self.gridsize - self.gridedge))
        self.MapRaycast()
        self.player1.entitydisplay(self.raydisplay)

    def Backdrop(self):
        self.raydisplay.fill(colourlist[0][1])
        self.raydisplay.blit(self.starrysky,(mapsize,0))
        #pygame.draw.rect(self.raydisplay,(44, 106, 130),(mapsize,0,res[0]-mapsize,res[1]/2))

    def GameCycle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameloop == False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player1.left = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player1.right = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player1.up = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player1.down = True
                if event.key == pygame.K_SPACE and self.player1.shootdelay < 1:
                    self.player1.shooting = True
                    self.player1.shoottime = 5
                    self.player1.shootdelay = 25
                if event.key == pygame.K_h:
                    print(self.enemyspawnqueue.datafilled,len(self.enemyobjlist))

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player1.left = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player1.right = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player1.up = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player1.down = False
        self.player1.entityposupdate()
            
    def enemyspawngeneration(self,i):
        count = 0
        self.totalenemy = 10
        while count < 11:
            randomspawn = (random.randint(1,square-1),random.randint(1,square-1))
            if self.gamemap.map[randomspawn] == 0 and randomspawn != start and not randomspawn in self.enemyspawnqueue.stack:
                self.enemyspawnqueue.add(randomspawn)
                count += 1
        for x in range(0,i):
            self.spawnenemy()

    def spawnenemy(self):
        stackitem = self.enemyspawnqueue.delete()
        if self.enemyspawnqueue.datafilled == 0:
            pass
        else:
            enemyposx = (stackitem[1]*(self.gridsize))+(self.gridsize/2)
            enemyposy = (stackitem[0]*(self.gridsize))+(self.gridsize/2)
            self.enemyobjlist.append(enemy(enemyposx,enemyposy,self))
        return self.totalenemy

    def MapRaycast(self): #behind the scenes algorithm for raycasting
        global raycount,fov
        fov = 75
        raycount = int((res[0]-mapsize)/2)
        for iterray in range(raycount):
            planespacing = ((res[0]-mapsize)/raycount)
            d = ((res[0]-mapsize)/2)/math.tan(math.radians(fov/2))
            angle = self.player1.angle + math.atan((planespacing*iterray - ((res[0]-mapsize)/2))/d)     
            angleP = math.degrees(self.player1.angle)
            #angle = math.radians(((fov/2)+angleP)-(iterray/5))
            if angle > 2*math.pi:
                angle -= 2*math.pi
            if angle < 0:
                angle += 2*math.pi
            hx,hy,posh = self.HorizontalCheck(self.player1,angle) #tries to check for horizontal wall
            vx,vy,posv = self.VerticalCheck(self.player1,angle) #tries to check for vertical wall
            d1,d2,pos = self.RayLength(hx,hy,vx,vy,posh,posv)
            magnitude = math.sqrt(((self.player1.x-d1)**2)+((self.player1.y-d2)**2))
            distance = self.FishEye(magnitude,angle)
            i = (self.gamemap.map[pos])-1
            if i in range(0,len(texture)):
                colour = texture[i]
            else:
                colour = texture[0]
            self.Engine2Dto3D(distance,iterray,raycount,colour,d1,d2,angle)

    def FishEye(self,hypo,angle):
        alpha = self.player1.angle - angle
        distance = math.cos(alpha) * hypo
        return distance

    def RayLength(self,hx,hy,vx,vy,posh,posv):
        raycol = colourlist[3][1]
        if hx and hy and vx and vy:
                if math.sqrt(((self.player1.x-hx)**2)+((self.player1.y-hy)**2)) == math.sqrt(((self.player1.x-vx)**2)+((self.player1.y-vy)**2)):
                    pygame.draw.line(self.raydisplay,(raycol),(self.player1.x,self.player1.y),(hx,hy))
                    return hx,hy,posh
                else:
                    if math.sqrt(((self.player1.x-hx)**2)+((self.player1.y-hy)**2)) < math.sqrt(((self.player1.x-vx)**2)+((self.player1.y-vy)**2)):
                        pygame.draw.line(self.raydisplay,(raycol),(self.player1.x,self.player1.y),(hx,hy))
                        return hx,hy,posh
                    if math.sqrt(((self.player1.x-hx)**2)+((self.player1.y-hy)**2)) > math.sqrt(((self.player1.x-vx)**2)+((self.player1.y-vy)**2)):
                        pygame.draw.line(self.raydisplay,(raycol),(self.player1.x,self.player1.y),(vx,vy))
                        return vx,vy,posv
        elif hx and hy:
            pygame.draw.line(self.raydisplay,(raycol),(self.player1.x,self.player1.y),(hx,hy))
            return hx,hy,posh
        elif vx and vy:
            pygame.draw.line(self.raydisplay,(raycol),(self.player1.x,self.player1.y),(vx,vy))
            return vx,vy,posv
        else:
            return 10000000,10000000,posh

    def HorizontalCheck(self,player,inpangle):
            if math.pi < inpangle < 2*math.pi:
                angle = inpangle
                ny = player.y - (math.floor((player.y)/(self.gridconvert))*self.gridsize)
                nx = ny / -math.tan(angle)
                rx = player.x+nx
                ry = player.y-ny
                finalx = math.floor(rx/self.gridconvert)
                finaly = math.floor(ry/self.gridconvert)-1
                if 0 <= finaly <= square-1 and 0 <= finalx <= square-1:
                    if self.gamemap.map[finaly,finalx] != 0:
                        pass
                    elif self.gamemap.map[finaly,finalx] == 0:
                        dof = 0
                        oy = self.gridsize
                        ox = oy / -math.tan(angle)
                        rx = player.x+nx
                        ry = player.y-ny
                        while dof < square:
                            rx = ((rx) + ox)
                            ry = ((ry) - oy)
                            finalx = math.floor((rx)/self.gridconvert)
                            finaly = math.floor((ry)/self.gridconvert)-1
                            if 0 <= finalx < square and 0 <= finaly < square:
                                if self.gamemap.map[finaly,finalx] != 0:
                                    dof = square
                            dof += 1
                    position = (finaly,finalx)
                    return rx,ry,position

            elif inpangle > 0 and inpangle < math.pi:
                angle = inpangle
                ny = (math.ceil((player.y)/(self.gridconvert))*self.gridsize) - player.y
                nx = ny / math.tan(angle)
                rx = player.x+nx
                ry = player.y+ny
                finalx = math.floor(rx/self.gridconvert)
                finaly = math.floor(ry/self.gridconvert)
                if 0 <= finaly <= square-1 and 0 <= finalx <= square-1:
                    if self.gamemap.map[finaly,finalx] != 0:
                        pass
                    elif self.gamemap.map[finaly,finalx] == 0:
                        dof = 0
                        oy = self.gridsize
                        ox = oy / math.tan(angle)
                        rx = player.x+nx
                        ry = player.y+ny
                        while dof < square:
                            rx = ((rx) + ox)
                            ry = ((ry) + oy)
                            finalx = math.floor((rx)/self.gridconvert)
                            finaly = math.floor((ry)/self.gridconvert)
                            if 0 <= finalx < square and 0 <= finaly < square:
                                if self.gamemap.map[finaly,finalx] != 0:
                                    dof = square
                            dof += 1
                    position = (finaly,finalx)
                    return rx,ry,position
            return False,False,False
    
    def VerticalCheck(self,player,inpangle):
        if math.pi/2 < inpangle < (3*math.pi)/2:
            angle = inpangle - math.pi/2
            nx = player.x - (math.floor((player.x)/(self.gridconvert))*self.gridsize)
            ny = nx / math.tan(angle)
            rx = player.x - nx
            ry = player.y + ny
            finalx = math.floor(rx/self.gridconvert)-1
            finaly = math.floor(ry/self.gridconvert)
            if 0 <= finaly <= square-1 and 0 <= finalx <= square-1:
                if self.gamemap.map[finaly,finalx] != 0:
                    pass
                elif self.gamemap.map[finaly,finalx] == 0:
                    dof = 0
                    ox = self.gridsize
                    oy = ox / math.tan(angle)
                    while dof < square:
                        rx = rx-ox
                        ry = ry+oy
                        finalx = math.floor((rx)/self.gridconvert)-1
                        finaly = math.floor((ry)/self.gridconvert)
                        if 0 <= finalx < square and 0 <= finaly < square:
                            if self.gamemap.map[finaly,finalx] != 0:
                                dof = square
                        dof += 1
                position = (finaly,finalx)
                return rx,ry,position

        elif 0 <= inpangle < math.pi/2 or (3*math.pi)/2 < inpangle < 2*math.pi:
            angle = inpangle - math.pi/2
            nx = (math.ceil((player.x)/(self.gridconvert))*self.gridsize)-player.x
            ny = nx / -math.tan(angle)
            rx = player.x + nx
            ry = player.y + ny
            finalx = math.floor(rx/self.gridconvert)
            finaly = math.floor(ry/self.gridconvert)
            if 0 <= finaly <= square-1 and 0 <= finalx <= square-1:
                if self.gamemap.map[finaly,finalx] != 0:
                    pass
                elif self.gamemap.map[finaly,finalx] == 0:
                    dof = 0
                    ox = self.gridsize
                    oy = ox / -math.tan(angle)
                    while dof < square:
                        rx = rx+ox
                        ry = ry+oy
                        finalx = math.ceil((rx)/self.gridconvert)
                        finaly = math.floor((ry)/self.gridconvert)
                        if 0 <= finalx < square and 0 <= finaly < square:
                            if self.gamemap.map[finaly,finalx] != 0:
                                dof = square
                        dof += 1
            position = (finaly,finalx)
            return rx,ry,position
        return False,False,False

    def DrawDisplay(self): #algorithm for outputting
        pygame.display.flip()

    def SpriteSlicer(self,sprite, width, height,x,enemyplane):
        spriteslice = pygame.Surface((1,height)).convert_alpha()
        scaledsprite = pygame.transform.scale(sprite,(enemyplane,height))
        spriteslice.blit(scaledsprite,(0,0),(x, 0, 1, res[1]))
        #spriteslice = pygame.transform.scale(spriteslice,(1,height))
        return spriteslice

    def Engine2Dto3D(self,dist,i,raycount,wallcolour,d1,d2,angle):        
        d = (0.5*self.gridsize)/math.tan(math.radians(fov/2))
        width = (res[0]-mapsize)/raycount
        x = i * width
        height = int((d/dist) * res[1])
        colour = list(wallcolour)
        if height > res[1]:
            height = res[1]
        y = (res[1]/2) - height/2
        colour[0] = sorted((0,(6+colour[0] * (height**2/res[1]**2)),255))[1]
        colour[1] = sorted((0,(6+colour[1] * (height**2/res[1]**2)),255))[1]
        colour[2] = sorted((0,(20+colour[2] * (height**2/res[1]**2)),255))[1]
        pygame.draw.rect(self.raydisplay,colour,((x+mapsize),y,width,height))
        for obj in self.enemyobjlist:
            playertoenemyangle, enemydist = obj.entity3D(self.player1)
            if enemydist != 0:
                enemyplane = int(((0.5*(self.gridsize/3))/math.tan(math.radians(fov/2))/enemydist * res[1])/2)
            else:
                enemyplane = res[0]-mapsize
            playertoenemyangle -= math.pi
            if playertoenemyangle < 0:
                playertoenemyangle += 2*math.pi
            enemyplane = self.gridsize/2
            if enemydist != 0:
                maxplaneangle = (math.atan((enemyplane/2)/enemydist))
            else:
                maxplaneangle = 0
            beta = min(abs(playertoenemyangle-angle), 2 * math.pi - abs(playertoenemyangle-angle))
            if -maxplaneangle <= beta <= maxplaneangle:
                alpha = self.player1.angle-angle
                #alpha = min(abs(self.player1.angle - angle), 2 * math.pi - abs(self.player1.angle - angle))
                enemy_slice_offset = math.tan(alpha)*enemydist
                disttoplane = math.sqrt((enemydist**2)-(enemy_slice_offset**2))
                if disttoplane < dist:
                    enemyheight = ((self.gridsize/3)/(enemydist)*res[1])
                    enemyposy = (res[1]/2) - enemyheight/2
                    pygame.draw.rect(self.raydisplay,(0,150,0),((x+mapsize),enemyposy,width,enemyheight))
                    #spritesliced = self.SpriteSlicer(self.ghost,width,enemyheight,x,enemyplane)
                    #self.raydisplay.blit(spritesliced,((x+mapsize),enemyposy))
                    obj.entitydisplay(self.raydisplay)
                    self.EnemyDamageGame(angle,obj,i)
                            
    def EnemyDamageGame(self,angle,enemyobj,iterratedray):
        if int(raycount/2-raycount/8) < iterratedray < int(raycount/2+raycount/8):
            dead = self.player1.shootingcheck(angle,enemyobj)
            if dead:
                self.enemyobjlist.remove(enemyobj)
                self.totalenemy -= 1
                self.spawnenemy()
                print(self.enemyspawnqueue.datafilled)


# map generation
class raycastmap:
    def __init__(self):
        self.map = np.ones((square,square), dtype=int)
        self.visited = np.zeros((square, square), dtype=bool)
        for row in range(square):
            for column in range(square):
                randwall = random.randint(1,len(texture))
                self.map[row][column] = randwall
    
    def MapGeneration(self): #main algorithm to start the recursive algorithm
        global start
        StartRandList = [(1,square-2),(square-2,square-2),(square-2,1),(1,1)]
        start = random.choice(StartRandList)
        print("start chosen is: ", start) #for debugging
        self.MapCellNeighbour(start[0], start[1])

    def MapCellNeighbour(self, x, y): #single instance of the recursive algorithm
        global end
        self.map[x, y] = 0 #sets current node as an "air" cell
        self.visited[x, y] = True #sets current node as visited
        CellNeighbour = [((x-2),y), ((x+2),y), (x,(y-2)), (x,(y+2))] #looks two spaces from the current cell as it is where the next cell could be chosen
        random.shuffle(CellNeighbour) #randomly shuffles the list so that randomness is introduced
        for celln in CellNeighbour: #for loop
            if 0 <= celln[0] < square-1 and 0 <= celln[1] < square-1 and not self.visited[celln] == True: #filters out the neighbour cell coordinates which are out of bound and/or are already visited
                airx = (x + celln[0]) // 2 #finds the "midpoint" between the chosen cell and the current cell and assigns it
                airy = (y + celln[1]) // 2 # ^^^^
                self.map[airx, airy] = 0 #makes the cell between the neighbour and the current cell into an air cell
                self.map[celln] = 0 #makes the neigbouring cell also into an air cell
                self.MapCellNeighbour(celln[0],celln[1]) #calls itself again, using the neighbour cell as the starting cell for the next iteration
                # ^recursion


class entity:
    def __init__(self, x, y,game):
        self.entitysize = game.gridsize / 5
        self.rect = pygame.Rect(x , y, self.entitysize, self.entitysize)
        self.x = int(x)
        self.y = int(y)
        self.angle = 0
        self.entityspeed = game.gridsize / 40
        self.SpeedX = self.entityspeed
        self.SpeedY = 0
        self.colour = (0,0,0)
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.gridconvert = mapsize/square
        self.game = game

    def entitydisplay(self, window):
        self.rect.x = int(self.x-(self.entitysize/2))
        self.rect.y = int(self.y-(self.entitysize/2))
        pygame.draw.rect(window, self.colour, self.rect)

    def entityposupdate(self):
        fronty,frontx,backy,backx = self.collision()
        if self.right and not self.left:
            self.angle += 0.05
            if self.angle >= 2*math.pi:
                self.angle -= (2*math.pi)
            self.SpeedX = math.cos(self.angle) * self.entityspeed
            self.SpeedY = math.sin(self.angle) * self.entityspeed
        if self.left and not self.right:
            self.angle -= 0.05
            if self.angle <= 0:
                self.angle += (2*math.pi)
            self.SpeedX = math.cos(self.angle) * self.entityspeed
            self.SpeedY = math.sin(self.angle) * self.entityspeed
        if self.up and not self.down and frontx:
            self.x += self.SpeedX
        if self.up and not self.down and fronty:
            self.y += self.SpeedY
        if self.down and not self.up and backx:
            self.x -= self.SpeedX
        if self.down and not self.up and backy:
            self.y -= self.SpeedY
    
    def collision(self):
        infronty1 = math.floor(((self.y)+(self.SpeedY*2))/self.gridconvert)
        infrontx1 = math.floor(((self.x)+(self.SpeedX*2))/self.gridconvert)
        outbacky1 = math.floor(((self.y)-(self.SpeedY*2))/self.gridconvert)
        outbackx1 = math.floor(((self.x)-(self.SpeedX*2))/self.gridconvert)
        fronty,frontx,backy,backx = True,True,True,True
        if self.game.gamemap.map[infronty1][math.floor((self.x)/self.gridconvert)] != 0:
            fronty = False
        if self.game.gamemap.map[outbacky1][math.floor((self.x)/self.gridconvert)] != 0:
            backy = False
        if self.game.gamemap.map[math.floor((self.y)/self.gridconvert)][infrontx1] != 0:
            frontx = False
        if self.game.gamemap.map[math.floor((self.y)/self.gridconvert)][outbackx1] != 0:
            backx = False
        return fronty,frontx,backy,backx


class player(entity):
    def __init__(self,x,y,game):
        super().__init__(x,y,game)
        self.colour = colourlist[2][1] #overriding parent attribute
        self.weapon = pygame.image.load("doomgun.png")
        self.weaponfired = pygame.image.load("doomgunfired.png")
        self.xwobble = 0
        self.ywobble = 50
        self.shooting = False
        self.shoottime = 0
        self.shootdelay = 0
        self.shotround = False

    def shootingcheck(self,rayangle,enemy):
        if self.shooting == True and self.shotround == False:
            self.shotround = True
            isdead = enemy.TakeDamage()
            if isdead == True:
                return True
            return False
    
    def ui(self):
        if (self.up and not self.down):
            self.xwobble += 0.0005
            self.ywobble += 0.002
        if (self.down and not self.up):
            self.xwobble -= 0.0001
            self.ywobble -= 0.002
        if self.xwobble > 360:
            self.xwobble -= 360
        if self.ywobble > 360:
            self.ywobble -= 360
        if self.shooting == False:
            self.game.raydisplay.blit(self.weapon,(mapsize+((res[0]-mapsize)/3)+(25*math.sin(math.degrees(self.xwobble))),res[1]-450+(20*math.sin(math.degrees(self.ywobble))))) #simple 
            if self.shootdelay > 0:
                self.shootdelay -= 1
        if self.shooting == True:
            self.game.raydisplay.blit(self.weaponfired,(mapsize+((res[0]-mapsize)/3)+(25*math.sin(math.degrees(self.xwobble))),res[1]-450+(20*math.sin(math.degrees(self.ywobble)))))
            self.shoottime -= 1
            self.shootdelay -= 1
            if self.shoottime < 0:
                self.shooting = False
                self.shotround = False


class enemy(entity):
    def __init__(self,x,y,game):
        super().__init__(x,y,game)
        self.colour = (0,150,0)
        self.health = random.randint(3,5)

    def AImovement(self):
        pass 
    
    def entitydisplay(self,window):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        pygame.draw.circle(window, self.colour, (self.rect.x,self.rect.y),self.entitysize)
    
    def entity3D(self,player):
        y = player.y - self.y
        x = player.x - self.x
        beta = math.atan2(y,x)
        if beta < 0:
            beta = 2*math.pi + beta
        distance = math.sqrt((x)**2 + (y)**2)
        return beta,distance
    
    def TakeDamage(self):
        self.health -= 1
        if self.health == 0:
            return True
        return False

# if __name__ == '__main__':
#     game = raygame()


async def main():
    game = raygame()
    await asyncio.sleep(0)      

asyncio.run(main())

