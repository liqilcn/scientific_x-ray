#=====================================================================================
#title  : gen_tree_analysis_data.py
#author  : Li Qi
#e-mail  : liqilcn@sjtu.edu.cn or qili_xidian@163.com
#date  : 20200711
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

def get_ave_depth(deep2node):
    # 生成当前年份脉络树的平均深度，从根节点开始，根节点的深度为0
    deep_list = []
    for deep in deep2node:
    	for node in deep2node[deep]:
    		deep_list.append(int(deep))
    return np.mean(deep_list)

def get_width(deep2node):
    # 生成当前年份脉络树的宽度（所有层宽度的最大值），从根节点开始，根节点的深度为0
    return max([len(deep2node[deep]) for deep in deep2node])

def get_tree_node_num(skeleton_tree):
	# 生成当前脉络树的节点数目
	return len(skeleton_tree)

def subtree_node_num(Node):
    # 获取根节点A的子树内的节点数量
    NodeList = []
    MyQueue = queue.Queue()
    MyQueue.put(Node)
    while (not(MyQueue.empty())):
        NodeNow = MyQueue.get()
        NodeList.append(NodeNow)
        for NodeLinked in NodeNow.ReturnBeCited():
            MyQueue.put(NodeLinked)
    return len(NodeList)

def get_bias_rate(skeleton_tree, pid):
	# 生成第一层降序排列的有偏程度，以及第一层的最大有偏程度
	node_detail = skeleton_tree
	id2node = {}
	NodeList = []
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
        
	all_node_num = len(id2node)
	bias_rate_list = []
	for Node in id2node[str(pid)].ReturnBeCited():
		bias_rate_list.append(1.0*subtree_node_num(Node) / all_node_num)
 
	return bias_rate_list, max(bias_rate_list)

def SubTreeEntropySum(NodeNow):
    # 获取子树的所有节点的树熵之和
    # EntropyIndex:节点在脉络树中的树熵
    SubTreeTreeEntropySum = float(id2tree_entropy[int(NodeNow.ReturnID())])
    for NodeLinked in NodeNow.ReturnBeCited():
        SubTreeTreeEntropySum = SubTreeTreeEntropySum + SubTreeEntropySum(NodeLinked)
    return SubTreeTreeEntropySum

def get_max_bias_subtree_entropy(pid, skeleton_tree, id2t_entropy):
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

    NodeNow = id2node[str(pid)]  # 找到根节点
    BiasEntropyIndexList = []
    for NodeLinked in NodeNow.ReturnBeCited():
        BiasEntropyIndexList.append(SubTreeEntropySum(NodeLinked))
    BiasEntropyIndexListSum = sum(BiasEntropyIndexList)
    for i in range(len(BiasEntropyIndexList)):
        BiasEntropyIndexList[i] = 1.0*BiasEntropyIndexList[i]/BiasEntropyIndexListSum

    return max(BiasEntropyIndexList)

def SubTreeNodeEntropySum(NodeNow):
    TreeNodeEntropySum = float(id2node_entropy[int(NodeNow.ReturnID())])
    for NodeLinked in NodeNow.ReturnBeCited():
        TreeNodeEntropySum = TreeNodeEntropySum + SubTreeNodeEntropySum(NodeLinked)
    return TreeNodeEntropySum

def get_max_bias_node_entropy(pid, skeleton_tree, id2n_entropy):
    # 生成脉络树的最大有偏点熵
    global id2node_entropy
    id2node_entropy = id2n_entropy
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

    NodeNow = id2node[str(pid)]  # 找到根节点

    BiasNodeEntropyIndexList = []
    for NodeLinked in NodeNow.ReturnBeCited():
        BiasNodeEntropyIndexList.append(SubTreeNodeEntropySum(NodeLinked))
    BiasNodeEntropyIndexListSum = sum(BiasNodeEntropyIndexList)
    for i in range(len(BiasNodeEntropyIndexList)):
        BiasNodeEntropyIndexList[i] = 1.0*BiasNodeEntropyIndexList[i]/BiasNodeEntropyIndexListSum

    return max(BiasNodeEntropyIndexList)