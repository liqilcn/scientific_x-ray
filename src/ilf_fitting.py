import os
import json
import datetime
import numpy as np
from tqdm import tqdm
from get_high_node_entropy_node_and_subtree_nodes import get_high_node_entropy_and_subtree_nodes, get_high_node_entropy_and_subtree_nodes_by_year

THRESHOLD = 10

def filter_data(all_pids):
    # 去除所有深度演进波动的主题，以避免影响结果
    # 如果统计可视深度总和，会有少数主题由于知识熵先增后减导致VDS先增后减的情况发生，去掉知识熵存在波动的主题
    selected_pids = []  # 深度演进曲线不存在波动的主题
    for pid in tqdm(all_pids):
        abandon_flag = 0
        year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
        year2max_visible_depth = {}
        year2vd_seq = {}
        for year in year_list:
            pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(year), 'r'))
            tree_node_deep = json.load(open('../temp_files/tree_deep_by_year/'+str(pid)+'/{}'.format(year), 'r'))
            visible_depths = [] # 将包含点熵大于10的深度值加入，然后取最大值得最大可视深度
            for deep in tree_node_deep:
                for p_id in tree_node_deep[deep]:
                    if float(pid2node_entropy[str(p_id)]) >= THRESHOLD:
                        visible_depths.append(int(deep))
                        break
            year2vd_seq[year] = visible_depths
            max_visible_depth = 0 if len(visible_depths) == 0 else len(visible_depths)-1 # 如果visible_depths的长度为空，则代表主题的seminal paper的知识熵目前还未大于10，因此目前主题为0层
            year2max_visible_depth[str(year)] = max_visible_depth
        sorted_year2max_visible_depth = sorted(year2max_visible_depth.items(), key = lambda item:item[0])
        # 包含重新统计树深的过程
        for i in range(len(sorted_year2max_visible_depth)-1):
            if sorted_year2max_visible_depth[i][1] > sorted_year2max_visible_depth[i+1][1]:
                abandon_flag = 1
                break
        sorted_year2vd_seq = sorted(year2vd_seq.items(), key = lambda item:int(item[0]))
        for i in range(len(year2vd_seq)-1):
            if not set(sorted_year2vd_seq[i][1]).issubset(sorted_year2vd_seq[i+1][1]):
                abandon_flag = 1
                break
        if not abandon_flag:
            selected_pids.append(pid)
    return selected_pids

def get_high_node_entropy_nodes_and_subtree_visible_depth(pid):
    # 获取子树可视深度的方法
    # 先找到最近一年的高知识熵节点及其引领的最大子树
    year_now = 2021
    tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/{year_now}', 'r'))
    pid2depth = {}
    for dp in tree_node_deep:
        for p_id in tree_node_deep[dp]:
            pid2depth[str(p_id)] = dp
    pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/{year_now}', 'r'))
    selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes(pid) # 获取最近一年所有知识熵大于等于10的节点及其对应的子树节点，# 在此步已经做过对子树中超越节点的处理，子树递归时不再向下深入，只保留最浅层的节点
    #============================================================================#
    #筛选最大的子树，这里面有些子树是其他子树的子树，判断条件：如果引领节点是某一子树的孩子节点，且该节点的知识熵小于等于父子树的引领节点，则判定
    #为非最大子树
    max_subtree_lead_nodes = []
    for p_id in selected_pid2subtree_nodes:
        NOT_MAX_TREE_FLAG = 0
        for pp_id in selected_pid2subtree_nodes:
            if pp_id == p_id:
                continue
            else:
                if p_id in selected_pid2subtree_nodes[pp_id]:
                    NOT_MAX_TREE_FLAG = 1
                    break
        if not NOT_MAX_TREE_FLAG:
            max_subtree_lead_nodes.append(p_id)
    #后面如果有需要可以改为所有高知识熵节点
    #============================================================================#
    year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
    data_detail_1 = {}
    for year in year_list:
        tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/{year}', 'r'))
        pid2depth = {}
        for dp in tree_node_deep:
            for p_id in tree_node_deep[dp]:
                pid2depth[str(p_id)] = dp
        pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/{year}', 'r'))
        selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes_by_year(pid, year)
        selected_pid2subtree_depth = {}
        for p_id in max_subtree_lead_nodes:
            if p_id in selected_pid2subtree_nodes:
                selected_child_id = []
                for child_id in selected_pid2subtree_nodes[p_id]:
                    if pid2node_entropy[child_id] >= THRESHOLD:
                        selected_child_id.append(child_id)
                selected_child_id_depth = []
                leading_node_depth = int(pid2depth[p_id])
                for s_id in selected_child_id:
                    selected_child_id_depth.append(int(pid2depth[s_id]) - leading_node_depth)  # 减去引领文章的深度得到孩子节点在子树中的深度
                selected_pid2subtree_depth[p_id] = len(set(selected_child_id_depth)) if len(set(selected_child_id_depth)) > 0 else 0 # 上面统计主题的可视深度稍有不同，上面是从seminal paper开始，故需要减1，下面是同孩子节点开始，故不需要间
        data_detail_1[year] = {'VD':selected_pid2subtree_depth, 'KE': {pid:pid2node_entropy[pid] for pid in selected_pid2subtree_depth}}
    return data_detail_1

def gen_draw_fig_point(data_detail):
    pid2time = {}
    for yr in data_detail:
        if data_detail[yr]['VD'] == {}:
            continue
        else:
            for p_id in data_detail[yr]['VD']:
                if p_id not in pid2time:
                    pid2time[p_id] = []
                pid2time[p_id].append(int(yr))
    pid2start_time = {}
    pid2end_time = {}
    for p_id in pid2time:
        pid2start_time[p_id] = min(pid2time[p_id])
        pid2end_time[p_id] = max(pid2time[p_id])
    pid2fig_point = {}
    for p_id in pid2start_time:
        start_time = pid2start_time[p_id]  # t0
        end_time = pid2end_time[p_id]
        max_depth = data_detail[end_time]['VD'][p_id]
        point_list = []
        for t in range(start_time, end_time):
            if p_id not in data_detail[t+1]['VD']:
                continue
            delta_d = max_depth - data_detail[t+1]['VD'][p_id]
            delta_t = t+1-start_time
            ke = data_detail[t+1]['KE'][p_id]
            point_list.append((delta_t, ke, delta_d))
        pid2fig_point[p_id] = point_list
    
    return pid2fig_point

def fitting_idea_limit():
    # 最小二乘法得到时间衰减系数
    # 获取所有完成脉络树提取与知识熵计算的主题
    candidates_pids = os.listdir('../temp_files/node_entropy_by_year')
    all_pids = []
    year_now = 2021
    for cpid in candidates_pids:
        years = os.listdir(f'../temp_files/node_entropy_by_year/{cpid}')
        if str(year_now) in years:
            all_pids.append(cpid)
    # 去掉可视深度存在抖动的情况
    selected_pids = filter_data(all_pids)
    # 获取所有主题的子树及其深度演进数据，为后面拟合做准备
    pid2data_detail = {}
    for pid in tqdm(selected_pids):
        data_detail = get_high_node_entropy_nodes_and_subtree_visible_depth(pid)
        pid2data_detail[pid] = data_detail
    # 生成拟合用的数据点
    pid2fig_point = {} # 可能会存在不同树中的同一个节点的覆盖效应
    for p_id in tqdm(pid2data_detail):
        pid2fig_point.update(gen_draw_fig_point(pid2data_detail[p_id]))
    # 最小二乘法拟合公式得到a
    dt,ke,dd =[],[],[]
    for p_id in pid2fig_point:
        for point in pid2fig_point[p_id]:
            dt.append(point[0])
            ke.append(point[1])
            dd.append(point[2])
    a = sum(np.log10(np.array(ke))-np.array(dd))/sum(np.log10(np.array(dt)))
    json.dump(a, open('a.json', 'w'))
    print(f"==============================a:{a}==============================")


if __name__ == "__main__":
	fitting_idea_limit()

