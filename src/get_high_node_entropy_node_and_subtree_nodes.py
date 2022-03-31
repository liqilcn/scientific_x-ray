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
    
    
def get_subtree_nodes_recursion(NodeNow):
    # 递归遍历子树，获取子树的所有节点id
    global subtree_nodes, leading_node_entropy
    for NodeLinked in NodeNow.ReturnBeCited():
        subtree_nodes.append(NodeLinked.ReturnID())
#         print(len(NodeLinked.ReturnBeCited()))
        if pid2node_entropy[str(NodeLinked.ReturnID())] > leading_node_entropy:
            continue
        get_subtree_nodes_recursion(NodeLinked)

def get_subtree_nodes(NodeNow, p_id):
    global subtree_nodes, leading_node_entropy
    leading_node_entropy = pid2node_entropy[p_id]
    subtree_nodes = []
    get_subtree_nodes_recursion(NodeNow)
    return subtree_nodes

def get_high_node_entropy_and_subtree_nodes(pid):
    # 树结构初始化
    id2node = {}
    NodeList = []

    node_detail = json.load(open(f'../temp_files/skeleton_tree_by_year/{pid}/2019', 'r'))
    
    tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/2019', 'r'))
    pid2depth = {}
    for dp in tree_node_deep:
        for p_id in tree_node_deep[dp]:
            pid2depth[str(p_id)] = dp

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

    # 获取所有点熵数值超过10的节点
    global pid2node_entropy
    pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/2019', 'r'))
    selected_pids = []  # 所有点熵超过10的节点
    for p_id, node_entropy in sorted(pid2node_entropy.items(), key=lambda item:item[1], reverse=True):
        if p_id == pid:
            continue
        if node_entropy >= 10:
            selected_pids.append(p_id)
        else:
            break
    # 遍历子树，获取选定节点的子树中所有节点id
    selected_pid2subtree_nodes = {}
    for p_id in selected_pids:
        NodeNow = id2node[str(p_id)]
        subtree_nodes = get_subtree_nodes(NodeNow, p_id)
        selected_pid2subtree_nodes[p_id] = subtree_nodes
    return selected_pid2subtree_nodes


def get_high_node_entropy_and_subtree_nodes(pid):
    # 树结构初始化
    id2node = {}
    NodeList = []
    year_now = 2021
    node_detail = json.load(open(f'../temp_files/skeleton_tree_by_year/{pid}/{year_now}', 'r'))
    
    tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/{year_now}', 'r'))
    pid2depth = {}
    for dp in tree_node_deep:
        for p_id in tree_node_deep[dp]:
            pid2depth[str(p_id)] = dp

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

    # 获取所有点熵数值超过10的节点
    global pid2node_entropy
    pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/{year_now}', 'r'))
    selected_pids = []  # 所有点熵超过10的节点
    for p_id, node_entropy in sorted(pid2node_entropy.items(), key=lambda item:item[1], reverse=True):
        if p_id == pid:
            continue
        if node_entropy >= 10:
            selected_pids.append(p_id)
        else:
            break
    # 遍历子树，获取选定节点的子树中所有节点id
    selected_pid2subtree_nodes = {}
    for p_id in selected_pids:
        NodeNow = id2node[str(p_id)]
        subtree_nodes = get_subtree_nodes(NodeNow, p_id)
        selected_pid2subtree_nodes[p_id] = subtree_nodes
    return selected_pid2subtree_nodes

def get_high_node_entropy_and_subtree_nodes_by_year(pid, yr):
    # 树结构初始化
    id2node = {}
    NodeList = []

    node_detail = json.load(open(f'../temp_files/skeleton_tree_by_year/{pid}/{yr}', 'r'))
    
    tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/{yr}', 'r'))
    pid2depth = {}
    for dp in tree_node_deep:
        for p_id in tree_node_deep[dp]:
            pid2depth[str(p_id)] = dp

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

    # 获取所有点熵数值超过10的节点
    global pid2node_entropy
    pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/{yr}', 'r'))
    selected_pids = []  # 所有点熵超过10的节点
    for p_id, node_entropy in sorted(pid2node_entropy.items(), key=lambda item:item[1], reverse=True):
        if p_id == pid:
            continue
        if node_entropy >= 10:
            selected_pids.append(p_id)
        else:
            break
    # 遍历子树，获取选定节点的子树中所有节点id
    selected_pid2subtree_nodes = {}
    for p_id in selected_pids:
        NodeNow = id2node[str(p_id)]
        subtree_nodes = get_subtree_nodes(NodeNow, p_id)
        selected_pid2subtree_nodes[p_id] = subtree_nodes
    return selected_pid2subtree_nodes