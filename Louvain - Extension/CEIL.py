#!/usr/bin/python

"""
Copyright (c) 2009, Thomas Aynaud <thomas.aynaud@lip6.fr>
All rights reserved.
"""

"""
This module implements the community detection "CEIL"" described in the paper "CEIL: A scalable, resolution limit free approach for detecting communities in large networks".
This code is a derivation from the implementation of python-Louvain by Thomas Aynaud. The python-Louvain code can be found at https://bitbucket.org/taynaud/python-louvain. 
"""

__all__ = ["best_partition","partition_at_level","generate_dendogram","induced_graph"]

__MIN = 0.0000001

import sys
from collections import defaultdict
from gmpy import comb
import time

def best_partition(graph) :
    """
    Compute the partiton of the graph which maximises the score
    Parameters
    ----------
    graph : An object of the class Graph
        The input graph.
    Returns
    -------
    partition : dictionary
        Key is the node and Value is the community of the node.
    """
    dendogram = generate_dendogram(graph)
    partition = partition_at_level(dendogram, len(dendogram)-1)
    return partition

def partition_at_level(dendogram, level) :
    partition = dendogram[0].copy()
    for index in range(1, level+1) :
        for node, community in partition.items() :
            partition[node] = dendogram[index][community]
    return partition

def generate_dendogram(graph) :
    """
    Computes the dendogram structure of the partition
    Parameters
    ----------
    graph : An object of the class Graph
        The input graph.
    Returns
    -------
    dendo : List of dictionaries
        Key is the node and Value is the community of the node in every dictionary.
    """
    status = Status()
    status.init(graph)
    dendo = list()
    __one_level(graph, status)
    partition = __renumber(status.node2com)
    dendo.append(partition)
    cur_score = __score(status)
    current_graph = induced_graph(partition, graph)
    status.init(current_graph)
    while True:
        __one_level(current_graph, status)
        new_score = __score(status)
        if (new_score - cur_score) < __MIN :
            break
        partition = __renumber(status.node2com)
        #print partition
        dendo.append(partition)
        cur_score = new_score
        current_graph = induced_graph(partition, current_graph)
        status.init(current_graph)
    return dendo

def induced_graph(partition, graph) :
    """
    Constructs a graph where a community is a node
    """
    induced_graph = Graph()
    induced_graph.nodes = set(partition.values())
    for edge, weight in graph.edge2weight.items() :
        node1, node2 = edge
        com1 = partition[node1]
        com2 = partition[node2]
        if com1 == com2 :
            induced_graph.node2internal[com1] = induced_graph.node2internal.get(com1, 0) + (0.5 * weight)
        else :
            induced_graph.node2neighbors[com1].add(com2)
            induced_graph.node2neighbors[com2].add(com1)
            induced_graph.edge2weight[(com1,com2)] = induced_graph.edge2weight.get((com1,com2), 0) + weight
    for node in partition.keys() :
        com = partition[node]
        induced_graph.node2internal[com] = induced_graph.node2internal.get(com,0) + graph.node2internal[node]
        induced_graph.node2degree[com] = induced_graph.node2degree.get(com, 0) + graph.node2degree[node]
        induced_graph.node2number_of_nodes[com] = induced_graph.node2number_of_nodes.get(com, 0) + graph.node2number_of_nodes[node]
    induced_graph.node_count = graph.node_count
    return induced_graph

def __one_level(graph, status) :
    modif = True
    new_score = __score(status)
    while modif :
        cur_score = new_score
        modif = False
        for node in graph.nodes :
            com = status.node2com[node]
            node_internal = graph.internal(node)
            node_deg = graph.degree(node)
            node_number = graph.number_of_nodes(node)
            weights = __neighcomm(node, graph, status)
            neighbor_communities = weights.keys()
            cur_score = status.com2score[com]
            new_score = __remove(node, node_internal, node_deg, node_number, com, weights, status, graph.node_count)
            best_com = com
            best_increase = cur_score - new_score
            for neighbor_community in neighbor_communities :
                internal = status.com2internal[neighbor_community] + node_internal + weights[neighbor_community]
                degree = status.com2degree[neighbor_community] + node_deg
                number_of_nodes = status.com2total_nodes[neighbor_community] + node_number
                cur_score = status.com2score[neighbor_community]
                new_score = score(internal, degree, number_of_nodes, graph.node_count)
                increase = new_score - cur_score
                if increase > best_increase :
                    best_com = neighbor_community
                    best_increase = increase
            if best_com != com :
                modif = True
            node_internal += weights.get(best_com,0)
            __insert(node, node_internal, node_deg, node_number, best_com, best_increase, status)
        new_score = __score(status)
        if (new_score - cur_score) < __MIN :
            break

def __renumber(dictionary) :
    """
    Renumber the values of the dictionary from 0 to n
    """
    count = 0
    ret = dictionary.copy()
    mapping = dict()
    for key in dictionary.keys() :
        value = dictionary[key]
        new_value = mapping.get(value, -1)
        if new_value == -1 :
            mapping[value] = count
            new_value = count
            count += 1
        ret[key] = new_value
    return ret
            
def score(internal, degree, number_of_nodes, total_nodes) :
    """
    Returns the score for a single community 
    """
    community_score = 0.
    external = degree - (2*internal)
    if number_of_nodes == 0 :
        pass
    elif number_of_nodes == 1 :
        pass
    else :
        separability = internal / float(internal + external)
        internal_density = internal / float(comb(number_of_nodes,2))
        community_score = separability * internal_density
    actual_score = (number_of_nodes / float(total_nodes)) * community_score
    return actual_score

class Status :
    """
    Store the current status of the communities
    """
    community_count = 0
    node2com = {}
    com2internal = {}
    com2degree = {}
    com2total_nodes = {}
    com2score = {}
    total_nodes = 0

    def __init__(self) :
        self.node2com = dict()
        self.com2internal = dict()
        self.com2degree = dict()
        self.com2total_nodes = dict()
        self.com2score = dict()
        self.total_nodes = 0

    def init(self, graph) :
        self.__init__()
        community_count = 0
        for node in graph.nodes :
            self.node2com[node] = community_count
            self.com2internal[community_count] = graph.internal(node)
            self.com2degree[community_count] = graph.degree(node)
            self.com2total_nodes[community_count] = graph.number_of_nodes(node)
            community_count += 1
        self.total_nodes = graph.node_count
        for com in range(community_count) :
            self.com2score[com] = score(self.com2internal[com], self.com2degree[com], self.com2total_nodes[com],graph.node_count)

def __score(status) :
    """
    Calculates the score faster using the status
    """
    node_count = status.total_nodes
    score = 0.
    for community in status.com2internal.keys() :
        #number_of_nodes = status.com2total_nodes[community]
        community_score = status.com2score[community]
        #score += (number_of_nodes / float(node_count) * community_score)
        score += community_score
    return score

def __neighcomm(node, graph, status) :
    """
    Computes the weights to communities of neighbors
    """
    neighbors = graph.neighbors(node)
    weights = {}
    for neighbor in neighbors :
        neigh_com = status.node2com[neighbor]
        weights[neigh_com] = weights.get(neigh_com, 0) + graph.weight(node, neighbor)
    return weights

def __remove(node, node_internal, node_deg, node_number, com, weights, status, total_nodes) :
    status.node2com[node] = -1
    internal = status.com2internal[com] - node_internal - weights.get(com,0)
    status.com2internal[com] = internal
    degree = status.com2degree[com] - node_deg
    status.com2degree[com] = degree
    number_of_nodes = status.com2total_nodes[com] - node_number
    status.com2total_nodes[com] = number_of_nodes
    new_score = score(internal, degree, number_of_nodes, total_nodes)
    status.com2score[com] = new_score
    return new_score

def __insert(node, internal, deg, number_of_nodes, com, increase, status) :
    status.node2com[node] = com
    status.com2internal[com] += internal
    status.com2degree[com] += deg
    status.com2total_nodes[com] += number_of_nodes
    status.com2score[com] += increase

class Graph :
    """
    Stores a graph
    """
    nodes = set()
    node2neighbors = defaultdict(set)
    edge2weight = {}
    node2internal = {}
    node2degree = {}
    node2number_of_nodes = {}
    node_count = 0
    
    def __init__(self) :
        self.nodes = set()
        self.node2neighbors = defaultdict(set)
        self.edge2weight = dict()
        self.node2internal = dict()
        self.node2degree = dict()
        self.node2number_of_nodes = dict()
        self.node_count = 0

    def read(self, graph_file_name) :
        """
        Reads the graph from the input file and stores it. 
        The input format is edge list.
        """
        graph_file = open(graph_file_name)
        for line in graph_file :
            (nodeA,nodeB) = line.split()
            self.node2neighbors[nodeA].add(nodeB)
            self.node2neighbors[nodeB].add(nodeA)
            self.edge2weight[(nodeA,nodeB)] = 1
            self.edge2weight[(nodeB,nodeA)] = 1
        graph_file.close()
        self.nodes = set(self.node2neighbors.keys())
        for node in self.nodes :
            deg = len(self.node2neighbors[node])
            self.node2degree[node] = deg
            self.node2internal[node] = 0
            self.node2number_of_nodes[node] = 1
        self.node_count = len(self.nodes)
        
    def neighbors(self,node) :
        """
        Returns the neighbors of the node
        """
        return self.node2neighbors[node]

    def weight(self,nodeA,nodeB) :
        """
        Returns the weight of the edge between nodeA and nodeB
        """
        return self.edge2weight[(nodeA,nodeB)]

    def internal(self,node) :
        """
        Returns the internals of the node
        """
        return self.node2internal[node]

    def degree(self,node) :
        """
        Returns the degree of the node
        """
        return self.node2degree[node]

    def number_of_nodes(self,node) :
        """
        Returns the number of nodes of the hyper node
        """
        return self.node2number_of_nodes[node]

def execute(input_file_name,output_file_name) :
    graph = Graph()
    graph.read(input_file_name)
    partition = best_partition(graph)
    output_file = open(output_file_name,'w')
    for node, community in partition.items() :
        output_file.write(str(node)+" "+str(community)+"\n")
    output_file.close()
    return partition

def __main() :
    input_file_name = sys.argv[1]
    graph = Graph()
    graph.read(input_file_name)
    t0 = time.clock()
    partition = best_partition(graph)
    t1 = time.clock()
    time_taken = t1 - t0
    print( "Time Taken : " + str(time_taken))
    output_file_name = sys.argv[2]
    output_file = open(output_file_name,'w')
    for node, community in partition.items() :
        output_file.write(str(node)+" "+str(community)+"\n")
    output_file.close()

if __name__ == "__main__" :
    __main()