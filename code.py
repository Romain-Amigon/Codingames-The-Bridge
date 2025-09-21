import sys
import math
import copy
import random
import time

m = int(input())
v = int(input())
l0 = input()
l1 = input()
l2 = input()
l3 = input()
Carte=[l0,l1,l2,l3]

class moto():
    def __init__(self):
        self.x=0
        self.y=0
        self.vivant=True
    def maj(self,x,y,a):
        self.x=x
        self.y=y
        self.vivant=bool(a)

Motos=[moto() for _ in range(m)]

def verify(motos,Carte,s,v,instruct):
    l=len(Carte[0])
    tmp=[m for m in motos if m.vivant]
    surv=list(tmp)
    if instruct=="SPEED":
        for m in tmp:
            if '0' in Carte[m.y][m.x+1:min(m.x+s+2,l)]:
                surv.remove(m)
                if len(surv)<v: return 0
        return 1
    if instruct=="SLOW":
        if s<=1: return 0
        for m in tmp:
            if '0' in Carte[m.y][m.x:min(l,m.x+s)]:
                surv.remove(m)
                if len(surv)<v: return 0
        return 1
    if instruct=="JUMP":
        for m in tmp:
            if Carte[m.y][min(l-1,m.x+s)]=='0':
                surv.remove(m)
                if len(surv)<v: return 0
        return 1
    if instruct=="UP":
        for m in tmp:
            if m.y==0: return 0
            if '0' in (Carte[m.y][m.x+1:min(l,m.x+s)] + Carte[m.y-1][m.x:min(l,m.x+s+1)]):
                surv.remove(m)
                if len(surv)<v: return 0
        return 1
    if instruct=="DOWN":
        for m in tmp:
            if m.y==3: return 0
            if '0' in (Carte[m.y][m.x+1:min(l,m.x+s)] + Carte[m.y+1][m.x:min(l,m.x+s+1)]):
                surv.remove(m)
                if len(surv)<v: return 0
        return 1
    return 0

def action(motos, s, instruct):
    nm = copy.deepcopy(motos)
    s2 = s
    l = len(Carte[0])

    if instruct == "SPEED":
        for m in nm:
            if '0' in Carte[m.y][m.x+1:min(m.x+s+2, l)]:
                m.vivant = False
            m.x += s + 1
        s2 += 1

    elif instruct == "SLOW":
        for m in nm:
            if '0' in Carte[m.y][m.x:min(l, m.x+s)]:
                m.vivant = False
            m.x += s - 1
        s2 = max(s2 - 1, 0)

    elif instruct == "JUMP":
        for m in nm:
            if Carte[m.y][min(l-1, m.x+s)] == '0':
                m.vivant = False
            m.x += s

    elif instruct == "UP":
        for m in nm:
            if m.y > 0:
                if '0' in (Carte[m.y][m.x+1:min(l, m.x+s)] + Carte[m.y-1][m.x:min(l, m.x+s+1)]):
                    m.vivant = False
                m.x += s
                m.y -= 1

    elif instruct == "DOWN":
        for m in nm:
            if m.y < 3:
                if '0' in (Carte[m.y][m.x+1:min(l, m.x+s)] + Carte[m.y+1][m.x:min(l, m.x+s+1)]):
                    m.vivant = False
                m.x += s
                m.y += 1

    return nm, s2


instructions=["SPEED","JUMP","SLOW","UP","DOWN"]

class leaf:
    def __init__(self,instr,parent):
        self.instr=instr
        self.score=0.0
        self.visits=0
        self.parent=parent
        self.childs=set()

def backpropagate(node,reward):
    while node:
        node.visits+=1
        node.score+=reward
        node=node.parent

def uct(node,pvisits,c=1.41):
    if node.visits==0: return float('inf')
    return node.score/node.visits + c*math.sqrt(math.log(pvisits)/node.visits)

def rollout(motos,Carte,v,s):
    steps=0
    while steps<50:
        if sum(m.vivant and m.x>=len(Carte[0])-1 for m in motos)>=v:
            return 1
        poss=[inst for inst in instructions if verify(motos,Carte,s,v,inst)]
        if not poss: return 0
        inst=random.choice(poss)
        motos,s=action(motos,s,inst)
        steps+=1
    return 0

def dfs(motos, Carte, s, v, depth=5):
    if depth == 0:
        print('eeee')
        return sum(m.vivant  for m in motos) >= v #and m.x >= len(Carte[0])-1

    for inst in instructions:
        if verify(motos, Carte, s, v, inst):
            new_motos, new_s = action(motos, s, inst)
            if dfs(new_motos, Carte, new_s, v, depth-1):
                return True
    return False

def simulate(Motos,Carte,v,s,start):
    root=leaf("",None)
    tree=[root]
    for inst in instructions:
        if verify(Motos,Carte,s,v,inst):
            tree.append(leaf(inst,root))
            root.childs.add(len(tree)-1)
    i=0
    while time.time()-start<0.14:
        current=root
        motos=copy.deepcopy(Motos)
        s2=s
        while current.childs:
            current=max((tree[i] for i in current.childs),
                        key=lambda n: uct(n,n.parent.visits))
            motos,s2=action(motos,s2,current.instr)
        reward=rollout(motos,Carte,v,s2)
        backpropagate(current,reward)
        for inst in instructions:
            if verify(motos,Carte,s2,v,inst):
                tree.append(leaf(inst,current))
                current.childs.add(len(tree)-1)
        i+=1
    return max((tree[i] for i in root.childs),
               key=lambda n: n.score/n.visits if n.visits else 0).instr

while True:
    start=time.time()
    s=int(input())
    for i in range(m):
        x,y,a=[int(j) for j in input().split()]
        Motos[i].maj(x,y,a)
    if s==0:
        print("SPEED")
    else:
        print(simulate(Motos,Carte,v,s,start))
