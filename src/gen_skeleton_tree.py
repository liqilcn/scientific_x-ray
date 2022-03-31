#=====================================================================================
#title  : gen_skeleton_tree.py
#author  : Li Qi
#e-mail  : liqilcn@sjtu.edu.cn or qili_xidian@163.com
#date  : 20200711
#=====================================================================================

import networkx as nx
import numpy as np
import treelib as tl
import queue
import math
import csv
import os
from graphviz import Digraph
from readgml import readgml
from tqdm import tqdm_notebook as tqdm
import json
import datetime
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


def gen_skeleton_tree(id, Distance1Index, INPUT_FILE_PATH):

    nodes, edges = readgml.read_gml(INPUT_FILE_PATH)
    nodes, edges = clean_reference_data(nodes, edges, int(id))

    NodeList = []
    NodeIDList = {}

    G=nx.DiGraph()

    NodeCount = 0
    for node in nodes:
        NodeCount = NodeCount + 1
        label = node.get('label', '')
        ID = node['id']
        year = node['date']
        labelnew = ''
        for i in label: # 去除异常编码
            if ((0 <= ord(i)) and (ord(i) <= 127)): # ord函数，输入一个字符输出一个ascii或者unicode编码
                labelnew = labelnew + i
        NewNode = MyNode(ID,labelnew,year)
        if ID in NodeIDList:
            pass
        else:
            NodeList.append(NewNode)
            NodeIDList[ID] = len(NodeList)-1
            G.add_node(ID,label = label)

    for ID in NodeIDList.keys():
        if (ID != NodeList[NodeIDList[ID]].ReturnID()):
            print ('Error!')

    EdgeCount = 0
    for edge in edges:
        EdgeCount = EdgeCount + 1
        Source = edge['source']
        Target = edge['target']
        G.add_edge(Source,Target)
        if (Source in NodeIDList) and (Target in NodeIDList):
            # 将引用和被引写入节点对象
            NodeList[NodeIDList[Source]].AppendCite(NodeList[NodeIDList[Target]])
            NodeList[NodeIDList[Target]].AppendBeCited(NodeList[NodeIDList[Source]])

    CiteCount,BeCitedCount = 0,0
    for ID in NodeIDList.keys():
        # 总引用量和总被引量
        CiteCount = CiteCount + NodeList[NodeIDList[ID]].ReturnCiteTimes()
        BeCitedCount = BeCitedCount + NodeList[NodeIDList[ID]].ReturnBeCitedTimes()


    if ((CiteCount != EdgeCount) or (BeCitedCount != EdgeCount)):
        print ('Error!')

    try:
        Data = nx.find_cycle(G,orientation='ignore') 
    except:
        Data = []

    i = 0
    while (Data):
        EdgeIndexList = []
        for EdgeNow in Data:
            EdgeIndexList.append(abs(float(Distance1Index[EdgeNow[0]])-float(Distance1Index[EdgeNow[1]])))
        EdgeIndexListCopy = EdgeIndexList[:]

        while (True):
            if (EdgeIndexListCopy.count(-1) == len(EdgeIndexListCopy)):
                CutEdgeIndex = EdgeIndexList.index(max(EdgeIndexList))
                Node1 = NodeList[NodeIDList[Data[CutEdgeIndex][0]]]
                Node2 = NodeList[NodeIDList[Data[CutEdgeIndex][1]]]
                for edge in Data:
                    print(edge)
                break

            CutEdgeIndex = EdgeIndexListCopy.index(max(EdgeIndexListCopy))
            EdgeIndexListCopy[CutEdgeIndex] = -1
            Node1 = NodeList[NodeIDList[Data[CutEdgeIndex][0]]]
            Node2 = NodeList[NodeIDList[Data[CutEdgeIndex][1]]]
            if (Data[CutEdgeIndex][0] != Node1.ReturnID()):
                print ('Error!1')
            if (Data[CutEdgeIndex][1] != Node2.ReturnID()):
                print ('Error!2')
            if ((Node2 in Node1.ReturnBeCited()) and (Node1 in Node2.ReturnCite())):
                if (Node2.ReturnCiteTimes() > 1):
                    break
            elif ((Node1 in Node2.ReturnBeCited()) and (Node2 in Node1.ReturnCite())):
                if (Node1.ReturnCiteTimes() > 1):
                    break
            else:
                print ('Error!3')

        Node1.RemoveCite(Node2)
        Node1.RemoveBeCited(Node2)
        Node2.RemoveCite(Node1)
        Node2.RemoveBeCited(Node1)

        G.remove_edge(Node1.ReturnID(),Node2.ReturnID())
        try:
            G.remove_edge(Node2.ReturnID(),Node1.ReturnID()) # 理想情况下两篇paper不存在互相引用的环，但实际数据中确实存在
            i += 1
        except:
            pass
        try:
            Data = nx.find_cycle(G,orientation='ignore') # 切断一个环，继续寻找
        except:
            break

    node_detail = {}
    for node in NodeList:
        if node.ReturnID() not in node_detail:
            node_detail[str(node.ReturnID())] = {}
        node_detail[str(node.ReturnID())]['label'] = node.ReturnLabel()
        node_detail[str(node.ReturnID())]['year'] = node.ReturnYear()[0:4]
        node_detail[str(node.ReturnID())]['cite'] = [node.ReturnID() for node in node.ReturnCite()]
        node_detail[str(node.ReturnID())]['becited'] = [node.ReturnID() for node in node.ReturnBeCited()]

    return node_detail