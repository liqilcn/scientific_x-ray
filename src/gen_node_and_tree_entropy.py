#=====================================================================================
#title  : gen_node_and_tree_entropy.py
#author  : Li Qi
#e-mail  : liqilcn@sjtu.edu.cn or qili_xidian@163.com
#date  : 20200712
#=====================================================================================
import matplotlib.pyplot as plt
import scipy.linalg as linalg
import networkx as nx
import numpy as np
import treelib as tl
import datetime
import queue
import json
import math
import csv
import os
from readgml import readgml
from graphviz import Digraph
from tqdm import tqdm_notebook as tqdm
from itertools import combinations, permutations
from multiprocessing.pool import Pool

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


def Entropy_1(NodeParent,Node,TotalSize, id2v_a, id2g_a):
    # 求树熵
    EdgeCount = len(id2g_a[Node.ReturnID()])
    v = len(id2v_a[NodeParent.ReturnID()])
    v_a = len(id2v_a[Node.ReturnID()])

    return -1.0 * EdgeCount * 0.5 / TotalSize * math.log(1.0*v_a/v)

def MutualEntropy_1(NodeParent,Node1,Node2,TotalSize, id2v_a, id2g_a):
    # 求互知识熵
    parent_node = id2v_a[NodeParent.ReturnID()]
    child_node_union = id2v_a[Node1.ReturnID()].union(id2v_a[Node2.ReturnID()])
    temp_g = id2g_a[Node1.ReturnID()].union(id2g_a[Node2.ReturnID()])
    num = 0
    for e in temp_g:
        e_0 = int(e.split('|')[0])
        e_1 = int(e.split('|')[1])
        if e_0 in child_node_union and e_1 in child_node_union:
            num += 1
    EdgeCount = len(temp_g) - num

    v_a = len(id2v_a[Node1.ReturnID()])
    v_b = len(id2v_a[Node2.ReturnID()])
    v = len(id2v_a[NodeParent.ReturnID()])
    
    return -1.0 * EdgeCount * 0.25 / TotalSize * math.log(1.0*v_a*v_b/(v*v))

def gen_subtree_parm(id, id2node, tree_node_deep):
    # 用于生成计算互熵的相关参数即每个子树的节点v，以及每个子树对应的g的边，对求互熵进行提速
    deep = len(tree_node_deep)
    id2g_a = {}  # a为根节点的g_a
    id2v_a = {}  # a为根节点的v_a

    for n in id2node:
        id2g_a[n] = set()
        id2v_a[n] = set()
    for i in reversed(range(deep)):
        now_deep_list = tree_node_deep[i]
        for node in now_deep_list:
            id2v_a[node].add(node)# 计入根节点的数目
            for n in id2node[node].ReturnBeCited():
                for n_0 in id2v_a[n.ReturnID()]:
                    # 加入孩子节点内的节点
                    id2v_a[node].add(n_0)

        for node in now_deep_list:
            for n in id2node[node].ReturnOriginCite():
                # 加入根节点的外引用
                if n.ReturnID() not in id2v_a[node]:
                    id2g_a[node].add(str(node)+'|'+str(n.ReturnID()))
            for n in id2node[node].ReturnOriginBeCited():
                # 加入根节点的外被引
                if n.ReturnID() not in id2v_a[node]:
                    id2g_a[node].add(str(n.ReturnID())+'|'+str(node))

            for n in id2node[node].ReturnBeCited():
                for e_0 in id2g_a[n.ReturnID()]:
                    # 加入孩子节点内的节点
                    if not(int(e_0.split('|')[0]) in id2v_a[node] and int(e_0.split('|')[1]) in id2v_a[node]):
                        id2g_a[node].add(e_0)
                    
    return id2v_a, id2g_a


def clean_reference_data(nodes, edges, top_id):
    # 去除发表日期大于当前日期的论文及其引用关系,这种情况有可能出现，但对学术脉络发展来说，不会对后面的脉络产生太大影响
    # 去除两篇文章之间的互引
    # 去除网络中存在的有向环
    # 存在开山作发表前的文章
    # 开山作引用别的文章的边
    import time
    source_nodes_len = len(nodes)
    source_edges_len = len(edges)
    yyy = datetime.datetime.now().year
    mmm = datetime.datetime.now().month
    ddd = datetime.datetime.now().day
    time_stamp_flag = int(time.mktime(time.strptime(f'{yyy}-{mmm}-{ddd}', '%Y-%m-%d')))  # 只需更改这个flag值即可更改论文的最新年份的界限
    top_paper_time_stamp = 0
    out_date_id_set = set()
    id2time_stamp = {}
    G = nx.DiGraph()

    for node in nodes:
        if node['id'] == top_id:
            top_paper_time_stamp = int(time.mktime(time.strptime(node['date'], '%Y-%m-%d')))
    for node in nodes:
        id = node['id']
        date = node['date']
        node_time_stamp = int(time.mktime(time.strptime(date, '%Y-%m-%d')))
        id2time_stamp[id] = node_time_stamp
        # 将出版日期异常的点加入集合中
        if node_time_stamp > time_stamp_flag or node_time_stamp < top_paper_time_stamp:
            out_date_id_set.add(id)

    # 去除日期异常的节点
    nodes_copy = nodes[:]
    for node in nodes:
        if node['id'] in out_date_id_set:
            nodes_copy.remove(node)
    # 去除含有异常日期的边
    edges_copy = edges[:]
    cut_edge_num = 0
    for edge in edges:
        # 去掉时间不在演进范围内节点相关的边
        if edge['source'] in out_date_id_set or edge['target'] in out_date_id_set:
            edges_copy.remove(edge)
            cut_edge_num += 1
        # 去掉top_paper引用别人的边
        if edge['source'] == top_id:
            try:
                edges_copy.remove(edge)
                cut_edge_num += 1
            except:
                pass
    
    for node in nodes_copy:
        G.add_node(node['id'])
    for edge in edges_copy:
        G.add_edge(edge['source'], edge['target'])
    need_cut_edge = []
    try:
        Data = nx.find_cycle(G)
        ii = 0
        iii = 0
        while (Data):
            if len(Data) == 2:
                # 两篇paper互引的情况，根据两篇文章的发表顺序修复
                node_id_0 = Data[0][0]
                node_id_1 = Data[0][1]

                node_0_time_stamp = id2time_stamp[node_id_0]
                node_1_time_stamp = id2time_stamp[node_id_1]

                if node_0_time_stamp >= node_1_time_stamp:
                    need_cut_edge.append((node_id_1, node_id_0))
                    G.remove_edge(node_id_1,node_id_0)
                    ii += 1
                else:
                    need_cut_edge.append((node_id_0, node_id_1))
                    G.remove_edge(node_id_0,node_id_1)
                    iii += 1
            else:
                # 有向环去除，根据论文的发表顺序
                cut_flag = 0
                for ed in Data:
                    if id2time_stamp[ed[1]] >= id2time_stamp[ed[0]]:
                        cut_flag = 1
                        need_cut_edge.append(ed)
                        G.remove_edge(ed[0],ed[1])
                if cut_flag == 0:
                    # 如果自环存在
                    # 此if永远不会成立
                    pass
            try:
                Data = nx.find_cycle(G) # 切断一个环，继续寻找
            except:
                break
    except:
        pass
    nodes = []
    nodes = nodes_copy[:] # 要加[:]，不然是引用赋值，容易造成错误
    edges = []
    edges = edges_copy[:]
    
    remed_edge = []
    for edge in edges_copy:
        for nd_cut_edge in need_cut_edge:
            if edge['source'] == nd_cut_edge[0] and edge['target'] == nd_cut_edge[1]:
                remed_edge.append(edge)
                edges.remove(edge)

    if len(nodes) + len(out_date_id_set) != source_nodes_len or len(edges) + len(need_cut_edge) + cut_edge_num != source_edges_len:
        print('error')
    
    return nodes, edges


def gen_entropy(id, skeleton_tree, deep2node, INPUT_FILE_PATH):
    
    id = int(id)

    nodes, edges = readgml.read_gml(INPUT_FILE_PATH)
    nodes, edges = clean_reference_data(nodes, edges, int(id))

    NodeList = []
    NodeIDList = {}
    id2node = {}

    NodeCount = 0
    for node in nodes:
        NodeCount = NodeCount + 1
        label = node.get('label', '')
        ID = node['id']
        year = node['date'][0:4]
        labelnew = ''
        for i in label: # 去除异常编码
            if ((0 <= ord(i)) and (ord(i) <= 127)): # ord函数，输入一个字符输出一个ascii或者unicode编码
                labelnew = labelnew + i
        NewNode = MyNode(ID,labelnew,year)
        if ID in NodeIDList:
            pass
        else:
            NodeList.append(NewNode)
            id2node[ID] = NewNode
            NodeIDList[ID] = len(NodeList)-1

    for ID in NodeIDList.keys():
        if (ID != NodeList[NodeIDList[ID]].ReturnID()):
            print ('Error!')

    EdgeCount = 0
    for edge in edges:
        EdgeCount = EdgeCount + 1
        Source = edge['source']
        Target = edge['target']
        if (Source in NodeIDList) and (Target in NodeIDList):
            # 将引用和被引写入节点对象
            NodeList[NodeIDList[Source]].AppendOriginCite(NodeList[NodeIDList[Target]])
            NodeList[NodeIDList[Target]].AppendOriginBeCited(NodeList[NodeIDList[Source]])

    CiteCount,BeCitedCount = 0,0
    for ID in NodeIDList.keys():
        # 总引用量和总被引量
        CiteCount = CiteCount + NodeList[NodeIDList[ID]].ReturnOriginCiteTimes()
        BeCitedCount = BeCitedCount + NodeList[NodeIDList[ID]].ReturnOriginBeCitedTimes()

    if ((len(NodeList) != NodeCount) or (len(NodeIDList) != NodeCount)):
        print ('Error!')
    if ((CiteCount != EdgeCount) or (BeCitedCount != EdgeCount)):
        print ('Error!')

    node_detail = skeleton_tree

    for node in id2node:
        for nd in node_detail[str(node)]['cite']:
            id2node[node].AppendCite(id2node[int(nd)])
        for nd in node_detail[str(node)]['becited']:
            id2node[node].AppendBeCited(id2node[int(nd)])

    id2v_a, id2g_a = gen_subtree_parm(id, id2node, deep2node)
#     print(len(id2v_a))
#     print(len(id2v_a[id]))
#     print(len(id2g_a[id]))
    NodeTreeList = {}
    MyQueue = queue.Queue()
    MyQueue.put(id2node[int(id)])

    cnt = 0
    while (not(MyQueue.empty())):
        NodeNow = MyQueue.get()
        if (NodeNow.ReturnID() in NodeTreeList):
            NodeTreeList[NodeNow.ReturnID()] = NodeTreeList[NodeNow.ReturnID()] + 1
        else:
            NodeTreeList[NodeNow.ReturnID()] = 1
        for NodeLinked in NodeNow.ReturnBeCited():
            MyQueue.put(NodeLinked)

    EntropyIndex = {}
    EntropyCutIndex = {}

    for NodeNow in NodeList:
        if (int(NodeNow.ReturnID()) != int(id)):
            Answer1 = Entropy_1(NodeNow.ReturnCite()[0],NodeNow,len(NodeList)-1, id2v_a,id2g_a)
#             Answer2 = MutualEntropy(NodeNow.ReturnCite()[0],NodeNow,NodeNow,len(NodeList)-1)
#             if ((2.0*float(Answer1) - float(Answer2)) > 0.001):
#                 print(Answer1,Answer2)
            EntropyIndex[NodeNow.ReturnID()] = Answer1
            MutualEntropyAnswer = Answer1

            # 求孩子节点的树熵，相同节点的互熵相同
            for Node in NodeNow.ReturnBeCited():
#                 print('--------------1-------------------')
                MutualEntropyAnswer = MutualEntropyAnswer - MutualEntropy_1(NodeNow,Node,Node,len(NodeList)-1, id2v_a,id2g_a)
#                 print('--------------2-------------------')
#                 MutualEntropy_1(NodeNow,Node,Node,len(NodeList)-1, id2v_a,id2g_a)
            # 先求列表的组合数（为了加速）
            mutual_id_list = [node.ReturnID() for node in NodeNow.ReturnBeCited()]
            id_com_list = list(combinations(mutual_id_list, 2))
            # 求互熵
            for id_com in id_com_list:
#                 print('--------------3-------------------')
                MutualEntropyAnswer = MutualEntropyAnswer + MutualEntropy_1(NodeNow,id2node[id_com[0]],id2node[id_com[1]],len(NodeList)-1, id2v_a,id2g_a)
#                 print('--------------4-------------------')
#                 MutualEntropy_1(NodeNow,id2node[id_com[0]],id2node[id_com[1]],len(NodeList)-1, id2v_a,id2g_a)
            if (MutualEntropyAnswer < 0):
                MutualEntropyAnswer = 0
            EntropyCutIndex[NodeNow.ReturnID()] = MutualEntropyAnswer

    root_tree_entropy = 0
    MutualEntropyAnswer = 0
    # 求孩子节点的树熵
    for Node in id2node[int(id)].ReturnBeCited():
        MutualEntropyAnswer = MutualEntropyAnswer - MutualEntropy_1(id2node[int(id)],Node,Node,len(NodeList)-1,id2v_a,id2g_a)
    # 先求列表的组合数（为了加速）
    mutual_id_list = [node.ReturnID() for node in id2node[int(id)].ReturnBeCited()]
    id_com_list = list(combinations(mutual_id_list, 2))

    mt = 0
    # 求互熵
    for id_com in id_com_list:
        m = MutualEntropy_1(id2node[int(id)],id2node[id_com[0]],id2node[id_com[1]],len(NodeList)-1, id2v_a,id2g_a)
        MutualEntropyAnswer = MutualEntropyAnswer + m
        mt += m

    if (MutualEntropyAnswer < 0):
        print('error')
        MutualEntropyAnswer = 1
    
    EntropyCutIndex[int(id)] = MutualEntropyAnswer # 根节点的树熵无法计算，但树熵很小，故使用树熵计算公式后半部分进行近似
    EntropyIndex[int(id)] = root_tree_entropy # 根节点的树熵，使用其孩子节点的树熵之和近似

    return EntropyIndex, EntropyCutIndex # EntropyIndex: 树熵， EntropyCutIndex： 点熵