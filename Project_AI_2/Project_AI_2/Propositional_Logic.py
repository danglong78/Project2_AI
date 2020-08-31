import re
class KB: #Propositional Logic KB
    def __init__(self,sentence=None):
        self.clauses=[]
        if sentence:
            self.tell(sentence)
    def tell(self,sentence): # Add new sentence to KB
        self.clauses.extend(conjunct(to_cnf(sentence)))
    def retract(self, sentence): #Remove the sentence's clauses from the KB
        for c in conjunct(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)
def is_symbol(s):
    return isinstance(s, str) and s[0].isalpha()

class Clause:
    def __init__(self, op, *args):
        self.op=op
        self.args = list(map(expr, args))
    def __call__(self, *args):
        return Clause(self.op, *args)
    def __and__(self, other):    # And operator
        return Clause('&',  self, other)
    def __neg__(self):           # not operator
        if self.op=='-' and len(self.args)==1 :
            return self.args[0]
        else:
            return Clause('-',  self)
    def __or__(self, other):     # or operator
        return Clause('|',  self, other)
    def __rshift__(self, other): # implication operator
        return Clause('==>', self, other)
    def __mod__(self, other):    # Equivalence operator
        return Clause('<=>',  self, other)
    def __eq__(self,other):
        return (other is self) or (isinstance(other,Clause) and self.op == other.op and self.args == other.args)
    def __repr__(self):
        if len(self.args) == 0: # Constant or proposition with arity 0
            return str(self.op)
        elif is_symbol(self.op): # Functional or Propositional operator
            return '%s(%s)' % (self.op, ', '.join(map(repr, self.args)))
        elif len(self.args) == 1: # Prefix operator
            return self.op + repr(self.args[0])
        else: # Infix operator
            return '(%s)' % (' '+self.op+' ').join(map(repr, self.args))
    def __hash__(self):
        return hash(self.op) ^ hash(tuple(self.args))
def expr(s):
    if isinstance(s, Clause): 
        return s
    s = s.replace('==>', '>>')
    s = s.replace('<=>', '%')
    ## Replace a symbol or number, such as 'P' with 'Clause("P")'
    s = re.sub(r'([a-zA-Z0-9_.]+)', r'Clause("\1")', s)
    return eval(s, {'Clause':Clause})
    
def to_cnf(s):
    if isinstance(s,str):
        s=expr(s)
    s=implication_elim(s)
    s= move_not_inwards(s)
    return distribute_or_over_and(s)

       

def implication_elim(s):
    if s.op=='<=>':
        a,b=s.args[::]
        s = ( a >> b ) & (b>>a) 
    if s.op=='==>':
        a,b=s.args[::]
        s= -a | b   
    s.args=[implication_elim(i) for i in s.args]
    return s 
def move_not_inwards(s):
    if s.op=='-':
        NOT = lambda b: move_not_inwards(-b)
        a = s.args[0]
        if a.op == '-': return move_not_inwards(a.args[0])
        if a.op =='&': return Remove_Bracket('|', *map(NOT, a.args))
        if a.op =='|': return Remove_Bracket('&', *map(NOT, a.args))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Clause(s.op, *map(move_not_inwards, s.args))
def Remove_Bracket(op, *args):
    arglist = []
    for i in args:
        if i.op == op: 
            arglist.extend(i.args)
        else: 
            arglist.append(i)
    if len(args) == 1:
        return args[0]
    else:
        return Clause(op, *arglist)
def distribute_or_over_and(s):
    if s.op == '|':
        s = Remove_Bracket('|', *s.args)
        if len(s.args) == 1:
            return distribute_or_over_and(s.args[0])
        conj = [i for i in s.args if i.op=='&' ]
        if not conj:
            return Remove_Bracket(s.op, *s.args)
        conj=conj[0]
        others = [a for a in s.args if a is not conj]
        if len(others) == 1:
            rest = others[0]
        else:
            rest = Remove_Bracket('|', *others)
        return Remove_Bracket('&', *map(distribute_or_over_and,[(c|rest) for c in conj.args]))
    elif s.op == '&':
        return Remove_Bracket('&', *map(distribute_or_over_and, s.args))
    else:
        return s


    
def conjunct(s):
    if s.op=='&' and isinstance(s,Clause):
        return s.args
    else:
        return [s]
def disjunct(s):
    if s.op=='|' and isinstance(s,Clause):
        return s.args
    else:
        return [s]

def pl_resolve(ci,cj):
    temp=[]
    for i in disjunct(ci):
        for j in disjunct(cj):
            if i==-j:
                temp.extend([i,j])
    if temp:            
        new_args=[]
        for i in (disjunct(ci)+disjunct(cj)):
            if i not in new_args and i not in temp:
                new_args.append(i)
        if new_args:
            return [Remove_Bracket('|', *new_args)]
        else:
            return"FALSE"
    else:
         return[]  
def pl_resolution(KB,alpha):
    clauses=KB.clauses+ conjunct(to_cnf(alpha))
    pair = [(clauses[i], clauses[j]) for i in range(len(clauses)) for j in range(i+1,len(clauses)) ]
    new=set()
    s=0
    i=0
    while True:
        for (ci, cj) in pair:
            resolvents = pl_resolve(ci, cj)
            if type(resolvents)==str: 
                return True  
            new.update(set(resolvents))
        if new.issubset(set(clauses)): 
            return False
        pair.clear()
        pair=[(i,j) for i in clauses for j in list(new)[s:] ]+ [ (list(new)[i], list(new)[j]) for i in range(s,len(new)) for j in range(i+1, len(new))]
        s=len(new)
        for c in new:
            if c not in clauses: clauses.append(c)  
#def pl_resolution(KB,alpha):
#    clauses=KB.clauses+ conjunct(to_cnf(alpha))
#    new=set()
#    while True:
#        n = len(clauses)
#        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i+1, n)]
#        for (ci, cj) in pairs:
#            resolvents = pl_resolve(ci, cj)
#            if type(resolvents)==str: 
#                return True  
#            new.update(set(resolvents))
#        if new.issubset(set(clauses)): 
#            return False
#        for c in new:
#            if c not in clauses: clauses.append(c)       
            

        # Ham them thong tin 1 o vao KB:

def Add_Clause(K_B,maze,pos,w,h):
    cur_state = maze[pos[0]][pos[1]]
    next = []
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if(pos[0] + i>=0) and (pos[0] + i<h) and (pos[1] + z>=0) and (pos[1] + z<w):
            next.append([pos[0]+i,pos[1]+z])

    if 'B' in cur_state:        # co gio
        new_clause = '('
        for i in next:
            new_clause += ('P'+str(i[0])+str(i[1])+'|')
        new_clause = (new_clause[:-1] + ')')
        K_B.tell(to_cnf(new_clause))
    else:
        new_clause = '('
        for i in next:
            new_clause = '('
            new_clause += ('-P'+str(i[0])+str(i[1])+')')
            K_B.tell(to_cnf(new_clause))


    if 'S' in cur_state:        # co mui
        new_clause = '('
        for i in next:
            new_clause += ('W'+str(i[0])+str(i[1])+'|')
        new_clause = (new_clause[:-1] + ')')
        K_B.tell(to_cnf(new_clause))
    else:
        new_clause = '('
        for i in next:
            new_clause = '('
            new_clause += ('-W'+str(i[0])+str(i[1])+')')
            K_B.tell(to_cnf(new_clause))


    if 'W' in cur_state:        # co Wumpus
        new_clause = ( '(W' + str(pos[0]) + str(pos[1]) + ')' )
        K_B.tell(to_cnf(new_clause))
    else:
        new_clause = ( '(-W' + str(pos[0]) + str(pos[1]) + ')' )
        K_B.tell(to_cnf(new_clause))
    
    if 'P' in cur_state:        # co pit
        new_clause = ( '(P' + str(pos[0]) + str(pos[1]) + ')' )
        K_B.tell(to_cnf(new_clause))
    else:
        new_clause = ( '(-P' + str(pos[0]) + str(pos[1]) + ')' )
        K_B.tell(to_cnf(new_clause))


    if cur_state == '-' :       #An toan
        
        for i in next:
            new_clause = '('
            new_clause += ('-W'+str(i[0])+str(i[1])+')')
            K_B.tell(to_cnf(new_clause))
        new_clause = '('
        for i in next:
            new_clause = '('
            new_clause += ('-P'+str(i[0])+str(i[1])+')')
            K_B.tell(to_cnf(new_clause))
        

        #Ham doc file:
def read_file(path):
    f=open(path,'r')
    temp = f.readline()
    h = int(temp)
    w = h
    maze = []
    for i in range(h):
        temp = f.readline()
        temp = temp[:-1]
        row = temp.split('.')
        maze.append(row)
    for i in range(h):
        for z in range(w):
            if 'A' in maze[i][z]:
                start_pos = [i,z]
                maze[i][z] = maze[i][z].replace('A','')
                if(len(maze[i][z])==0):
                    maze[i][z] = '-'
    return [maze,h,w,start_pos]



        # Ham kiem tra da kham pha het map chua
def Is_Completed(A_map,h,w):
    for i in A_map:
        for z in i:
            if z == 'U':
                return False
    return True



        # Ham tao Agent map ban dau
def Init_Amap(G_map,start_pos,h,w):
    A_map = []
    for i in range(h):
        temp = []
        for z in range(w):
            temp.append('U')
        A_map.append(temp)
    A_map[start_pos[0]][start_pos[1]] = G_map[start_pos[0]][start_pos[1]]
    return A_map



        # Ham tinh khoang cach Manhattan
def Manhattan(des,cur):
    return (abs(des[0]-cur[0]) + abs(des[1] - cur[1]))



        # Ham tim cac o unexplored co the den:
def Can_Reach(A_map,h,w,cur_pos):
    result_list = []
    for i in range(h):
        for z in range(w):
            if A_map[i][z] =='U':
                for (x,y) in zip([i-1,i,i,i+1],[z,z-1,z+1,z]):
                    if (x>=0) and (x<h) and (y>=0) and (y<w):
                        if (A_map[x][y] != 'U') and ('W' not in A_map[x][y]) and ('P' not in A_map[x][y]):
                            result_list.append([i,z])
                            break
    if(len(result_list)==0):
        return result_list
    result_list.sort(key = lambda x: Manhattan(x,cur_pos))
    return result_list



        #Ham tim duong di - Dung BFS
def next_step(A_map,pos,h,w):
    return_list = []
    for (i,z) in zip([pos[0]-1,pos[0],pos[0],pos[0]+1],[pos[1],pos[1]-1,pos[1]+1,pos[1]]):
        if (i >= 0) and (i < h) and (z >= 0) and (z <w):
            if (A_map[i][z] != 'U') and ('W' not in A_map[i][z]) and ('P' not in A_map[i][z]):
                return_list.append([i,z])
    if(len(return_list)==0):
        return []
    return return_list

def BFS(A_map,h,w,cur_pos,des_pos):
    exp_list=[]
    frontier=[]
    comp=False
    frontier.append([cur_pos.copy(),cur_pos.copy()])
    while(len(frontier)>0):
        cur=frontier[0]
        exp_list.append([cur[0].copy(),cur[1].copy()])
        son = next_step(A_map,cur[0],h,w)
        for i in son:
            if i==des_pos :
                exp_list.append([des_pos.copy(),cur[0].copy()])
                frontier.pop(0)
                comp=True
                break
        if comp :
            break
        for i in son:
            check=True
            for z in exp_list:
                if i==z[0]:
                    check=False
                    break
            if check :
                for z in frontier:
                    if i==z[0]:
                        check=False
                        break
            if check :
                frontier.append([i.copy(),cur[0].copy()])
        frontier.pop(0)
    re_path=[]
    cur=exp_list[-1]
    while(cur[0]!=cur_pos):
        re_path.append(cur[0].copy())
        for i in exp_list:
            if i[0]==cur[1]:
                cur=i
                break
    re_path.reverse()
    return re_path


        # Ham kiem tra 1 o unexplored
def Check(A_map,pos,h,w):
    print('Thinking about (' + str(h-pos[0]+1) + ' , ' + str(pos[1]) + '):')
    Near_list = []
    have_breeze=False
    have_stench= False
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if (pos[0]+i >=0) and (pos[0]+i <h) and (pos[1]+z >=0) and (pos[1]+z <w):
            if A_map[pos[0]+i][pos[1]+z] != 'U':
                Near_list.append([pos[0]+i,pos[1]+z])
                if 'B' in A_map[pos[0]+i][pos[1]+z]:
                    have_breeze=True
                if 'S' in A_map[pos[0]+i][pos[1]+z]:
                    have_stench=True

    if len(Near_list)==0:
        return False

    # tao KB
    kb = KB()
    # them thong tin cho KB
    for i in Near_list:
        Add_Clause(kb,A_map,i,w,h)
    state = ''
    print('Having Wumpus?')
    if have_stench:
        # kiem tra xem co Wumpus:
        clause = '(-W'+str(h-pos[0]+1)+str(pos[1])+')'
        result = pl_resolution(kb,clause)
        if result:
            print('Yes')
            state+='W'      # co Wumpus
        else:
            print('Unknow')
            print('Not having Wunpus?')
            clause = '(W'+str(h-pos[0]+1)+str(pos[1])+')'
            result = pl_resolution(kb,clause)
            if result:
                print('Yes')
                state +='-W'
            else:
                print('Unknow')
    else:
        print('No')
        state +='-W'
    print('Having Pit?')
    if have_breeze:
        #kiem tra xem co Pit:
        clause = '(-P'+str(h-pos[0]+1)+str(pos[1])+')'
        result = pl_resolution(kb,clause)
        if result:
            print('Yes')
            state+='P'      # co Pit
        else:
            print('Unknow')
            print('Not having Pit?')
            clause = '(P'+str(h-pos[0]+1)+str(pos[1])+')'
            result = pl_resolution(kb,clause)
            if result:
                print('Yes')
                state += '-P'
            else:
                print('Unknow')
    else:
        print('No')
        state +='-P'
    print("====================================================")
    if state == '':     #khong xac dinh
        A_map[pos[0]][pos[1]]='U'
        return False

    if (state =='WP'):   #co Wumpus va Pit
        A_map[pos[0]][pos[1]]='WP'
        return False

    if (state == '-WP') or (state == 'P'):      #khong co Wumpus chi co Pit
        A_map[pos[0]][pos[1]]='P'
        return False

    if (state == 'W-P') or (state == 'W'):      #co Wumpus khong co Pit
        A_map[pos[0]][pos[1]]='W'
        return False

    if state == '-W-P':     #safe
        A_map[pos[0]][pos[1]]='-'
        return True
    return False


        # Ham tim cac o co stench
def Find_Stench(A_map,cur_pos,h,w):
    result_list = []
    for i in range(h):
        for z in range(w):
            if ('S' in A_map[i][z]) and ('W' not in A_map[i][z]) and ('P' not in A_map[i][z]):
                result_list.append([i,z])
    if len(result_list)==0:
        return []
    result_list.sort(key = lambda x: Manhattan(x,cur_pos))
    return result_list[0]


        # Ham Dung Arrow


    # Ham do uu tien
def Count_Stench(A_map,pos,h,w):
    
    if 'W' in A_map[pos[0]][pos[1]]:
        return -100
    Near_list = []
    have_breeze=False
    have_stench= False
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if (pos[0]+i >=0) and (pos[0]+i <h) and (pos[1]+z >=0) and (pos[1]+z <w):
            if A_map[pos[0]+i][pos[1]+z] != 'U':
                Near_list.append([pos[0]+i,pos[1]+z])

    # tao KB
    kb = KB()
    # them thong tin cho KB
    for i in Near_list:
        Add_Clause(kb,A_map,i,w,h)
        # kiem tra xem co Wumpus:
    for i in kb.clauses:
        print(i)
    clause = '(-W'+str(pos[0])+str(pos[1])+')'
    result = pl_resolution(kb,clause)
    if result:
        return -100
    clause = '(W'+str(pos[0])+str(pos[1])+')'
    result = pl_resolution(kb,clause)
    if result:
        return 100
    count=0
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if(pos[0]+i >=0) and (pos[0]+i <h) and (pos[1]+z >=0) and (pos[1]+z <w):
            if 'S' in A_map[pos[0]+i][pos[1]+z]:
                count = count-1
    return count



    # Ham tim thu tu ban:
def Wumpus_in(A_map,cur_pos,h,w):
    result_list = []
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if(cur_pos[0]+i >=0) and (cur_pos[0]+i <h) and (cur_pos[1]+z >=0) and (cur_pos[1]+z <w):
            if ('U' in A_map[cur_pos[0]+i][cur_pos[1]+z]) or ('W' in A_map[cur_pos[0]+i][cur_pos[1]+z]):
                result_list.append([cur_pos[0]+i,cur_pos[1]+z])
    if len(result_list) ==0:
        return []
    result_list.sort(key = lambda x: Count_Stench(A_map,x,h,w))
    return result_list



    # Ham cap nhat Stench
def Update_Stench(A_map,G_map,pos,h,w):
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if(pos[0]+i >=0) and (pos[0]+i <h) and (pos[1]+z >=0) and (pos[1]+z <w):
            if 'W' in G_map[pos[0]+i][pos[1]+z]:
                if A_map[pos[0]][pos[1]] != 'U':
                    A_map[pos[0]][pos[1]] = G_map[pos[0]][pos[1]]
                return None
    G_map[pos[0]][pos[1]] = G_map[pos[0]][pos[1]].replace('S','')
    if(len(G_map[pos[0]][pos[1]]) ==0):
        G_map[pos[0]][pos[1]] = '-'
    if A_map[pos[0]][pos[1]] != 'U':
        A_map[pos[0]][pos[1]] = G_map[pos[0]][pos[1]]
    return None


    # Ham cap nhat ban do
def Update_map(A_map,G_map,pos,h,w):
    G_map[pos[0]][pos[1]] = G_map[pos[0]][pos[1]].replace('W','')
    if(len(G_map[pos[0]][pos[1]]) ==0):
        G_map[pos[0]][pos[1]] = '-'
    for (i,z) in zip([-1,0,0,1],[0,-1,1,0]):
        if(pos[0]+i >=0) and (pos[0]+i <h) and (pos[1]+z >=0) and (pos[1]+z <w):
            Update_Stench(A_map,G_map,[pos[0]+i,pos[1]+z],h,w)
    return True


    #ham ban cung
def Using_arrow(cur_pos,A_map,G_map,h,w):
    Stench_pos = Find_Stench(A_map,cur_pos,h,w)
    if len(Stench_pos)==0:
        return []
    path = BFS(A_map,h,w,cur_pos,Stench_pos)

    if(len(path)>0):
        cur_pos = path[-1].copy()
    Goal_list = Wumpus_in(A_map,cur_pos,h,w)
    for i in Goal_list:
        path.append([-1,i[0],i[1]])
        Update_map(A_map,G_map,[i[0],i[1]],h,w)
        if 'S' not in G_map[cur_pos[0]][cur_pos[1]]:
            A_map[cur_pos[0]][cur_pos[1]] = G_map[cur_pos[0]][cur_pos[1]]
            cur_pos[0] = i[0]
            cur_pos[1] = i[1]
            path.append(cur_pos)
            return path
    return path


        #Ham van hanh
def Play_Game(file_name):
    
    # khoi tao cac bien tro choi:
    [G_map,h,w,Start_pos] = read_file(file_name)
    A_map = Init_Amap(G_map,Start_pos,h,w)
    cur_pos = Start_pos
    path = []
    # Vong lap tro choi
    while(not Is_Completed(A_map,h,w)):
        can_go = False
        # Xet tat ca cac o unexplored co the di
        next_list = Can_Reach(A_map,h,w,cur_pos)
        for pos in next_list:
            can_go = Check(A_map,pos,h,w)
            if(can_go):
                temp_path = BFS(A_map,h,w,cur_pos,pos)
                if len(temp_path) == 0:
                    can_go = False
                else:
                    path = path + temp_path
                    cur_pos = pos
                    can_go = True
                    break

        # Neu khong tim duoc o moi thi den o co stench de dung cung
        if(not can_go):

            temp_path = Using_arrow(cur_pos,A_map,G_map,h,w)
            if len(temp_path) ==0:
                break
            path = path + temp_path
            cur_pos[0] = path[-1][0]
            cur_pos[1] = path[-1][1]
            can_go = True
        # Neu khong ban cung duoc thi se thoat game:
        if(not can_go):
            break

        # Neu da co the di hoac ban duoc Wumpus thi cap nhat A_map
        A_map[cur_pos[0]][cur_pos[1]] = G_map[cur_pos[0]][cur_pos[1]]
        if 'G' in A_map[cur_pos[0]][cur_pos[1]]:
            A_map[cur_pos[0]][cur_pos[1]] = A_map[cur_pos[0]][cur_pos[1]].replace('G','')
            if len(A_map[cur_pos[0]][cur_pos[1]]) ==0:
                A_map[cur_pos[0]][cur_pos[1]] = '-'
            G_map[cur_pos[0]][cur_pos[1]] = A_map[cur_pos[0]][cur_pos[1]]


    # Ket thuc vong lap tro choi:

    # tim duong ve cua hang
    temp_path = BFS(A_map,h,w,cur_pos,Start_pos)
    path = path + temp_path
    print('-----------------------------')
    rs=[list(i) for i in path]
    for i in range(len(rs)):
        rs[i][0]=h-rs[i][0]+1
    print(rs)
    print('-----------------------------')

    return path

