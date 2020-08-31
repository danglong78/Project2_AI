from graph import *
from Propositional_Logic import *
path= Play_Game('map1.txt')
map=Map("map1.txt")
map.game(path)
#map.print_result()
#map,n,player=graphic_loadmap('map1.txt')
#outline=Pen(wall_shape)
#x0,y0,list_wall,gold,wumpus=outline.draw_map(map,n,n)
#p=Player(player_shape,player[0],player[1])
#p.start(x0+player[1]*square,y0-player[0]*square)

done()
