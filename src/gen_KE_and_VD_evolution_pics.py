# 生成高知识熵节点与可视深度演进曲线图
### 论文弄好之后修改原始代码库

import os
import re
import csv
import json
import math
import random
import queue
import datetime
import MySQLdb
import MySQLdb.cursors
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
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

from entropy_tree_layout2gml import gen_entropy_tree_visual_gml, gen_citation_entropy_tree_visual_gml # 传递参数较多，集成的模块从函数内部进行配置传参
from gen_tree_analysis_data import get_max_bias_subtree_entropy, get_max_bias_node_entropy
from simply_skeleton_tree import simply_skeleton_tree
from gml2jpg import gml2png # 传递的参数较少，集成模块时直接从函数调用时传参

THRESHOLD = 10

def get_top_entropy_pids2colorlist(pid):
    # 在当前年份的点熵中找到点熵排名前10的节点的id，返回pid与颜色对应的字典
    # 特别研究的论文所用的颜色列表
    color_list = [
            '#25753f',
            '#c14510',
            '#8a1752',
            '#619cb9',
            '#f8f014',
            '#9b56b1',
            '#e88d24'
        ]
    # node_entropy = json.load(open(f"../temp_files/node_entropy_by_year/{pid}/{datetime.datetime.now().year}", 'r'))
    node_entropy = json.load(open(f"../temp_files/node_entropy_by_year/{pid}/{2021}", 'r'))
    pid_entropy_tuple = sorted(node_entropy.items(), key = lambda item:item[1], reverse=True)
    pids_list = []
    pid2color_list = {}
    ii = 0
    for i in range(8):
        if pid_entropy_tuple[i][0] == str(pid):
            continue
        pids_list.append(pid_entropy_tuple[i][0])
        pid2color_list[str(pid_entropy_tuple[i][0])] = color_list[ii]
        ii += 1
    return pid2color_list


def top_knowledge_entropy_evolution(pid):
    # 可视化高知识熵论文知识熵与脉络树的演化特性，并绘制曲线图，并将曲线存储在相应文件夹下
    # 在2019年的点熵中找到点熵排名前10的节点的id，返回id列表
    # node_entropy = json.load(open(f"../temp_files/node_entropy_by_year/{pid}/{datetime.datetime.now().year}", 'r'))
    node_entropy = json.load(open(f"../temp_files/node_entropy_by_year/{pid}/{2021}", 'r'))
    pid_entropy_tuple = sorted(node_entropy.items(), key = lambda item:item[1], reverse=True)
    pids_list = []
    for i in range(3): # 只取前两名，不包含seminal paper
        if pid_entropy_tuple[i][0] == str(pid):
            continue
        pids_list.append(pid_entropy_tuple[i][0])
    # 获取pid引领的脉络树的top论文的点熵与时间的关系
    node_entropys = {}
    year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
    pid2color_list = get_top_entropy_pids2colorlist(pid) # 生辰论文id与颜色的对应关系
    
    for year in year_list:
        pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/'+str(year), 'r'))
        for p_id in pids_list:
            if p_id not in node_entropys:
                node_entropys[p_id] = []
            if p_id not in pid2node_entropy:
                continue
            else:
                node_entropys[p_id].append((year, pid2node_entropy[p_id]))
    
    plt.figure(figsize = (42, 20), dpi = 100) # 2000*800
    plt.axes(yscale = "log")  # 纵坐标为对数坐标
    x_label_set = set()
    pid2label = json.load(open(f"../temp_files/attributed_idea_tree_by_year/{pid}/high_KE_pid2label.json",'r'))
    legend_handles = []
    legend_labels = []
    for p_id in node_entropys:
        x = [int(tp[0]) for tp in node_entropys[p_id]]
        for yr in x:
            x_label_set.add(yr)
        y = [tp[1] for tp in node_entropys[p_id]]
        l, = plt.plot(x,y, 'o-', color = pid2color_list[str(p_id)], lw=20, ms=50)
        legend_handles.append(l)
        if str(p_id) == str(pid):
            legend_labels.append('Leading Paper')
        elif str(p_id) in pid2label['body']:
            legend_labels.append(f"Paper {chr(int(pid2label['body'][str(p_id)])+64)}")  # 将数字标号变为大写字母
        else:
            legend_labels.append('KE < 10')
    plt.legend(handles=legend_handles, labels=legend_labels, loc='lower right', prop={'size': 80})
    plt.xticks(sorted(list(x_label_set)), sorted(list(x_label_set)), rotation=45, ha='right')  # 解决横坐标显示不全的问题
    # plt.xlabel('Year', size = 80, weight='bold')
    plt.ylabel('Knowledge Entropy', size = 80, weight='bold')
    plt.tick_params(top=False,right=False,length=16,width=12,labelsize=80) # 控制上下边框的刻度
    plt.tick_params(top=False,right=False,which='minor',length=10,width=6)
    plt.gca().spines['bottom'].set_linewidth(10) # 设置坐标轴的粗细其余三个（'left', 'top', 'right'）,颜色.spines['top'].set_color('red')
    plt.gca().spines['left'].set_linewidth(10)
    
    sns.despine()
    plt.tight_layout()
#     plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) # 强制坐标轴显示整数
    if not os.path.exists(f'../temp_files/skeleton_evolution_related_jpg/{pid}'):
        os.makedirs(f'../temp_files/skeleton_evolution_related_jpg/{pid}')
    plt.savefig('../temp_files/skeleton_evolution_related_jpg/'+str(pid)+'/'+'knowledge_entropy_evolution_without_seminal_paper.jpg', bbox_inches='tight')
    plt.close()
#     plt.title('(a) NodeEntropy Evolution', size = 40)
    # 将开山作加入node_entropys中
    for year in year_list:
        pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/'+str(year), 'r'))
        if str(pid) not in node_entropys:
            node_entropys[str(pid)] = []
        node_entropys[str(pid)].append((year, pid2node_entropy[str(pid)]))
    # 添加color_list的颜色
    pid2color_list[str(pid)] = '#ff0000'
    # 绘制子图2
    plt.figure(figsize = (42, 20), dpi = 100) # 2000*800
    plt.axes(yscale = "log")  # 纵坐标为对数坐标
    x_label_set = set()
    legend_handles = []
    legend_labels = []
    for p_id in node_entropys:
        # print(pids_list)
        if str(p_id) == str(pids_list[1]):
            continue
        x = [int(tp[0]) for tp in node_entropys[p_id]]
        for yr in x:
            x_label_set.add(yr)
        y = [tp[1] for tp in node_entropys[p_id]]
        l, = plt.plot(x,y, 'o-', color = pid2color_list[str(p_id)], lw=20, ms=50)
        legend_handles.append(l)
        if str(p_id) == str(pid):
            legend_labels.append('Leading Paper')
        elif str(p_id) in pid2label['body']:
            legend_labels.append(f"Paper {chr(int(pid2label['body'][str(p_id)])+64)}")
        else:
            legend_labels.append('KE < 10')
    plt.legend(handles=legend_handles, labels=legend_labels, loc='lower right', prop={'size': 80})
    plt.xticks(sorted(list(x_label_set)), sorted(list(x_label_set)), rotation=45, ha='right')  # 解决横坐标显示不全的问题
    # plt.xlabel('Year', size = 80, weight='bold')
    plt.ylabel('Knowledge Entropy', size = 80, weight='bold')
    plt.tick_params(top=False,right=False,length=16,width=12,labelsize=80) # 控制上下边框的刻度
    plt.tick_params(top=False,right=False,which='minor',length=10,width=6)
    plt.gca().spines['bottom'].set_linewidth(10) # 设置坐标轴的粗细其余三个（'left', 'top', 'right'）,颜色.spines['top'].set_color('red')
    plt.gca().spines['left'].set_linewidth(10)
    sns.despine()
    plt.tight_layout()
#     plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) # 强制坐标轴显示整数
    if not os.path.exists(f'../temp_files/skeleton_evolution_related_jpg/{pid}'):
        os.makedirs(f'../temp_files/skeleton_evolution_related_jpg/{pid}')
    plt.savefig('../temp_files/skeleton_evolution_related_jpg/'+str(pid)+'/'+'knowledge_entropy_evolution_with_seminal.jpg', bbox_inches='tight')
    plt.close() # 直接关闭plt，此时jupyter不会输出


# 对每个领域生成逐年可视深度的演进图
def visible_depth_evoluation(pid):
    year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
    max_visible_depth_list = []
    year2max_visible_depth = {}
    for year in year_list:
        pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(year), 'r'))
        tree_node_deep = json.load(open('../temp_files/tree_deep_by_year/'+str(pid)+'/{}'.format(year), 'r'))
        visible_depths = [] # 将包含点熵大于10的深度值加入，然后取最大值得最大可视深度
        for deep in tree_node_deep:
            for p_id in tree_node_deep[deep]:
                if float(pid2node_entropy[str(p_id)]) >= THRESHOLD:
                    visible_depths.append(int(deep))
                    break
        max_visible_depth = 0 if len(visible_depths) == 0 else len(visible_depths)-1
        max_visible_depth_list.append(max_visible_depth)
        year2max_visible_depth[int(year)] = max_visible_depth

    if not os.path.exists(f'../temp_files/year2visible_depth'):
        os.makedirs(f'../temp_files/year2visible_depth')
    json.dump(year2max_visible_depth, open(f'../temp_files/year2visible_depth/{pid}.json', 'w'))
    
    plt.figure(figsize = (42, 20), dpi = 100)
    plt.xticks(sorted(list(year_list)), sorted(list(year_list)), rotation=45, ha='right')  # 解决横坐标显示不全的问题
    plt.plot(year_list, max_visible_depth_list, lw=20, marker='o', ms=50, color='#ef3e59')
    # plt.xlabel('Year', size = 80, weight='bold')
    plt.ylabel('Valid Depth', size = 80, weight='bold')
#     plt.title('(d) BiasTopicEntropy Evolution', size = 40)
    plt.tick_params(top=False,right=False,length=16,width=12,labelsize=80) # 控制上下边框的刻度，以及刻度标签的大小
    plt.gca().spines['bottom'].set_linewidth(10) # 设置坐标轴的粗细其余三个（'left', 'top', 'right'）,颜色.spines['top'].set_color('red')
    plt.gca().spines['left'].set_linewidth(10)
    sns.despine()
    # plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) # 强制坐标轴显示整数
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True)) # 强制坐标轴显示整数
    # plt.yticks([-0.045, -0.03, -0.015, 0, 0.015, 0.03, 0.045],[-3, -2,-1,0,1,2, 3]) # 绘制深度为0专用，其他要注释掉
    if not os.path.exists(f'../temp_files/skeleton_evolution_related_jpg/{pid}'):
        os.makedirs(f'../temp_files/skeleton_evolution_related_jpg/{pid}')
    plt.tight_layout()
    plt.savefig('../temp_files/skeleton_evolution_related_jpg/'+str(pid)+'/'+'max_visible_depth.jpg')
    plt.close() # 直接关闭plt，此时jupyter不会输出
    print(pid)

if __name__=="__main__":
    pids = json.load(open('pids2process.json', 'r'))
    pids = ['180782032', '12014159', '162137477', '166247013', '401130906', '372732296', '25839486', '142812978', '223164844', '1587314', '194520463', '24264266', '2633249', '351922417']
    pids = ['252470610']
    pids = ['267126213', '457139010', '12014159', '162137477', '180782032', '372732296', '223164844', '1587314', '194520463', '351922417', '364638540', '263480625']
    pids = ['144236702']
    pids = ["477088530", "216352736", "218923005", "461030152", "63436595", "245538108"]
    pids = [
            # '38572377', 
            # '252470610', 
            '166247013', 
            '445475439', 
            '166725067', 
            # '457139010'
            ]
    pids = [
             # '262101246',
             # '290257163',
             # '3950247',
             # '434239941',
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
             '239501141',
             # '404272823',
             # '464101270',
             # '223164844',
             # '142118272',
             # '194520463',
             # '351922417',
             # '1587314'
            ]
    # pids = json.load(open('all_pids_2021_12_6.json', 'r'))
    # visible_depth_evoluation('387202101')
    process_num = len(pids) if len(pids) <= 50 else 50

    with Pool(process_num) as pool:
        pool.map(top_knowledge_entropy_evolution, pids)
    with Pool(process_num) as pool:
        pool.map(visible_depth_evoluation, pids)


    # for pid in tqdm(pids):
    #     top_knowledge_entropy_evolution(pid)
    #     visible_depth_evoluation(pid)