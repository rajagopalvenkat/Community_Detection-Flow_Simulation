import community
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import sys

G=nx.Graph()
f=open(sys.argv[1], "r")

for line in list(f.readlines()):
	x=line.split()
	G.add_edge(x[0],x[1])

out=open("mod_coms", "w")
c = community.best_partition(G)
for k,v in c.items():
	out.write(str(k) + " " + str(v) + "\n")
