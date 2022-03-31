#=====================================================================================
#title  : gen_tree_node_deep.py
#author  : Li Qi
#e-mail  : liqilcn@sjtu.edu.cn or qili_xidian@163.com
#date  : 20200711
#=====================================================================================

import scipy.linalg as linalg
import networkx as nx
import numpy as np
import treelib as tl
import queue
import chardet
import json
import math
import csv
import os
from readgml import readgml
from graphviz import Digraph
from multiprocessing.pool import Pool

class MyNode:
    def __init__(self,ID,label,year,cite=[],becited=[]):
        self.ID = ID
        self.Label = label
        self.Year = year
        self.Cite = cite[:]
        self.BeCited = becited[:]

    def AppendCite(self,paper):
        self.Cite.append(paper)

    def AppendBeCited(self,paper):
        self.BeCited.append(paper)

    def RemoveCite(self,paper):
        if (paper in self.Cite):
            self.Cite.remove(paper)

    def RemoveBeCited(self,paper):
        if (paper in self.BeCited):
            self.BeCited.remove(paper)

    def ReturnID(self):
        return self.ID

    def ReturnLabel(self):
        return self.Label

    def ReturnYear(self):
        return self.Year

    def ReturnCite(self):
        return self.Cite

    def ReturnBeCited(self):
        return self.BeCited

    def ReturnCiteTimes(self):
        return len(self.Cite)

    def ReturnBeCitedTimes(self):
        return len(self.BeCited)

    def copy(self):
        NewNode = MyNode(self.ID,self.Label,self.URL,self.Cite,self.BeCited)
        return NewNode


def gen_tree_node_deep(id, node_detail):
    # 确定树节点所属的深度数
    id = int(id)
    id2node = {}
    NodeList = []
    for node in node_detail:
        node = str(node)
        ID = node
        label = node_detail[node]['label']
        year = node_detail[node]['year']
        NewNode = MyNode(int(ID),label,year)
        id2node[node] = NewNode
    for node in id2node:
        for nd in node_detail[node]['cite']:
            id2node[node].AppendCite(id2node[str(nd)])
        for nd in node_detail[node]['becited']:
            id2node[node].AppendBeCited(id2node[str(nd)])
        NodeList.append(id2node[node])
        
    # 对脉络树进行广度优先遍历
    i = 0
    deep2node = {}
    deep2node[i] = []
    deep2node[i].append(int(id))
    node_num = 1
    now_deep = []
    now_deep.append(id2node[str(id)])
    while True:
        i += 1
        next_deep = []
        for node in now_deep:
            next_deep.extend(node.ReturnBeCited())
        if i not in deep2node:
            deep2node[i] = []
        for n in next_deep:
            deep2node[i].append(n.ReturnID())
            node_num += 1
        if node_num == len(NodeList):
            break
        else:
            now_deep = next_deep[:]
    return deep2node