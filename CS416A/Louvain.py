import networkx as nx
import numpy as np
import operator
import itertools
from networkx.algorithms.community.quality import modularity
from networkx.linalg.modularitymatrix import modularity_matrix
from networkx.utils.mapped_queue import MappedQueue
from numpy import linalg as LA
import time
from graph_tool.all import *
import sys

G = Graph()
weights = G.new_edge_property("int")
G.edge_properties["weight"]=weight_dict



f=open(sys.argv[1], "r")
for line in list(f.readlines()):
	new_edge=line.split()
	e=G.add_edge(int(new_edge[0]), int(new_edge[1]))
	weights[e]=int(new_edge[2])

