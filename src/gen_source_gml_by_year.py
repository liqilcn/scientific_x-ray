import MySQLdb
import MySQLdb.cursors
import networkx as nx
import time
import json
import random
import os
import datetime
from readgml import readgml
from tqdm import tqdm_notebook as tqdm
from multiprocessing.pool import Pool


# In[16]:


def clean_reference_data(nodes, edges, top_id):
    # 去除发表日期大于当前日期的论文及其引用关系,这种情况有可能出现，但对学术脉络发展来说，不会对后面的脉络产生太大影响
    # 去除两篇文章之间的互引
    # 去除网络中存在的有向环
    # 存在开山作发表前的文章
    # 开山作引用别的文章的边
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
    
    return nodes, edges


# In[13]:


def gen_year_by_year_source_gml(pid):
    
    allowed_min_nodes_num = 5  # 所允许的领域内最少paper数
    nodes, edges = readgml.read_gml(f"../input/source_gml/{pid}.gml")
    nodes, edges = clean_reference_data(nodes, edges, int(pid))
    pid2label = {}
    pid2date = {}
    for node in nodes:
        pid2label[int(node['id'])] = node['label']
        pid2date[int(node['id'])] = node['date']
    min_year = min([int(node['date'][0:4]) for node in nodes])
    max_year = int(datetime.datetime.now().year)
    year2nodes = {}
    year2edges = {}
    for i in range(max_year-min_year+1):
        year2nodes[min_year+i] = set()
        for node in nodes:
            if int(node['date'][0:4]) <= (min_year+i):
                year2nodes[min_year+i].add(node['id'])
    for year in year2nodes:
        if len(year2nodes[year]) < allowed_min_nodes_num: # 当前年份内paper数过少，不分析
            continue
        else:
            year2edges[year] = []
            for edge in edges:
                if edge['source'] in year2nodes[year] and edge['target'] in year2nodes[year]:
                    year2edges[year].append((edge['source'], edge['target']))
                    
    if not os.path.exists(f"../temp_files/source_gml_by_year/{pid}"):
        os.makedirs(f"../temp_files/source_gml_by_year/{pid}")
        
    for year in year2edges:
        nodes_list = year2nodes[year]
        edges_list = year2edges[year]
        graph_info = 'graph [\n  directed 1\n'
        with open(f"../temp_files/source_gml_by_year/{pid}/{year}.gml", "w+", encoding="utf-8") as f:
            f.write(graph_info)
            for node in nodes_list:
                node_info = '  node' + '\n' + '  [\n    id ' + str(node) + '\n' + '    label ' + str(pid2label[node]).replace('"', "").replace(":", "") + '\n'+'    date ' + str(pid2date[node]) + '\n  ]\n'
                f.write(node_info)
            for edge in edges_list:
                edge_info = '  edge' + '\n' + '  [\n    source ' + str(edge[0]) + '\n' + '    target ' + str(
                    edge[1]) + '\n  ]\n'
                f.write(edge_info)
            f.write("]")