import os
import sys
from operator import itemgetter
from math import log10
from random import randint
from threading import *
Vert={}
G={}
visitednodes=[]
origin=[]
add=0
v=[]
print(sys.argv[1])
f=open("../datasets/"+sys.argv[1], "r")
lines=f.readlines()
for line in lines:
	inp=line.split()
	inp=[int(x) for x in inp]
	if inp[0] in G:
		G[inp[0]][0]+=[inp[1],]
		G[inp[0]][1]+=[inp[2],]
	else:
		G[inp[0]]=[[inp[1]], [inp[2]]]
	Vert[inp[0]]=0
	Vert[inp[1]]=0
f.close()
print("Loaded Graph")
print(len(Vert))
numrank=[]
degrank=[]

for key, value in G.items():
	numrank+=[[key, len(value[0])],]
	degrank+=[[key, sum(value[1])],]

numrank=sorted(numrank, key=itemgetter(1))
degrank=sorted(degrank, key=itemgetter(1))

seeds=float(sys.argv[2])
'''
Enter seeds = 1-(k/100)
'''

numrank=numrank[int(len(numrank)*seeds):]
degrank=degrank[int(len(degrank)*seeds):]
numrank=[a[0] for a in numrank]
degrank=[a[0] for a in degrank]

numrank=sorted(numrank)
degrank=sorted(degrank)

origin=[]

i=len(degrank)-1
j=i
while i>=0:
	if degrank[i]>numrank[j]:
		i-=1
	elif degrank[i]<numrank[j]:
		j-=1	
	else:
		origin+=[degrank[i],]
		degrank[i]=-1
		numrank[j]=-1
		i-=1
		j-=1


print("Origin initialized with ", len(origin), " nodes")
i=0




######################################################################################

#UPDATE : This step is unnecessary


'''
# Comment out this section for small graphs

conflicts=[]
knn=0

current=[]
for i in origin:
	current+=[i, ]

def nextN(N, v):
	global conflicts
	global origin
	source=[v]
	vis=[v]
	nex=[]
	for i in range(N):
		nbr=[]
		for node in source:
			if node in G:
				nbr+=G[node][0]
		nbr=list(set(nbr))
		for vert in nbr:
			if vert in origin and vert not in vis:
				conflicts+=[(v, vert),]
		vis+=nbr
		source=[]
		for vert in nbr:
			source+=[vert,]


for o in origin:
	nextN(1, o)


#print(conflicts)
conflicts=list(set(conflicts))
print(len(conflicts))

conf_map={}

for conflict in conflicts:
	if conflict[1] in conf_map:
		conf_map[conflict[1]]+=1
	else:
		conf_map[conflict[1]]=1


'''
#####################################################################################




#print(origin)
print("Spread Start with ", len(origin), " nodes")

for i in origin:
	Vert[i]=i 			# Initialize labels

'''

Replace randomizer here!!!!!!!

Tested randomizers :
	
	Python random library
	Dump of n random numbers from random.org 

TODO  :  Integrate with random.org API instead of using dump.

'''
add=0
rand=open("random", "r")
lines=rand.readlines()
i=0


def spread(arry, tLock):
	global origin
	global G
	global lines
	global visitednodes
	global add
	global Vert
	global i
	for v in arry:
		if v in G:
			c=0
			for j in range(0,len(G[v][0])):
				if Vert[G[v][0][j]]==0:
					c+=1
					if float(lines[(i%len(lines))])<=(((G[v][1][j])**(1/4))/(sum(G[v][1])**(1/4))):  #REPLACE lines[] with random function
					#if randint(0,100)/100 <= (((G[v][1][j])**(1/4))/(sum(G[v][1])**(1/4))):
						tLock.acquire()
						origin+=[G[v][0][j],]
						Vert[G[v][0][j]]=Vert[v]
						add=0
						c-=1
						tLock.release()
				i+=1
			if c==0:
				origin.remove(v)
				visitednodes+=[v,]
		else:
			origin.remove(v)
			visitednodes+=[v,]

def chunkify(lst,n):
		return [ lst[i::n] for i in range(n) ]

threadLock=Lock()
while add<=3:
	add+=1
	threads=[]
	if len(origin)<=200:
		for x in chunkify(origin, int(len(origin)/2)):
			threads.append(Thread(target=spread, args=(x, threadLock)))
	else:
		for x in chunkify(origin,100):
			threads.append(Thread(target=spread, args=(x, threadLock)))
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()

#out=open(sys.argv[1], "w")
out=open("../outputs/"+sys.argv[1]+"_"+str(seeds*100), "w")
for key, val in Vert.items():
	out.write(str(key) + "  " + str(val)+"\n")
out.close()
