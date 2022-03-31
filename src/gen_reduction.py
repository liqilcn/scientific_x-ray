#=====================================================================================
#title  : gen_reduction.py
#author  : Li Qi
#e-mail  : liqilcn@sjtu.edu.cn or qili_xidian@163.com
#date  : 20200711
#=====================================================================================

import scipy.linalg as linalg
import networkx as nx
import numpy as np
import queue
import datetime
import math
import json
import csv
import os
from readgml import readgml
from tqdm import tqdm_notebook as tqdm
from multiprocessing.pool import Pool

class MyNode:
    def __init__(self,ID,year):
        self.ID = ID
        self.Year = year
        self.Cite = []
        self.BeCited = []

    def AppendCite(self,paper):
        self.Cite.append(paper)

    def AppendBeCited(self,paper):
        self.BeCited.append(paper)

    def ReturnID(self):
        return self.ID

    def ReturnYear(self):
        return self.Year

    def ReturnCite(self):
        return set(self.Cite)

    def ReturnBeCited(self):
        return set(self.BeCited)

    def ReturnCiteTimes(self):
        return len(set(self.Cite))

    def ReturnBeCitedTimes(self):
        return len(set(self.BeCited))

def GetLaplacianMatrix(Matrix):
    d = np.sum(Matrix,axis=1)
    D = np.diag(d)
    L = D - Matrix
    Dn = np.power(np.linalg.matrix_power(D,-1),0.5)
    LaplacianMatrix = np.dot(np.dot(Dn,L),Dn)
    return LaplacianMatrix

def getKSmallestEigVec(LaplacianMatrix,k):
    EigenValue,EigenVector = linalg.eig(LaplacianMatrix)
    Dimension = len(EigenValue)

    EigenValueDictionary = dict(zip(EigenValue,range(0,Dimension)))
    EigenK = np.sort(EigenValue)[0:k]
    Index = [EigenValueDictionary[k] for k in EigenK]
    return EigenValue[Index],EigenVector[:,Index]

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
#             print(node['date'])
#             print(top_paper_time_stamp)
    for node in nodes:
        id = node['id']
        date = node['date']
        node_time_stamp = int(time.mktime(time.strptime(date, '%Y-%m-%d')))
        id2time_stamp[id] = node_time_stamp
        # 将出版日期异常的点加入集合中
        if node_time_stamp > time_stamp_flag or node_time_stamp < top_paper_time_stamp:
#             print(id)
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
                # 异常发生原因是前面一步已经移除了该边
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
#     print(len(nodes))
#     print(source_nodes_len)
#     print(len(need_cut_edge) + cut_edge_num)
    
    return nodes, edges

def gen_reduction(paper_id, INPUT_FILE_PATH):

    NodeList = []
    NodeIDList = {}
    Node_ID = set()
    G = nx.DiGraph()
    nodes, edges = readgml.read_gml(INPUT_FILE_PATH)
    nodes, edges = clean_reference_data(nodes, edges, int(paper_id))
    NodeCount = 0
    yearflag = int(datetime.datetime.now().year)
    for node in nodes:
        ID = node['id']
        year = int(node['date'][0:4])
        if year <= yearflag:
            NodeCount = NodeCount + 1
            NewNode = MyNode(ID,year)
            if ID in NodeIDList:
                pass
            else:
                NodeList.append(NewNode)
                NodeIDList[ID] = len(NodeList)-1
                G.add_node(ID)
                Node_ID.add(ID)
    
    for ID in NodeIDList.keys():
        if (ID != NodeList[NodeIDList[ID]].ReturnID()):
            print ('Error1!')
            
    EdgeCount = 0
    for edge in edges:
        Source = edge['source']
        Target = edge['target']
        if (Source != Target) and (Source in NodeIDList) and (Target in NodeIDList):
            NodeList[NodeIDList[Source]].AppendCite(NodeList[NodeIDList[Target]])
            NodeList[NodeIDList[Target]].AppendBeCited(NodeList[NodeIDList[Source]])
            EdgeCount = EdgeCount + 1

    CiteCount,BeCitedCount = 0,0
    for ID in NodeIDList.keys():
        CiteCount = CiteCount + NodeList[NodeIDList[ID]].ReturnCiteTimes()
        BeCitedCount = BeCitedCount + NodeList[NodeIDList[ID]].ReturnBeCitedTimes()

    if ((len(NodeList) != NodeCount) or (len(NodeIDList) != NodeCount)):
        pass
    if ((CiteCount != EdgeCount) or (BeCitedCount != EdgeCount)):
        print ('Error3!')

    AdjacencyMatrix = np.zeros((len(NodeIDList),len(NodeIDList)))
    iii = 0
    for NodeNow in NodeList:
        i = NodeIDList[NodeNow.ReturnID()]
        if NodeNow.ReturnID() == int(paper_id):
            AdjacencyMatrix[i][i] = 1
        for NodeLinked in NodeNow.ReturnCite():
            iii += 1
            j = NodeIDList[NodeLinked.ReturnID()]
            AdjacencyMatrix[i][j] = 1
    
    if (sum(sum(AdjacencyMatrix)) != EdgeCount+1):
        print('存在与开山作的互引!')

    LaplacianMatrix = GetLaplacianMatrix(AdjacencyMatrix)
    EigenValue,EigenVector = getKSmallestEigVec(LaplacianMatrix,len(NodeIDList))

    MaxDistance = 0
    for NodeNow in NodeList:
        for NodeLinked in NodeNow.ReturnCite():
            distance = np.linalg.norm(EigenVector[NodeIDList[NodeNow.ReturnID()]] - EigenVector[NodeIDList[NodeLinked.ReturnID()]])
            G.add_edge(NodeNow.ReturnID(),NodeLinked.ReturnID(),weight = distance)
            if (distance > MaxDistance):
                MaxDistance = distance

    NodeBeCitedTimesList = []
    NodeBeCitedTimesIDList = []
    for i in NodeList:
        NodeBeCitedTimesList.append(i.ReturnBeCitedTimes())

    if (len(NodeBeCitedTimesList) != len(NodeIDList)):
        print ('Error5!')

    MaxIndex = NodeBeCitedTimesList.index(max(NodeBeCitedTimesList))
    while (NodeBeCitedTimesList[MaxIndex] != -1):
        if (NodeList[MaxIndex].ReturnBeCitedTimes() != NodeBeCitedTimesList[MaxIndex]):
            print ('Error6!')
        else:
            NodeBeCitedTimesIDList.append(NodeIDList[NodeList[MaxIndex].ReturnID()])
            NodeBeCitedTimesList[MaxIndex] = -1
            MaxIndex = NodeBeCitedTimesList.index(max(NodeBeCitedTimesList))

    if (sum(NodeBeCitedTimesList) != -1*len(NodeBeCitedTimesList)):
        print ('Error7!')

    NodeBeCitedTimesIDList.reverse()
    for i in NodeBeCitedTimesIDList:
        NodeBeCitedTimesList.append(NodeList[i])

    sumstep = 0
    sumpath = 0

    # 未使用最短路径，但求的是最大距离，理论上只要距离足够大就行
    # 对一个按照citation降序排列的节点列表进行遍历，第一个元素是开创性文章
    for i in NodeBeCitedTimesIDList:
        NodeNow = NodeList[i]
        for NodeLinked in NodeNow.ReturnCite():
            if (not(NodeNow in NodeLinked.ReturnBeCited())):
                print ('Error8!')
            else:
                MyQueueNow = queue.Queue()
                MyQueueNext = queue.Queue()
                ReferenceDictionary = {}
                for k in NodeLinked.ReturnCite():
                    MyQueueNext.put(k)
                Step = 0
                while (not(MyQueueNext.empty())):
                    Step = Step + 1
                    MyQueueNow = MyQueueNext
                    MyQueueNext = queue.Queue()
                    while (not(MyQueueNow.empty())):
                        NodeOperateNow = MyQueueNow.get()
                        if NodeOperateNow.ReturnID() in ReferenceDictionary:
                            pass
                        else:
                            ReferenceDictionary[NodeOperateNow.ReturnID()] = Step
                            sumstep = sumstep + Step
                            sumpath = sumpath + 1
                            for k in NodeOperateNow.ReturnCite():
                                if k.ReturnID() in ReferenceDictionary:
                                    pass
                                else:
                                    MyQueueNext.put(k)

    Distance1Index_init = {}
    Distance2Index_init = {}
    Distance3Index_init = {}
    for j in NodeList:
        Distance1Index_init[j.ReturnID()] = 0
        Distance2Index_init[j.ReturnID()] = 0
        # Distance3Index_init[j.ReturnID()] = MaxDistance * 1.0 * sumstep / sumpath
        Distance3Index_init[j.ReturnID()] = MaxDistance * 1.0 * sumstep / sumpath if sumpath != 0 else MaxDistance  # 这句尚存争议，原始代码为上面一句
    Distance1Index = Distance1Index_init.copy()
    for i in NodeBeCitedTimesIDList:
        NodeNow = NodeList[i]
        Distance2Index = Distance2Index_init.copy()
        for NodeLinked in NodeNow.ReturnCite():
            MyQueueNow = queue.Queue()
            MyQueueNext = queue.Queue()
            Distance3Index = Distance3Index_init.copy()
            Distance3Index_flag = {}
            for k in NodeLinked.ReturnCite():
                MyQueueNext.put(k)
            while (not(MyQueueNext.empty())):
                MyQueueNow = MyQueueNext
                MyQueueNext = queue.Queue()
                while (not(MyQueueNow.empty())):
                    NodeOperateNow = MyQueueNow.get()
                    if NodeOperateNow.ReturnID() in Distance3Index_flag:
                        pass
                    else:
                        length = nx.dijkstra_path_length(G, source=NodeLinked.ReturnID(), target=NodeOperateNow.ReturnID())
                        Distance3Index[NodeOperateNow.ReturnID()] = length
                        Distance2Index[NodeOperateNow.ReturnID()] = Distance2Index[NodeOperateNow.ReturnID()] + Distance3Index[NodeOperateNow.ReturnID()]
                        Distance3Index_flag[NodeOperateNow.ReturnID()] = 1
                        for k in NodeOperateNow.ReturnCite():
                            if k.ReturnID() in Distance3Index_flag:
                                pass
                            else:
                                MyQueueNext.put(k)

            Distance3Index_flag_key = set(Distance3Index_flag.keys())
            work_set = Node_ID.difference(Distance3Index_flag_key)
            for j in work_set:
                Distance2Index[j] = Distance2Index[j] + Distance3Index[j]

        for j in NodeList:
            Distance1Index[j.ReturnID()] = Distance1Index[j.ReturnID()] + Distance2Index[j.ReturnID()]
    
    SolutionList = []
    SolutionIDList = []
    SolutionIndexList = []
    for s in NodeBeCitedTimesIDList:
        SolutionIDList.append(NodeList[s].ReturnID())
        SolutionIndexList.append(Distance1Index[NodeList[s].ReturnID()])
        
    MaxIndex = max(SolutionIndexList)
    while (MaxIndex != -1):
        SolutionList.append(SolutionIDList[SolutionIndexList.index(MaxIndex)])
        SolutionIndexList[SolutionIndexList.index(MaxIndex)] = -1
        MaxIndex = max(SolutionIndexList)
    
    if (sum(SolutionIndexList) != -1*len(SolutionIndexList)):
        print ('Error--!')

    return Distance1Index