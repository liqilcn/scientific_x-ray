#!/usr/bin/env python
# coding: utf-8

# In[23]:


import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import treelib as tl
import queue
import math
import csv
import os
import re
from graphviz import Digraph
import json
from multiprocessing.pool import Pool
from lxml import etree
from networkx.utils import is_string_like


# In[24]:


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

#*************************************************************************************************#
TREE_JSON_FILE_PATH = '../temp_files/simplied_skeleton_tree_by_year/'
SVG_TAMPLE_FILE_PATH = '../temp_files/dot_svg_by_year/'
NODE_ENTROPY_PATH = '../temp_files/node_entropy_by_year/'
GML_FILE_PATH = '../temp_files/dot_vis_idea_tree_gml/'
INNER_CITATION_PATH = '../temp_files/pid2topic_iner_citaiton/'
CITATION_GML_FILE_PATH = '../temp_files/citaiton_simplied_skeleton_tree_gml/'
THRESHOLD = 10
#*************************************************************************************************#

def generate_gml(G):
    # gml图生成器直接将networkx源代码进行修改
    # recursively make dicts into gml brackets
    def listify(d,indent,indentlevel):
        result='[ \n'
        for k,v in d.items():
            if type(v)==dict:
                v=listify(v,indent,indentlevel+1)
            result += (indentlevel+1)*indent +                 string_item(k,v,indentlevel*indent)+'\n'
        return result+indentlevel*indent+"]"

    def string_item(k,v,indent):
        # try to make a string of the data
        if type(v)==dict: 
            v=listify(v,indent,2)
        elif is_string_like(v):
            v='"%s"'%v
        elif type(v)==bool:
            v=int(v)
        return "%s %s"%(k,v)

    # check for attributes or assign empty dict
    if hasattr(G,'graph_attr'):
        graph_attr=G.graph_attr
    else:
        graph_attr={}
    if hasattr(G,'node_attr'):
        node_attr=G.node_attr
    else:
        node_attr={}

    indent=2*' '
    count=iter(range(len(G)))
    node_id={}

    yield "graph ["
    if G.is_directed():
        yield indent+"directed 1"
    # write graph attributes 
    for k,v in G.graph.items():
        if k == 'directed':
            continue
        yield indent+string_item(k,v,indent)
    # write nodes
    for n in G:
        yield indent+"node ["
        # get id or assign number
        #nid=G.node[n].get('id',next(count))
        #node_id[n]=nid
        nid = n
        node_id[n]=n
        # 上两行对原代码进行修改，以原始输入的id作为输出图文件的id
        yield 2*indent+"id %s"%nid
        label=G.node[n]['L']
        node_json = G.node[n]['JSON']
        if is_string_like(label):
            label='"%s"'%label
        yield 2*indent+'label %s'%label
        yield 2*indent+'json %s'%node_json
        if n in G:
          for k,v in G.node[n].items():
              if k=='id' or k == 'label' or k == 'L' or k == 'JSON': continue
              yield 2*indent+string_item(k,v,indent)
        yield indent+"]"
    # write edges
    for u,v,edgedata in G.edges(data=True):
        source_color = G.node[u]['graphics']['fill']
        target_color = G.node[v]['graphics']['fill']
        yield indent+"edge ["
        yield 2*indent+"source %s"%u
        yield 2*indent+"target %s"%v
        yield 2*indent+"value 25.0"
        # yield 2*indent+"color "+ get_edge_color_by_mixe_node_color(source_color, target_color)
        yield 2*indent+"color #000000"
        yield 2*indent+"path "+edge2path[str(u)+'|'+str(v)]
        yield indent+"]"
    yield "]"


# In[27]:


def get_edge_color_by_mixe_node_color(source_color, target_color):
    # 用于将节点颜色进行混合，进而得到边的颜色
    r = str(hex(int((int(source_color[1:3], 16) + int(target_color[1:3], 16)) / 2)))
    g = str(hex(int((int(source_color[3:5], 16) + int(target_color[3:5], 16)) / 2)))
    b = str(hex(int((int(source_color[5:7], 16) + int(target_color[5:7], 16)) / 2)))
    if len(r.split('x')[1]) == 1:
        r = '0' + r.split('x')[1]
    else:
        r = r.split('x')[1]
    if len(g.split('x')[1]) == 1:
        g = '0' + g.split('x')[1]
    else:
        g = g.split('x')[1]
    if len(b.split('x')[1]) == 1:
        b = '0' + b.split('x')[1]
    else:
        b = b.split('x')[1]
    return '#' + r + g + b


# In[28]:

def gen_node_size(id2entropy):
    # 将所有节点的大小严格限制在10-200之间
    max_entropy = 0
    max_entropy_id = ''
    for pid in id2entropy:
        if id2entropy[pid] > 1000:
            id2entropy[pid] = 1000 + math.log(id2entropy[pid] - 1000)*10
        if id2entropy[pid] > max_entropy:
            max_entropy = id2entropy[pid]
            max_entropy_id = str(pid)
    factor = 190/max_entropy
    id2size = {}
    for pid in id2entropy:
        if id2entropy[pid] < 10:
            id2size[pid] = 10
        else: 
            id2size[pid] = factor*id2entropy[pid] + 20
    return id2size

# In[36]:



def layout_tree2svg(pid, yr, pid2color_list):
    # 返回使用networkx储存得到树G，包含节点标签，边
    # 使用graphviz的dot布局算法，将脉络树的布局结果以svg文件的形式存储
    depth2color = {
        'root': '#ff0000',
        'invisible': '#959595', # 只要不存在高知识熵节点的层都是invisible，用于高亮高知识熵节点
        '1': '#ffe306',
        '2': '#ff723a',
        '3': '#f81463',
        '4': '#9d126f',
        '5': '#6c48aa',
        '6': '#0a0da7',
        '7': '#0000ff'
    }

    depth2color = {
        'root': '#ff0000',
        'invisible': '#FF9900', # 只要不存在高知识熵节点的层都是invisible，用于高亮高知识熵节点
        '1': '#6c00c9',
        '2': '#6c00c9',
        '3': '#6c00c9',
        '4': '#6c00c9',
        '5': '#6c00c9',
        '6': '#6c00c9',
        '7': '#6c00c9'
    }
    
    tree_node_deep = json.load(open('../temp_files/tree_deep_by_year/'+str(pid)+'/{}'.format(yr), 'r'))
    id2entropy = json.load(open(NODE_ENTROPY_PATH+str(pid)+'/'+str(yr), 'r'))

    visible_depths = set()
    
    all_high_KE_node = []
    high_KE_node2deep = {}
    high_KE_node2KE = {}
    for deep in tree_node_deep:
        for p_id in tree_node_deep[deep]:
            if float(id2entropy[str(p_id)]) >= THRESHOLD:
                visible_depths.add(deep)
                all_high_KE_node.append(p_id)
                high_KE_node2deep[p_id] = deep
                high_KE_node2KE[str(p_id)] = float(id2entropy[str(p_id)])
    if '0' in visible_depths: # 删除seminal paper所在的层
        visible_depths.remove('0')
    
    pid2color = {}
    for deep in tree_node_deep: # 设置不可视层的颜色
        if deep not in visible_depths:
            for p_id in tree_node_deep[deep]:
                pid2color[str(p_id)] = depth2color['invisible']
    pid2color[str(pid)] = depth2color['root']  # seminal paper上色
    
    sorted_visible_depths = sorted(list(visible_depths))
    tree_deep2visible_depth = {}
    for i in range(len(sorted_visible_depths)):
        tree_deep2visible_depth[sorted_visible_depths[i]] = str(i+1)
        for p_id in tree_node_deep[sorted_visible_depths[i]]:
            pid2color[str(p_id)] = depth2color[str(i+1)] 
    # 去除毛刺，仅保留最大可视层下两层
    all_selected_pids = []
    deeps = []
    node2depth = {}

    for deep in tree_node_deep:
        if int(deep) <= int(int(0 if len(sorted_visible_depths) == 0 else sorted_visible_depths[-1])+2):
            deeps.append(int(deep))
            all_selected_pids += [str(p_id) for p_id in tree_node_deep[deep]]
            for p_id in tree_node_deep[deep]:
                node2depth[str(p_id)] = deep
    max_deep = max(deeps)

    node_detail = json.load(open(TREE_JSON_FILE_PATH+str(pid)+'/'+str(yr)))
    all_id_list = [str(p_id) for p_id in node_detail]
    
    selected_pids = list(set(all_id_list).intersection(set(all_selected_pids)))
    selected_node2depth = {p_id:node2depth[str(p_id)] for p_id in selected_pids}
    id2node = {}
    NodeList = []
    G = nx.DiGraph()
    for node in selected_pids:
        ID = node
        G.add_node(str(ID),graphics = {'w':0,'h':0,'d':0,'fill':''}, L = '', JSON='')
        node = str(node)
        label = node_detail[node]['label']
        year = node_detail[node]['year']
        NewNode = MyNode(ID,label,year)
        id2node[node] = NewNode
    for node in selected_pids:
        for nd in node_detail[node]['cite']:
            if nd in selected_node2depth:
                id2node[node].AppendCite(id2node[str(nd)])
                G.add_edge(str(nd), str(node)) # 脉络树的箭头方向为被引文献指向引用文献，以表示启发功能，与引文网络的方向相反
        for nd in node_detail[node]['becited']:
            if nd in selected_node2depth:
                id2node[node].AppendBeCited(id2node[str(nd)])
        NodeList.append(id2node[node])
    
    
    id2size = gen_node_size(id2entropy)

    # 向G中写入节点颜色
    for node in G.node:
        G.node[str(node)]['graphics']['fill'] = pid2color[str(node)] if str(node) in pid2color else '#959595'
    G.node[str(pid)]['graphics']['fill'] = '#ed1e79' 
    # for p_id in pid2color_list:
    #     try:
    #         G.node[str(p_id)]['graphics']['fill'] = pid2color_list[p_id]
    #     except:
    #         continue

    # 自适应计算idea tree横向和纵向的间距
    deep2size = {}
    for p_id in selected_node2depth:
        depth = selected_node2depth[p_id]
        size = id2size[p_id]
        if depth not in deep2size:
            deep2size[depth] = 0
        deep2size[depth] += (0.8+size)
    
    max_wide = max([deep2size[dp] for dp in deep2size])

    ranksep = max_wide/(max_deep+1.5)

    # if not os.path.exists(SVG_TAMPLE_FILE_PATH+str(pid)):
    #     os.makedirs(SVG_TAMPLE_FILE_PATH+str(pid))
    # mailuo_tree = Digraph('unix', filename=SVG_TAMPLE_FILE_PATH+str(pid)+'/'+str(yr), format = 'svg')
    mailuo_tree = Digraph('unix', filename=SVG_TAMPLE_FILE_PATH+str(pid), format = 'svg')
    mailuo_tree.attr(size='6,6')
    mailuo_tree.attr(nodesep='5')
    mailuo_tree.attr(ranksep=str(ranksep))
    mailuo_tree.node_attr.update(color='lightblue2', style='filled')

    ii = 0
    iii = 0
    high_KE_pid2label = json.load(open(f"../temp_files/attributed_idea_tree_by_year/{pid}/high_KE_pid2label.json", 'r'))
    high_KE_pid2label = high_KE_pid2label["body"]

    for NodeNow in NodeList:
        G.node[NodeNow.ReturnID()]['L'] = chr(int(high_KE_pid2label[str(NodeNow.ReturnID())])+64) if str(NodeNow.ReturnID()) in high_KE_pid2label else ''
        mailuo_tree.node(str(NodeNow.ReturnID()),shape='circle', width = str(id2size[str(NodeNow.ReturnID())]), color=pid2color[str(NodeNow.ReturnID())], label='')
        for NodeLinked in NodeNow.ReturnCite():
            mailuo_tree.edge(str(NodeLinked.ReturnID()),str(NodeNow.ReturnID()))
            G.node[NodeLinked.ReturnID()]['L'] = chr(int(high_KE_pid2label[str(NodeLinked.ReturnID())])+64) if str(NodeLinked.ReturnID()) in high_KE_pid2label else ''
            mailuo_tree.node(str(NodeLinked.ReturnID()),shape='circle', width = str(id2size[str(NodeLinked.ReturnID())]), color=pid2color[str(NodeLinked.ReturnID())], label='')
    mailuo_tree.render()
    # G.node[str(pid)]['L'] = id2node[str(pid)].ReturnLabel()
    return G


# In[30]:


def transform_coordinate(id2node):
    # 返回将脉络树限制在x：0-800，y_max：500
    min_x = min(float(id2node[node][0]) for node in id2node)
    min_y = min(float(id2node[node][1]) for node in id2node)
    max_x = max(float(id2node[node][0]) for node in id2node)
    max_y = max(float(id2node[node][1]) for node in id2node)
    bbox = [min_x - 100, min_y - 100, max_x + 100, max_y + 100]
    scale_f = 800 / (bbox[2] - bbox[0])
    dx = -(bbox[2]+bbox[0]) / 2
    dy = 500 - bbox[1]
    return dx, dy, scale_f*10


# In[31]:


def rebuild_path(path, dx, dy, scale_f, id2node, target_id):
    # 将路径先做平移，然后再把所有节点缩小100倍
    # 当节点的坐标小于100时acemap前端显示可能会出现问题
    path_split = re.split('M|C', path)
    path_m_x = (float(path_split[1].split(',')[0]) + dx)*scale_f
    path_m_y = (float(path_split[1].split(',')[1]) + dy)*scale_f
    path_c = []
    path_c_split = path_split[2].split(' ')
    for p in path_c_split:
        point = ((float(p.split(',')[0]) + dx)*scale_f, (float(p.split(',')[1]) + dy)*scale_f)
        path_c.append(point)
    path_c.pop(-1)
    path_c.append(((float(id2node[target_id][0]) + dx)*scale_f, (float(id2node[target_id][1]) + dy)*scale_f))
    path_rebuild = 'M'+str(path_m_x)+','+str(path_m_y)+'C'
    for point in path_c:
        path_rebuild = path_rebuild+str(point[0])+','+str(point[1])+' '
    return str(path_rebuild[0:-1])


# In[32]:


def gen_entropy_tree_visual_gml(pid, year, pid2color_list):
    G = layout_tree2svg(pid, year, pid2color_list)
    with open(SVG_TAMPLE_FILE_PATH + str(pid) + '.svg', 'r') as fp:
        lines_list = fp.readlines()
    os.remove(SVG_TAMPLE_FILE_PATH + str(pid) + '.svg')
    os.remove(SVG_TAMPLE_FILE_PATH + str(pid))
    i = 0
    id2node = {}
    global edge2path
    edge2path = {}
    for line in lines_list:
        if 'class="node"' in line:
            ID = str(etree.fromstring(lines_list[i + 1]).text)
            x = float(etree.fromstring(lines_list[i + 2]).attrib.get('cx'))
            y = float(etree.fromstring(lines_list[i + 2]).attrib.get('cy'))
            r = float(etree.fromstring(lines_list[i + 2]).attrib.get('rx'))
            id2node[ID] = (x, y, r)
        if 'class="edge"' in line:
            edge = str(etree.fromstring(lines_list[i + 1]).text).split('->')[0] + '|' + str(etree.fromstring(lines_list[i + 1]).text).split('->')[1]
            if '/>' not in lines_list[i + 2]:
                print(lines_list[i + 2])
            path = str(etree.fromstring(lines_list[i + 2]).attrib.get('d'))
            edge2path[edge] = path
        i += 1
    dx, dy, scale_f = transform_coordinate(id2node)
#     print(dx, dy, scale_f)
    if len(id2node) != len(G.node):
        print('parse svg node error!')
    if len(edge2path) != len(G.edges):
        print('parse svg edge error!')
#     id2node, dx, dy = transform_coordinate2acemap(id2node)
    for edge in edge2path:
#         edge2path[edge] = rebuild_path(edge2path[edge], dx, dy)
        target_id = edge.split('|')[1]
        edge2path[edge] = rebuild_path(edge2path[edge], dx, dy, scale_f, id2node, target_id)
    # 向G中写入节点坐标
    for id in id2node:
#         G.node[str(id)]['graphics']['x'] = id2node[id][0]/100
#         G.node[str(id)]['graphics']['y'] = id2node[id][1]/100
#         G.node[str(id)]['graphics']['z'] = 0
#         G.node[str(id)]['graphics']['w'] = id2node[id][2]/120
#         G.node[str(id)]['graphics']['h'] = id2node[id][2]/120
#         G.node[str(id)]['graphics']['d'] = id2node[id][2]/120
        G.node[str(id)]['graphics']['x'] = (id2node[id][0] + dx)*scale_f # 对于ACEMAP前段显示来说，x的坐标小于100会导致问题
        G.node[str(id)]['graphics']['y'] = (id2node[id][1] + dy)*scale_f
#         print((id2node[id][0] + dx)*scale_f, (id2node[id][1] + dy)*scale_f)
        G.node[str(id)]['graphics']['z'] = 0
        G.node[str(id)]['graphics']['w'] = id2node[id][2]*scale_f
        G.node[str(id)]['graphics']['h'] = id2node[id][2]*scale_f
        G.node[str(id)]['graphics']['d'] = id2node[id][2]*scale_f
    
    if not os.path.exists(GML_FILE_PATH+str(pid)):
    	os.makedirs(GML_FILE_PATH+str(pid))
    with open(GML_FILE_PATH+str(pid)+'/'+str(year)+'.gml', 'w') as fp:
        for line in generate_gml(G):
            line+='\n'
            fp.write(line)

def layout_citation_tree2svg(pid, yr, pid2color_list):
    # 返回使用networkx储存得到树G，包含节点标签，边
    # 使用graphviz的dot布局算法，将脉络树的布局结果以svg文件的形式存储
    node_detail = json.load(open(TREE_JSON_FILE_PATH+str(pid)+'/'+str(yr)))
    id2node = {}
    NodeList = []
    G = nx.DiGraph()
    for node in node_detail:
        ID = node
        G.add_node(str(ID),graphics = {'w':0,'h':0,'d':0,'fill':''}, L = '', JSON='')
        node = str(node)
        label = node_detail[node]['label']
        year = node_detail[node]['year']
        NewNode = MyNode(ID,label,year)
        id2node[node] = NewNode
    for node in id2node:
        for nd in node_detail[node]['cite']:
            id2node[node].AppendCite(id2node[str(nd)])
            G.add_edge(str(nd), str(node)) # 脉络树的箭头方向为被引文献指向引用文献，以表示启发功能，与引文网络的方向相反
        for nd in node_detail[node]['becited']:
            id2node[node].AppendBeCited(id2node[str(nd)])
        NodeList.append(id2node[node])
    
    id2inner_citation = json.load(open(INNER_CITATION_PATH+str(pid), 'r'))
    id2size = gen_node_size(id2inner_citation)

    # 向G中写入节点颜色
    for node in G.node:
        G.node[str(node)]['graphics']['fill'] = '#2e5bff'
    G.node[str(pid)]['graphics']['fill'] = '#fc0706'
    for p_id in pid2color_list:
        try:
            G.node[str(p_id)]['graphics']['fill'] = pid2color_list[p_id]
        except:
            continue
    
    mailuo_tree = Digraph('unix', filename=SVG_TAMPLE_FILE_PATH+str(pid), format = 'svg')
    mailuo_tree.attr(size='6,6')
    mailuo_tree.node_attr.update(color='lightblue2', style='filled')

    ii = 0
    iii = 0
    for NodeNow in NodeList:
        G.node[NodeNow.ReturnID()]['L'] = ''
        mailuo_tree.node(str(NodeNow.ReturnID()),shape='circle', width = str(id2size[str(NodeNow.ReturnID())]))
        for NodeLinked in NodeNow.ReturnCite():
            mailuo_tree.edge(str(NodeLinked.ReturnID()),str(NodeNow.ReturnID()))
            G.node[NodeLinked.ReturnID()]['L'] = ''
            mailuo_tree.node(str(NodeLinked.ReturnID()),shape='circle', width = str(id2size[str(NodeLinked.ReturnID())]))
    mailuo_tree.render()
    G.node[str(pid)]['L'] = id2node[str(pid)].ReturnLabel()
    return G

def gen_citation_entropy_tree_visual_gml(pid, pid2color_list):
    
    year = 2019
    G = layout_citation_tree2svg(pid, year, pid2color_list)
    with open(SVG_TAMPLE_FILE_PATH + str(pid) + '.svg', 'r') as fp:
        lines_list = fp.readlines()
    os.remove(SVG_TAMPLE_FILE_PATH + str(pid) + '.svg')
    os.remove(SVG_TAMPLE_FILE_PATH + str(pid))
    i = 0
    id2node = {}
    global edge2path
    edge2path = {}
    for line in lines_list:
        if 'class="node"' in line:
            ID = str(etree.fromstring(lines_list[i + 1]).text)
            x = float(etree.fromstring(lines_list[i + 2]).attrib.get('cx'))
            y = float(etree.fromstring(lines_list[i + 2]).attrib.get('cy'))
            r = float(etree.fromstring(lines_list[i + 2]).attrib.get('rx'))
            id2node[ID] = (x, y, r)
        if 'class="edge"' in line:
            edge = str(etree.fromstring(lines_list[i + 1]).text).split('->')[0] + '|' + str(etree.fromstring(lines_list[i + 1]).text).split('->')[1]
            if '/>' not in lines_list[i + 2]:
                print(lines_list[i + 2])
            path = str(etree.fromstring(lines_list[i + 2]).attrib.get('d'))
            edge2path[edge] = path
        i += 1
    dx, dy, scale_f = transform_coordinate(id2node)
#     print(dx, dy, scale_f)
    if len(id2node) != len(G.node):
        print('parse svg node error!')
    if len(edge2path) != len(G.edges):
        print('parse svg edge error!')
#     id2node, dx, dy = transform_coordinate2acemap(id2node)
    for edge in edge2path:
#         edge2path[edge] = rebuild_path(edge2path[edge], dx, dy)
        target_id = edge.split('|')[1]
        edge2path[edge] = rebuild_path(edge2path[edge], dx, dy, scale_f, id2node, target_id)
    # 向G中写入节点坐标
    for id in id2node:
#         G.node[str(id)]['graphics']['x'] = id2node[id][0]/100
#         G.node[str(id)]['graphics']['y'] = id2node[id][1]/100
#         G.node[str(id)]['graphics']['z'] = 0
#         G.node[str(id)]['graphics']['w'] = id2node[id][2]/120
#         G.node[str(id)]['graphics']['h'] = id2node[id][2]/120
#         G.node[str(id)]['graphics']['d'] = id2node[id][2]/120
        G.node[str(id)]['graphics']['x'] = (id2node[id][0] + dx)*scale_f # 对于ACEMAP前段显示来说，x的坐标小于100会导致问题
        G.node[str(id)]['graphics']['y'] = (id2node[id][1] + dy)*scale_f
#         print((id2node[id][0] + dx)*scale_f, (id2node[id][1] + dy)*scale_f)
        G.node[str(id)]['graphics']['z'] = 0
        G.node[str(id)]['graphics']['w'] = id2node[id][2]*scale_f
        G.node[str(id)]['graphics']['h'] = id2node[id][2]*scale_f
        G.node[str(id)]['graphics']['d'] = id2node[id][2]*scale_f
    
    if not os.path.exists(CITATION_GML_FILE_PATH+str(pid)):
    	os.makedirs(CITATION_GML_FILE_PATH+str(pid))
    with open(CITATION_GML_FILE_PATH+str(pid)+'/'+str(year)+'.gml', 'w') as fp:
        for line in generate_gml(G):
            line+='\n'
            fp.write(line)

if __name__=="__main__":
    layout_tree2svg('194520463', 2021)