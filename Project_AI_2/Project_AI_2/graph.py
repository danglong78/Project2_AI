from turtle import *
import numpy as np
from time import *
square=48

scr=Screen()
scr.bgcolor("#f0f5f0")
scr.setup(1000,1000,0,0)
ht()
penup()
setpos(0,300)
color("black")
write("PROJECT 2",align="center" ,font=("arial",50,"normal"))


def input_shape():
    move=["d","u","r","l"]
    cell_shape=r"Pic\cell.gif"
    breeze_shape=r"Pic\breeze.gif"
    stench_shape=r"Pic\stench.gif"
    bs_shape=r"Pic\BS.gif"
    bg_shape=r"Pic\bg.gif"
    bsg_shape=r"Pic\bsg.gif"
    sg_shape=r"Pic\sg.gif"
    wall_shape=r"Pic\floor.gif"
    pit_shape=r"Pic\pit.gif"
    gold_shape=r"Pic\gold_floor.gif"
    wumpus_shape="Pic\wumpus.gif"
    player_shape=["Pic\\"+i+".gif"  for i in move]
    shoot_shape=["Pic\\s"+i+".gif"  for i in move]
    return wall_shape,gold_shape,shoot_shape,player_shape,cell_shape,pit_shape,breeze_shape,stench_shape,bs_shape, wumpus_shape,bg_shape,bsg_shape,sg_shape

wall_shape,gold_shape,shoot_shape,player_shape,cell_shape,pit_shape,breeze_shape,stench_shape,bs_shape, wumpus_shape,bg_shape,bsg_shape,sg_shape=input_shape()
scr.addshape(wumpus_shape)
scr.addshape(breeze_shape)
scr.addshape(stench_shape)
scr.addshape(bs_shape)
scr.addshape(bg_shape)
scr.addshape(bsg_shape)
scr.addshape(sg_shape)
scr.addshape(cell_shape)
scr.addshape(pit_shape)
scr.addshape(wall_shape)
scr.addshape(gold_shape)

for i in shoot_shape:
        scr.addshape(i)
for i in player_shape:
        scr.addshape(i)

all_shape={
    'W':wumpus_shape,
    'S':stench_shape,
    'B':breeze_shape,
    'P':pit_shape,
    'BS':bs_shape,'SB':bs_shape,
    'BSG':bsg_shape,'BGS':bsg_shape,'GSB':bsg_shape,'GBS':bsg_shape,'SGB':bsg_shape,'SBG':bsg_shape,
    'SG':sg_shape,'GS':sg_shape,
    'BG':bg_shape,'GB':bg_shape,
    '-':wall_shape,
    'G':gold_shape,
    'A':wall_shape
    }
  #---------------------------------------------
def graphic_loadmap(fi):
    map_game=[]

    f = open(fi, "r")
    if f.mode == "r":
        line =f.readline()
        n=int(line)
        for row in range(n):
            line = f.readline().strip('\n').split('.')
            map_game.append(line)
        map_game=np.array(map_game)
        start_postion=[int(i) for i in np.where(map_game=='A')]     
        f.close()
    global x_left_top,y_left_top
    x_left_top= -((n//2))*square
    y_left_top=(n//2)*square
    return map_game,n,start_postion

class Pen(Turtle):
    def __init__(self,wall):
        Turtle.__init__(self)
        self.speed(0)
        self.penup()
        self.shape(wall)
        self.s=""
    def draw_map(self,map,h,w):
        x=-((w//2))*square
        y=(h//2)*square
        gold=0
        monster=0
        self.st()
        list_wall={(x,y):self.clone() for x in range(h) for y in range(w)}
        
        for i in range(h):
            for j in range(w):
                if map[i][j]!='-' and map[i][j] !='A':
                    temp=list_wall[(i,j)]
                    temp.shape(all_shape[map[i][j]])
                    temp.s=all_shape[map[i][j]]
                    temp.goto(x+j*square,y-i*square)
                    if temp.s== gold_shape or temp.s== bsg_shape or temp.s== sg_shape or temp.s==bg_shape or map[i][j]=='WG' or map[i][j]=='GW':
                        gold+=1
                    if temp.s== wumpus_shape or map[i][j]=='WG' or map[i][j]=='GW':
                        monster+=1

                else:
                    #()
                    temp= list_wall[(i,j)]
                    temp.s=wall_shape
                    temp.shape(wall_shape)
                    temp.goto(x+j*square,y-i*square) 
        self.ht()
        self.shape('arrow')
        self.pen(fillcolor="black", pencolor="black", pensize=10)
        self.goto(300,300)
        return x,y,list_wall,gold,monster





class Player(Turtle):
    def __init__(self,s,row,col):
        Turtle.__init__(self)
        self.speed("slow")
        self.ht()
        self.s=s
        self.penup()
        self.row=row
        self.col=col
    def start(self,x,y):
        self.shape(self.s[0])
        self.goto(x,y)
        self.st()
    def down(self):
        self.seth(270)
        self.shape(self.s[0])
        self.fd(48)
    def up(self):
        self.seth(90)
        self.shape(self.s[1])
        self.fd(48)
    def right(self):
        self.seth(0)
        self.shape(self.s[2])
        self.fd(48)
    def left(self):
        self.seth(180)
        self.shape(self.s[3])
        self.fd(48)
    def move(self,index):
        if (self.row==index[0] and self.col>index[1]):
            self.left()
        elif (self.row==index[0] and self.col<index[1]):
            self.right()
        elif (self.row<index[0] and self.col==index[1]):
            self.down()
        elif (self.row>index[0] and self.col==index[1]):
            self.up()
        self.row,self.col=index
    def shoot(self,s,index):
        if (self.row==index[0] and self.col>index[1]):
            self.shape(s[3])
        elif (self.row==index[0] and self.col<index[1]):
            self.shape(s[2])
        elif (self.row<index[0] and self.col==index[1]):
            self.shape(s[0])
        elif (self.row>index[0] and self.col==index[1]):
            self.shape(s[1])
        sleep(0.75)

class Map:
    def __init__(self, filename):
        self.map,self.n,player=graphic_loadmap(filename)
        self.outline=Pen(wall_shape)
        x0,y0,self.list_wall,self.gold,self.wumpus=self.outline.draw_map(self.map,self.n,self.n)
        self.p=Player(player_shape,player[0],player[1])
        self.p.start(x0+player[1]*square,y0-player[0]*square)
        self.score=0
        self.arrow=0
        self.RS=(self.gold,self.wumpus)
        self.hide_all()
        self.explore()

    def is_beat(self):
        if self.map[self.p.row][self.p.col] in ['W','P','WG','GW']:
            return True
        return False

    def explore(self):
        i,j=self.p.row,self.p.col
        self.list_wall[(i,j)].shape(self.list_wall[(i,j)].s)

    def hide_all(self):
        for i in self.list_wall.values():
            i.shape(cell_shape)
    def eat_gold(self):
        i,j=self.p.row,self.p.col
        if self.list_wall[i,j].s==gold_shape:
            self.map[i][j]='-'
            self.list_wall[(i,j)].shape(wall_shape)
            self.list_wall[(i,j)].s=wall_shape
            self.score+=100
            self.gold-=1
        elif self.list_wall[i,j].s==sg_shape:
            self.map[i][j]='S'
            self.list_wall[(i,j)].shape(stench_shape)
            self.list_wall[(i,j)].s=stench_shape
            self.score+=100
            self.gold-=1
        elif self.list_wall[i,j].s==bsg_shape:
            self.map[i][j]='BS'
            self.list_wall[(i,j)].shape(bs_shape)
            self.list_wall[(i,j)].s=bs_shape
            self.score+=100
            self.gold-=1
        elif self.list_wall[i,j].s==bg_shape:
            self.map[i][j]='B'
            self.list_wall[(i,j)].shape(breeze_shape)
            self.list_wall[(i,j)].s=breeze_shape
            self.score+=100
            self.gold-=1
            
    def game(self,step):
        for i in step:
            self.outline.st()
            self.outline.write(self.score,align="center" ,font=("Arial",30,"normal"))
            self.outline.ht()
            if self.gold==0 and self.wumpus==0:
                break
            if len(i)==2:
                self.p.move(i)
                self.score-=10
                self.explore()
                if self.is_beat():
                    self.score-=10000
                    break
                self.eat_gold()
            elif len(i)==3:
                self.p.shoot(shoot_shape,(i[1],i[2]))
                self.arrow+=1
                self.score-=100
                self.remove_wumpus(i[1],i[2])
            if i== step[-1] and self.map[i[0]][i[1]]=='A':
                self.score+=20
            self.outline.clear()
    def remove_wumpus(self,i,j):
        if self.map[i][j]=='WG' or self.map[i][j]=='GW' :
            self.wumpus-=1
            self.map[i][j]='G'
            self.list_wall[(i,j)].shape(gold_shape)
            self.list_wall[(i,j)].s=gold_shape
           
        elif self.map[i][j]=='W':
            self.wumpus-=1
            self.list_wall[(i,j)].shape(wall_shape)
            self.list_wall[(i,j)].s=wall_shape
            self.map[i][j]='-'
            surround=get_surround(self.n,self.n,i,j)
         


    

    def print_result(self):
        scr.clear()
        scr.bgcolor("#f0f5f0")
        scr.setup(1000,1000,0,0)
        ht()
        penup()
        setpos(0,300)
        color("black")
        write("PROJECT 2",align="center" ,font=("Arial",50,"normal"))
        self.p.ht()
        self.outline.ht()
        penup()
        color("black")
        setpos(0,0)
        write("SCORE: "+str(self.score),align="center" ,font=("Arial",40,"normal"))
        penup()
        color("black")
        setpos(0,-60)
        write("GOLD: "+str(self.RS[0]-self.gold)+'/'+str(self.RS[0]),align="center" ,font=("Arial",40,"normal"))
        penup()
        color("black")
        setpos(0,-120)
        write("WUMPUS KILLED: "+str(self.RS[1]-self.wumpus)+'/'+str(self.RS[1]),align="center" ,font=("Arial",40,"normal"))
        penup()
        color("black")
        setpos(0,-180)
        write("ARROW: "+str(self.arrow),align="center" ,font=("Arial",40,"normal"))



def get_surround(h,w,i,j):
    rs=[]
    if i-1>=0:
        rs.append((i-1,j))
    if j-1>=0:
        rs.append((i,j-1))
    if i+1<h:
        rs.append((i+1,j))
    if j+1<w:
        rs.append((i,j+1))
    return rs

