import os
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import numpy as np
from tqdm import tqdm
from get_high_node_entropy_node_and_subtree_nodes import get_high_node_entropy_and_subtree_nodes, get_high_node_entropy_and_subtree_nodes_by_year


THRESHOLD = 10

def classify_topics(selected_pids):
    # 根据主题的极限深度，对主题进行分类
    max_visible_depth2pids = {}
    for pid in tqdm(selected_pids):
        year_list = sorted([int(file) for file in os.listdir('../temp_files/node_entropy_by_year/'+str(pid))])
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
            max_visible_depth = 0 if len(visible_depths) == 0 else len(visible_depths)-1 # 如果visible_depths的长度为空，则代表主题的seminal paper的知识熵目前还未大于10，因此目前主题为0层
            # 减1是因为加入了seminal paper
            year2max_visible_depth[str(year)] = max_visible_depth
        sorted_year2max_visible_depth = sorted(year2max_visible_depth.items(), key = lambda item:item[0])
        if sorted_year2max_visible_depth[-1][1] not in max_visible_depth2pids:
            max_visible_depth2pids[sorted_year2max_visible_depth[-1][1]] = []
        max_visible_depth2pids[sorted_year2max_visible_depth[-1][1]].append(pid)
    return max_visible_depth2pids

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
    tree_node_deep = json.load(open(f'/home/qli/repository/topic_x-ray/scientific-topic-limit/temp_files/tree_deep_by_year/{pid}/{year_now}', 'r'))
    pid2depth = {}
    for dp in tree_node_deep:
        for p_id in tree_node_deep[dp]:
            pid2depth[str(p_id)] = dp
    pid2node_entropy = json.load(open(f'/home/qli/repository/topic_x-ray/scientific-topic-limit/temp_files/node_entropy_by_year/{pid}/{year_now}', 'r'))
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
    year_list = sorted([int(file) for file in os.listdir('/home/qli/repository/topic_x-ray/scientific-topic-limit/temp_files/node_entropy_by_year/'+str(pid))])
    data_detail_1 = {}
    for year in year_list:
        tree_node_deep = json.load(open(f'/home/qli/repository/topic_x-ray/scientific-topic-limit/temp_files/tree_deep_by_year/{pid}/{year}', 'r'))
        pid2node_entropy = json.load(open(f'/home/qli/repository/topic_x-ray/scientific-topic-limit/temp_files/node_entropy_by_year/{pid}/{year}', 'r'))
        pid2depth = {}
        visible_depths = []
        for dp in tree_node_deep:
            for p_id in tree_node_deep[dp]:
                pid2depth[str(p_id)] = dp
                if float(pid2node_entropy[str(p_id)]) >= THRESHOLD:
                    visible_depths.append(int(dp))
        visible_depths = sorted(list(set(visible_depths)))
        dp2vd = {}
        for i in range(len(visible_depths)):
            dp2vd[str(visible_depths[i])] = i
        
        selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes_by_year(pid, year)
        selected_pid2subtree_depth = {} # 节点所引领子树的vd
        selected_pid2vd = {} # 节点所处idea tree的VL数
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
                selected_pid2vd[p_id] = dp2vd[pid2depth[p_id]]
        data_detail_1[year] = {'VD':selected_pid2vd, 'SUBVD':selected_pid2subtree_depth, 'KE': {pid:pid2node_entropy[pid] for pid in selected_pid2subtree_depth}}
    return data_detail_1

def main():
    # 统计整个树的有效深度
    all_pids = json.load(open('top_paper_list1000.json', 'r'))
    all_pids_set = set(all_pids)
    candidates_pids = os.listdir('../temp_files/node_entropy_by_year')
    all_finished_pids = []
    year_now = 2021
    for cpid in candidates_pids:
        if cpid not in all_pids_set:
            continue
        years = os.listdir(f'../temp_files/node_entropy_by_year/{cpid}')
        if str(year_now) in years:
            all_finished_pids.append(cpid)
    max_visible_depth2pids = classify_topics(all_finished_pids)

    topic_limit = []
    topic_num = []
    for vd in max_visible_depth2pids:
        topic_limit.append(vd)
        topic_num.append(len(max_visible_depth2pids[vd]))
    bar_label = []
    s = sum([int(n) for n in topic_num])
    for i in range(len(topic_num)):
        t = int(topic_num[i])/s*100
        f = float('%.2f' % t)
        bar_label.append(f"{f}%")
    plt.figure(figsize = (20, 10), dpi = 100)
    plt.bar(topic_limit, topic_num, width=0.5, color='#6d97e5')
    plt.tick_params(top=False,right=False,length=6,width=5,labelsize=40) # 控制上下边框的刻度，以及刻度标签的大小、
    text_y = [int(n)+0.05 for n in topic_num]
    for i in range(len(topic_limit)):
        plt.text(topic_limit[i], text_y[i], bar_label[i], ha='center', va= 'bottom', fontsize=30, fontweight='bold') # 给条形图的柱子添加标签
    plt.gca().spines['bottom'].set_linewidth(5) # 设置坐标轴的粗细其余三个（'left', 'top', 'right'）,颜色.spines['top'].set_color('red')
    plt.gca().spines['left'].set_linewidth(5)
    sns.despine()
    plt.tight_layout()
    plt.xlabel('Valid Depth', size = 40, weight='bold')
    plt.ylabel('Number of Publications', size = 40,  weight='bold')
    plt.savefig(f'./topic_limit&topic_num.jpg', bbox_inches='tight')
    plt.show()
    plt.close()

    #统计子树的有效深度
    selected_pids = filter_data(all_finished_pids)
    pid2data_detail = {}
    for pid in tqdm(selected_pids):
        data_detail = get_high_node_entropy_nodes_and_subtree_visible_depth(pid)
        pid2data_detail[pid] = data_detail
    depths = []
    for p_id in tqdm(pid2data_detail):
        for pp_id in pid2data_detail[p_id][2021]['SUBVD']:
            depths.append(pid2data_detail[p_id][2021]['SUBVD'][pp_id])
            
    dp2num = {}
    for dp in depths:
        if dp not in dp2num:
            dp2num[dp] = 0
        dp2num[dp] += 1
        
    subtree_VD = []
    subtree_num = []
    for vd in dp2num:
        subtree_VD.append(int(vd))
        subtree_num.append(int(dp2num[vd]))
    bar_label = []
    s = sum([int(n) for n in subtree_num])
    for i in range(len(subtree_num)):
        t = int(subtree_num[i])/s*100
        f = float('%.2f' % t)
        bar_label.append(f"{f}%")
    plt.figure(figsize = (40, 20), dpi = 100)
    plt.bar(subtree_VD, subtree_num, width=0.5, color='#6d97e5')
    plt.tick_params(top=False,right=False,length=12,width=10,labelsize=80) # 控制上下边框的刻度，以及刻度标签的大小、
    text_y = [int(n)+0.05 for n in subtree_num]
    for i in range(len(subtree_VD)):
        plt.text(subtree_VD[i], text_y[i], bar_label[i], ha='center', va= 'bottom', fontsize=70, fontweight='bold') # 给条形图的柱子添加标签
    plt.gca().spines['bottom'].set_linewidth(10) # 设置坐标轴的粗细其余三个（'left', 'top', 'right'）,颜色.spines['top'].set_color('red')
    plt.gca().spines['left'].set_linewidth(10)
    sns.despine()
    plt.tight_layout()
    plt.xlabel('Valid Depth', size = 80, weight='bold')
    plt.ylabel('Number of Subtrees', size = 80,  weight='bold')
    plt.savefig(f'./idea_limit&subtree_num.jpg', bbox_inches='tight')
    plt.show()
    plt.close()

    # 统计每个VD下的高KE节点的推动效应
    vd2subvds = {}
    for p_id in tqdm(pid2data_detail):
        for pp_id in pid2data_detail[p_id][2021]['VD']:
            if pid2data_detail[p_id][2021]['VD'][pp_id] not in vd2subvds:
                vd2subvds[pid2data_detail[p_id][2021]['VD'][pp_id]] = []
            vd2subvds[pid2data_detail[p_id][2021]['VD'][pp_id]].append(pid2data_detail[p_id][2021]['SUBVD'][pp_id])

    for vd in vd2subvds:
        print(f'{vd}: {np.mean(vd2subvds[vd])}')

if __name__ == "__main__":
    main()