import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image, ImageDraw, ImageFont
from readgml import readgml
from networkx.drawing.nx_agraph import graphviz_layout

import os
import re
import csv
import json
import math
import random
import queue
import MySQLdb
import MySQLdb.cursors
import matplotlib
matplotlib.use('Agg')
from multiprocessing.pool import Pool
import datetime
import matplotlib.pyplot as plt
from graphviz import Digraph
from tqdm import tqdm
from PIL import Image
from matplotlib import cm
import numpy as np
import seaborn as sns
import networkx as nx
import treelib as tl
import pandas as pd
from matplotlib.ticker import MaxNLocator
from networkx.utils import is_string_like

from entropy_tree_layout2gml import gen_entropy_tree_visual_gml, gen_citation_entropy_tree_visual_gml # 传递参数较多，集成的模块从函数内部进行配置传参
from gen_tree_analysis_data import get_max_bias_subtree_entropy, get_max_bias_node_entropy
from simply_skeleton_tree import simply_skeleton_tree, simply_skeleton_tree_2
from gml2jpg import gml2png # 传递的参数较少，集成模块时直接从函数调用时传参
from get_sub_field_entropy import get_sub_field_entropy

THRESHOLD = 10

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


def generate_gml(G):
    # gml图生成器直接将networkx源代码进行修改
    # recursively make dicts into gml brackets
    def listify(d,indent,indentlevel):
        result='[ \n'
        for k,v in d.items():
            if type(v)==dict:
                v=listify(v,indent,indentlevel+1)
            result += (indentlevel+1)*indent + string_item(k,v,indentlevel*indent)+'\n'
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
        yield 2*indent+"value 1.0"
        yield 2*indent+"color "+ get_edge_color_by_mixe_node_color(source_color, target_color)
        yield indent+"]"
    yield "]"


def gen_node_size(id2entropy):
    # 此函数对于节点尺寸的可视化效果不佳，未能凸显不同节点的知识熵差异，弃用
    id2size = {pid:5 for pid in id2entropy}
    for pid in id2entropy:
        if id2entropy[pid] >= THRESHOLD:
            id2size[pid] = ((math.log(float(id2entropy[pid])))** 2) + 10
    return id2size

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
        id2size[pid] = factor*id2entropy[pid] + 10
    return id2size

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

# 对每个领域生成逐年可视深度的演进图
def gen_visible_depth_marked_skeleton_tree_gml_and_high_KE_node_detail(seminal_pid, year):
    # 在简化的脉络树中标注出最大可视深度下的点熵超过10的节点，用深红色
    # 可视化思路：先筛选出所有不包含高知识熵节点的层，把这些节点上invisible这个颜色，然后将剩下的层按深度排序，分别上123456对应的颜色
    
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
    depth2color_half_trans = { #  同一颜色降低透明度，用于标识相应高知识熵节点使得某一层可视的所有节点
        '1': "#fff396",
        '2': '#ffb89c',
        '3': '#fb89b1',
        '4': '#ce88b7',
        '5': '#b5a3d4',
        '6': '#5355c1',
    }
    pid2simply_ratio = { # 用于对特定pid的脉络树进行微调，调节剪枝的比率
        '62270017': 0.3, #
    #     477114443,
        '142612150': 0.05,
        '214435441': 0.05,
        '255866650': 0.05, #
    #     274480977,
        '1842472': 0.05, #
        '356008829': 0.05,
        '71305135': 0.1, #
        '379075697': 0.05,
        '252195446': 0.07, # 
        '174864895': 0.1, #
        '175773368': 0.15, #
        '329258602': 0.05,
        '457139010': 0.3,
        '1587314': 0.35,
        '81075167': 0.14,
        '38572377': 0.00001,
        '252470610': 0.001,
        '166247013': 0.001,
        '445475439': 0.01,
        '166725067': 0.001,
        '457139010': 0.001
    }
    
    simply_ratio = pid2simply_ratio.get(seminal_pid, 0.2)
    
    pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(seminal_pid)+'/{}'.format(year), 'r'))

    tree_node_deep = json.load(open('../temp_files/tree_deep_by_year/'+str(seminal_pid)+'/{}'.format(year), 'r'))
    
    visible_depths = set()
    
    all_high_KE_node = []
    high_KE_node2deep = {}
    high_KE_node2KE = {}
    for deep in tree_node_deep:
        for p_id in tree_node_deep[deep]:
            if float(pid2node_entropy[str(p_id)]) >= THRESHOLD:
                visible_depths.add(deep)
                all_high_KE_node.append(p_id)
                high_KE_node2deep[p_id] = deep
                high_KE_node2KE[str(p_id)] = float(pid2node_entropy[str(p_id)])
    if '0' in visible_depths: # 删除seminal paper所在的层
        visible_depths.remove('0')
    
    pid2color = {}
    for deep in tree_node_deep: # 设置不可视层的颜色
        if deep not in visible_depths:
            for p_id in tree_node_deep[deep]:
                pid2color[str(p_id)] = depth2color['invisible']
    pid2color[str(seminal_pid)] = depth2color['root']  # seminal paper上色
    
    sorted_visible_depths = sorted(list(visible_depths))
    tree_deep2visible_depth = {}
    for i in range(len(sorted_visible_depths)):
        tree_deep2visible_depth[sorted_visible_depths[i]] = str(i+1)
        for p_id in tree_node_deep[sorted_visible_depths[i]]:
            pid2color[str(p_id)] = depth2color[str(i+1)]       
#     for p_id in all_high_KE_node:
#         if str(p_id) == str(seminal_pid):
#             continue
#         pid2color[str(p_id)] = depth2color[str(tree_deep2visible_depth[str(high_KE_node2deep[p_id])])]
    
    # simply_skeleton_tree(seminal_pid, year, simply_ratio) # 通过第上一个函数写文件，下一个函数读文件进行传递数据也是可行的
    simply_skeleton_tree_2(seminal_pid, year)

    yr = year
    node_detail = json.load(open(f"../temp_files/simplied_skeleton_tree_by_year/{seminal_pid}/{year}", "r"))
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
    

    id2size = gen_node_size(pid2node_entropy)
    pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(seminal_pid)+'/{}'.format(yr), 'r'))
    
    for id in id2node:
        G.node[str(id)]['graphics']['w'] = id2size[id]
        G.node[str(id)]['graphics']['h'] = id2size[id]
        G.node[str(id)]['graphics']['d'] = id2size[id]
        G.node[str(id)]['graphics']['fill'] = pid2color[id]
    # 为高知识熵节点打标签
    if seminal_pid in high_KE_node2KE:
        ttt = high_KE_node2KE.pop(str(seminal_pid))
    # 读文件初始化已有标签
    db = MySQLdb.connect(
            host = '10.10.10.10',
            user = 'readonly',
            password = 'readonly',
            db = 'am_paper',
            port = 3306,
            charset = 'utf8mb4',
            cursorclass=MySQLdb.cursors.SSCursor
    )
    if not os.path.exists(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/high_KE_pid2label.json"):
        high_KE_node2year = {}
        for pid in high_KE_node2KE:
            sql = f"SELECT year FROM `am_paper`.`am_paper` WHERE paper_id = {pid}"
            cursor = db.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            high_KE_node2year[pid] = int(result[0])
        sorted_high_KE_node2year = sorted(high_KE_node2year.items(), key = lambda item:item[1])
        high_KE_pid2label_body = {str(sorted_high_KE_node2year[i][0]):str(i+1) for i in range(len(sorted_high_KE_node2year))}
        high_KE_pid2label = {}
        high_KE_pid2label['body'] = high_KE_pid2label_body
        high_KE_pid2label['year'] = yr
        json.dump(high_KE_pid2label, open(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/high_KE_pid2label.json", 'w'))
    else:
        high_KE_pid2label = json.load(open(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/high_KE_pid2label.json", 'r'))
        if int(high_KE_pid2label['year']) > int(yr):
            high_KE_node2year = {}
            for pid in high_KE_node2KE:
                sql = f"SELECT year FROM `am_paper`.`am_paper` WHERE paper_id = {pid}"
                cursor = db.cursor()
                cursor.execute(sql)
                result = cursor.fetchone()
                high_KE_node2year[pid] = int(result[0])
            sorted_high_KE_node2year = sorted(high_KE_node2year.items(), key = lambda item:item[1])
            high_KE_pid2label_body = {str(sorted_high_KE_node2year[i][0]):str(i+1) for i in range(len(sorted_high_KE_node2year))}
            high_KE_pid2label['body'] = high_KE_pid2label_body
            high_KE_pid2label['year'] = yr
            json.dump(high_KE_pid2label, open(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/high_KE_pid2label.json", 'w'))
        else:
            high_KE_pid2label = json.load(open(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/high_KE_pid2label.json", 'r'))
            orig_len = len(high_KE_pid2label['body'])
            unlabeled_pids = []
            for pid in high_KE_node2KE:
                if str(pid) not in high_KE_pid2label['body']:
                    unlabeled_pids.append(str(pid))
            unlabeled_pid2year = {}
            for pid in unlabeled_pids:
                sql = f"SELECT year FROM `am_paper`.`am_paper` WHERE paper_id = {pid}"
                cursor = db.cursor()
                cursor.execute(sql)
                result = cursor.fetchone()
                unlabeled_pid2year[pid] = int(result[0])
            sorted_unlabeled_pid2year = sorted(unlabeled_pid2year.items(), key = lambda item:item[1])
            for i in range(len(sorted_unlabeled_pid2year)):
                high_KE_pid2label['body'][str(sorted_unlabeled_pid2year[i][0])] = str(orig_len + i + 1)
            high_KE_pid2label['year'] = yr
            json.dump(high_KE_pid2label, open(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/high_KE_pid2label.json", 'w'))

    for p_id in high_KE_pid2label['body']: # 会有极少数主题前期的高知识节点在后期知识熵降为极低而被剪枝算法去掉，导致G里面不包含这个节点，从而导致这里报错, if str(p_id) in G.node为新加
        if str(p_id) in G.node:
            G.node[str(p_id)]['L'] = chr(int(high_KE_pid2label['body'][p_id])+64)  # 将数字label转化为大写字母
    
    if not os.path.exists(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}"):
            os.makedirs(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}")
    
    with open(f"../temp_files/attributed_idea_tree_by_year/{seminal_pid}/{yr}.gml", 'w') as fp:
        for line in generate_gml(G):
            line+='\n'
            fp.write(line)
    
    # 生成主题内部的高知识熵节点的detail
    high_KE_pid2year = {}
    high_KE_pid2title = {}
    high_KE_pid2KE = {}
    for pid in high_KE_pid2label['body']:
        sql = f"SELECT year, title FROM `am_paper`.`am_paper` WHERE paper_id = {pid}"
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        high_KE_pid2year[pid] = int(result[0])
        high_KE_pid2title[pid] = result[1]
        high_KE_pid2KE[pid] = float(pid2node_entropy[pid])
    db.close()
    
    # print(pid2node_entropy)
    sorted_high_KE_pid2label = sorted(high_KE_pid2label['body'].items(), key=lambda item:int(item[1]))
    high_KE_node_detail = {'Label':[], 'Title':[], 'Knowledge Entropy':[], 'Published Year':[]}
    for pid, ke in sorted_high_KE_pid2label:
        high_KE_node_detail['Label'].append(chr(64+int(high_KE_pid2label['body'][pid]))) # 将数字label转化为大写字母
        high_KE_node_detail['Title'].append(high_KE_pid2title[pid])
        high_KE_node_detail['Knowledge Entropy'].append(high_KE_pid2KE[pid])
        high_KE_node_detail['Published Year'].append(str(high_KE_pid2year[pid]))
    df = pd.DataFrame(high_KE_node_detail)
    pd.set_option('display.max_colwidth',500)
    pd.set_option('display.width',500)
    high_KE_node_detail_latex = df.to_latex(index=False, header=True, float_format="%.4f", column_format='p{1cm}p{7.5cm}p{3cm}p{2cm}')
    if not os.path.exists(f"../output/final_topic_portrait/{seminal_pid}"):
        os.makedirs(f"../output/final_topic_portrait/{seminal_pid}")
    with open(f'../output/final_topic_portrait/{seminal_pid}/{yr}.txt', 'w') as fp:
        fp.write(high_KE_node_detail_latex)
    # 将表格转为图片
    col = ['Label', 'Title', 'Knowledge Entropy', 'Published Year']
    vals = []
    for i in range(len(high_KE_node_detail['Label'])):
        r = [high_KE_node_detail['Label'][i], high_KE_node_detail['Title'][i], float('%.4f' % high_KE_node_detail['Knowledge Entropy'][i]), high_KE_node_detail['Published Year'][i]]
        
        vals.append(r)

    plt.figure(figsize = (20, 20), dpi = 100)
    if len(vals) == 0:
        if not os.path.exists(f"../temp_files/high_KE_node_detail_png/{seminal_pid}"):
            os.makedirs(f"../temp_files/high_KE_node_detail_png/{seminal_pid}")
        plt.savefig(f"../temp_files/high_KE_node_detail_png/{seminal_pid}/{yr}.jpg")
        plt.close()
    else:
        tab = plt.table(cellText=vals, 
                        colLabels=col, 
                        loc='center', 
                        cellLoc='center',
                        rowLoc='center')
        tab.auto_set_font_size(False)
        tab.set_fontsize(10)
        tab.scale(1.3,1.3)
        plt.axis('off')
        if not os.path.exists(f"../temp_files/high_KE_node_detail_png/{seminal_pid}"):
            os.makedirs(f"../temp_files/high_KE_node_detail_png/{seminal_pid}")
        plt.savefig(f"../temp_files/high_KE_node_detail_png/{seminal_pid}/{yr}.jpg")
        plt.close()
if __name__=="__main__":
    pids = json.load(open('cccf_pids_1.json', 'r'))

    candidates_pids = os.listdir('../temp_files/node_entropy_by_year')
    all_pids = []
    year_now = datetime.datetime.now().year
    for cpid in candidates_pids:
        years = os.listdir(f'../temp_files/node_entropy_by_year/{cpid}')
        if str(year_now) in years:
            all_pids.append(cpid)

    pids = list(set(all_pids).intersection(set(pids)))
    pids = json.load(open('x_ray_geo_finished_pids.json', 'r'))
    pids = ['267126213', '457139010', '12014159', '162137477', '180782032', '372732296', '223164844', '1587314', '194520463', '351922417', '364638540', '263480625',
            '186736262', '3963681', '18869729', '144236702', '403862122', '404272823', '212067742', '239501141', '464101270'
     ]
    pids = ['403862122', '144236702']
    pids = ['18869729']
    pids = ['81075167']
    pids = [
            # '38572377', 
            # '252470610', 
            '166247013', 
            # '445475439', 
            # '166725067', 
            # '457139010'
            ]
    pids = ['372732296']
    pids = [
             # '262101246',
    #          '290257163',
    #          '3950247',
    #          '434239941',
             # '364638540',
             # '186736262',
             # '267126213',
             # '12014159',
             # '162137477',
             # '180782032',
             # '263480625',
             # '116579552',
             # '372732296',
             # '144236702',
             # '403862122',
             # '22340939',
             # '239501141',
             # '404272823',
             # '464101270',
             # '223164844',
             # '142118272',
             # '194520463',
             # '351922417',
             '438420345'
            ]
    for pid in tqdm(pids):
        files_list = os.listdir('../temp_files/source_gml_by_year/'+str(pid))
        years_list = sorted([int(file.split('.')[0]) for file in files_list])
        for year in years_list:
            print(year)
            gen_visible_depth_marked_skeleton_tree_gml_and_high_KE_node_detail(pid, year)

