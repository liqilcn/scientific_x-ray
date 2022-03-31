#!/usr/bin/env python
# coding: utf-8

# ### 给定一个topic的seminal paper的pid，基于节点的delta D得到主题的delta D

# In[15]:


import os
import json
import numpy as np
import datetime
from tqdm import tqdm


# In[16]:


THRESHOLD = 10


# In[75]:


def get_delta_D_for_specific_topic(pid):
    # 根据所有高知识熵节点delta D计算主题的delta D
    
    # 获取主题当前年份的可视深度
    year_now = datetime.datetime.now().year
    year_now = 2021
    pid2node_entropy_now = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(year_now), 'r'))
    tree_node_deep_now = json.load(open('../temp_files/tree_deep_by_year/'+str(pid)+'/{}'.format(year_now), 'r'))
    visible_depths = [] # 将包含点熵大于10的深度值加入，然后取最大值得最大可视深度
    for deep in tree_node_deep_now:
        for p_id in tree_node_deep_now[deep]:
            if float(pid2node_entropy_now[str(p_id)]) >= THRESHOLD:
                visible_depths.append(int(deep))
                break
    VD = 0 if len(visible_depths) == 0 else len(visible_depths)-1 # 如果visible_depths的长度为空，则代表主题的seminal paper的知识熵目前还未大于10，因此目前主题为0层
    if VD == 0:
        return (-99, ())
    # 获取可视深度与真实树深的映射
    if 0 in visible_depths: # 删除seminal paper所在的层
        visible_depths.remove(0)
    sorted_visible_depths = sorted(list(visible_depths))
    tree_deep2visible_depth = {}
    for i in range(len(sorted_visible_depths)):
        tree_deep2visible_depth[str(sorted_visible_depths[i])] = i+1
        
    # 获取pid与深度的映射关系
    pid2tree_deep = {}
    for dp in tree_node_deep_now:
        for p_id in tree_node_deep_now[dp]:
            pid2tree_deep[str(p_id)] = dp
    # 获取主题中所有知识熵大于等于10的节点
    candidates_pids = [] # 最终获得最深层的所有知识熵大于等于10的节点id
    for p_id in pid2node_entropy_now:
        if str(p_id) == str(pid):
            continue
        if float(pid2node_entropy_now[str(p_id)]) >= THRESHOLD:
            candidates_pids.append(p_id)
    
    # 找到所有候选节点的影响力开始显现的时间
    year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
    candidates_pid2start_year = {}
    for year in year_list:
        pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(year), 'r'))
        for p_id in candidates_pids:
            if p_id in pid2node_entropy and pid2node_entropy[p_id] >= THRESHOLD and p_id not in candidates_pid2start_year:
                candidates_pid2start_year[p_id] = int(year)
    
    # load最新拟合的时间衰减系数a
    a = float(json.load(open('a.json', 'r')))
    
    # 对所有候选节点计算delta D
    can_pid2detail = {}
    for p_id in candidates_pids:
        ke = pid2node_entropy_now[p_id]
        dt = 1 if int(year_now) - candidates_pid2start_year[p_id] == 0 else int(year_now) - candidates_pid2start_year[p_id]
        delta_D = np.log10(ke/(dt**2))
        delta_D_for_topic = delta_D - (VD - tree_deep2visible_depth[pid2tree_deep[p_id]])
        can_pid2detail[p_id] = (delta_D_for_topic, delta_D, VD - tree_deep2visible_depth[pid2tree_deep[p_id]], tree_deep2visible_depth[pid2tree_deep[p_id]], ke, dt, candidates_pid2start_year[p_id], int(year_now))
    sorted_can_pid2detail = sorted(can_pid2detail.items(), key = lambda item:item[1][0], reverse=True)
    return sorted_can_pid2detail[0][1][0], sorted_can_pid2detail

def get_delta_D_for_specific_topic_in_specific_year(pid, year_now):
    # 根据所有高知识熵节点delta D计算主题的delta D
    
    # 获取主题当前年份的可视深度
    pid2node_entropy_now = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(year_now), 'r'))
    tree_node_deep_now = json.load(open('../temp_files/tree_deep_by_year/'+str(pid)+'/{}'.format(year_now), 'r'))
    visible_depths = [] # 将包含点熵大于10的深度值加入，然后取最大值得最大可视深度
    for deep in tree_node_deep_now:
        for p_id in tree_node_deep_now[deep]:
            if float(pid2node_entropy_now[str(p_id)]) >= THRESHOLD:
                visible_depths.append(int(deep))
                break
    VD = 0 if len(visible_depths) == 0 else len(visible_depths)-1 # 如果visible_depths的长度为空，则代表主题的seminal paper的知识熵目前还未大于10，因此目前主题为0层
    if VD == 0:
        return (-99, ())
    # 获取可视深度与真实树深的映射
    if 0 in visible_depths: # 删除seminal paper所在的层
        visible_depths.remove(0)
    sorted_visible_depths = sorted(list(visible_depths))
    tree_deep2visible_depth = {}
    for i in range(len(sorted_visible_depths)):
        tree_deep2visible_depth[str(sorted_visible_depths[i])] = i+1
        
    # 获取pid与深度的映射关系
    pid2tree_deep = {}
    for dp in tree_node_deep_now:
        for p_id in tree_node_deep_now[dp]:
            pid2tree_deep[str(p_id)] = dp
    # 获取主题中所有知识熵大于等于10的节点
    candidates_pids = [] # 最终获得最深层的所有知识熵大于等于10的节点id
    for p_id in pid2node_entropy_now:
        if str(p_id) == str(pid):
            continue
        if float(pid2node_entropy_now[str(p_id)]) >= THRESHOLD:
            candidates_pids.append(p_id)
    
    # 找到所有候选节点的影响力开始显现的时间
    year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
    candidates_pid2start_year = {}
    for year in year_list:
        pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(year), 'r'))
        for p_id in candidates_pids:
            if p_id in pid2node_entropy and pid2node_entropy[p_id] >= THRESHOLD and p_id not in candidates_pid2start_year:
                candidates_pid2start_year[p_id] = int(year)
    
    # load最新拟合的时间衰减系数a
    a = float(json.load(open('a.json', 'r')))
    
    # 对所有候选节点计算delta D
    can_pid2detail = {}
    for p_id in candidates_pids:
        ke = pid2node_entropy_now[p_id]
        dt = 1 if int(year_now) - candidates_pid2start_year[p_id] == 0 else int(year_now) - candidates_pid2start_year[p_id]
        delta_D = np.log10(ke/(dt**2))
        delta_D_for_topic = delta_D - (VD - tree_deep2visible_depth[pid2tree_deep[p_id]])
        can_pid2detail[p_id] = (delta_D_for_topic, delta_D, VD - tree_deep2visible_depth[pid2tree_deep[p_id]], tree_deep2visible_depth[pid2tree_deep[p_id]], ke, dt, candidates_pid2start_year[p_id], int(year_now))
    sorted_can_pid2detail = sorted(can_pid2detail.items(), key = lambda item:item[1][0], reverse=True)
    return sorted_can_pid2detail[0][1][0], sorted_can_pid2detail

def delta_d_evolution(pid):
    year2delta_d = {}
    year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
    for year in year_list:
        topic_delta_D, detail = get_delta_D_for_specific_topic_in_specific_year(pid, year)
        year2delta_d[year] = topic_delta_D
    if not os.path.exists(f'../temp_files/year2delta_d'):
        os.makedirs(f'../temp_files/year2delta_d')
    json.dump(year2delta_d, open(f'../temp_files/year2delta_d/{pid}.json', 'w'))

if __name__ == "__main__":
    delta_d_evolution('5375658')
    # print(get_delta_D_for_specific_topic('212807447'))

