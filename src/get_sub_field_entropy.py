#=====================================================================================
#title  : get_sub_field_entropy.py
#author  : Li Qi
#e-mail  : liqilcn@sjtu.edu.cn or qili_xidian@163.com
#date  : 20200819
#=====================================================================================

import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import treelib as tl
import queue
import math
import csv
import os
import json

class MyNode:
    def __init__(self,ID,label,year):
        self.ID = ID
        self.Label = label
        self.Year = year
        self.Cite = []
        self.BeCited = []
        self.OriginCite = []
        self.OriginBeCited = []

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

    def AppendOriginCite(self,paper):
        self.OriginCite.append(paper)

    def AppendOriginBeCited(self,paper):
        self.OriginBeCited.append(paper)

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
    
    def ReturnOriginCite(self):
        return self.OriginCite

    def ReturnOriginBeCited(self):
        return self.OriginBeCited

    def ReturnOriginCiteTimes(self):
        return len(self.OriginCite)

    def ReturnOriginBeCitedTimes(self):
        return len(self.OriginBeCited)

def SubTreeEntropySum(NodeNow):
    # 获取子树的所有节点的树熵之和
    # EntropyIndex:节点在脉络树中的树熵
    SubTreeTreeEntropySum = float(id2tree_entropy[str(NodeNow.ReturnID())])
    for NodeLinked in NodeNow.ReturnBeCited():
        SubTreeTreeEntropySum = SubTreeTreeEntropySum + SubTreeEntropySum(NodeLinked)
    return SubTreeTreeEntropySum

def get_sub_field_entropy(skeleton_tree, id2t_entropy, target_pid):
    # 生成脉络树的最大有偏树熵
    global id2tree_entropy
    id2tree_entropy = id2t_entropy
    id2node = {}
    NodeList = []

    node_detail = skeleton_tree

    for node in node_detail:
        ID = str(node)
        node = str(node)
        label = node_detail[node]['label']
        year = node_detail[node]['year']
        NewNode = MyNode(ID,label,year)
        id2node[node] = NewNode

    for node in id2node:
        for nd in node_detail[node]['cite']:
            id2node[node].AppendCite(id2node[str(nd)])
        for nd in node_detail[node]['becited']:
            id2node[node].AppendBeCited(id2node[str(nd)])
        NodeList.append(id2node[node])

    NodeNow = id2node[str(target_pid)]
	
    return SubTreeEntropySum(NodeNow)