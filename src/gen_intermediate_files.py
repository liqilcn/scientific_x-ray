# ### 逐年生成相关科学主题的所需文件，逐年分割gml文件，脉络树文件，点熵树熵文件，树深文件
import networkx as nx
import time
import json
import random
import os
from readgml import readgml
from tqdm import tqdm_notebook as tqdm
from multiprocessing.pool import Pool

from gen_source_gml_by_year import gen_year_by_year_source_gml
from gen_reduction import gen_reduction
from gen_skeleton_tree import gen_skeleton_tree
from gen_tree_node_deep import gen_tree_node_deep
from gen_node_and_tree_entropy import gen_entropy
from gen_idea_tree_attributed_and_detail_file import gen_visible_depth_marked_skeleton_tree_gml_and_high_KE_node_detail
from gen_KE_and_VD_evolution_pics import top_knowledge_entropy_evolution, visible_depth_evoluation
from get_delta_D_for_specific_topic import delta_d_evolution


def gen_intermediate_files(pid):
    # 逐年生成脉络树，树深，各个节点的点熵树熵等
    gen_year_by_year_source_gml(pid)
    files_list = os.listdir('../temp_files/source_gml_by_year/'+str(pid))
    years_list = sorted([int(file.split('.')[0]) for file in files_list])
    if not os.path.exists('../temp_files/skeleton_tree_by_year/'+str(pid)):
        os.makedirs('../temp_files/skeleton_tree_by_year/'+str(pid))
    if not os.path.exists('../temp_files/node_entropy_by_year/'+str(pid)):
        os.makedirs('../temp_files/node_entropy_by_year/'+str(pid))
    if not os.path.exists('../temp_files/subtree_entropy_by_year/'+str(pid)):
        os.makedirs('../temp_files/subtree_entropy_by_year/'+str(pid))
    if not os.path.exists('../temp_files/tree_deep_by_year/'+str(pid)):
        os.makedirs('../temp_files/tree_deep_by_year/'+str(pid))
    if not os.path.exists('../temp_files/attributed_idea_tree_by_year/'+str(pid)):
        os.makedirs('../temp_files/attributed_idea_tree_by_year/'+str(pid))
    if not os.path.exists('../output/final_topic_portrait/'+str(pid)):
        os.makedirs('../output/final_topic_portrait/'+str(pid))
    for year in years_list:
        INPUT_FILE_PATH = '../temp_files/source_gml_by_year/'+str(pid)+'/'+str(year)+'.gml'
        pid2reduction = gen_reduction(pid, INPUT_FILE_PATH)
        skeleton_tree = gen_skeleton_tree(pid, pid2reduction, INPUT_FILE_PATH)
        deep2node = gen_tree_node_deep(pid, skeleton_tree)
        EntropyIndex, EntropyCutIndex = gen_entropy(pid, skeleton_tree, deep2node, INPUT_FILE_PATH)  # EntropyIndex: 树熵，EntropyCutIndex：点熵
        json.dump(skeleton_tree, open('../temp_files/skeleton_tree_by_year/'+str(pid)+'/'+str(year), 'w'))
        json.dump(deep2node, open('../temp_files/tree_deep_by_year/'+str(pid)+'/'+str(year), 'w'))
        json.dump(EntropyIndex, open('../temp_files/subtree_entropy_by_year/'+str(pid)+'/'+str(year), 'w'))
        json.dump(EntropyCutIndex, open('../temp_files/node_entropy_by_year/'+str(pid)+'/'+str(year), 'w'))
        gen_visible_depth_marked_skeleton_tree_gml_and_high_KE_node_detail(pid, year)
    visible_depth_evoluation(pid)
    delta_d_evolution(pid)
    print(f"Topic {pid} finish!")

if __name__=="__main__":
    pids = ['107234871', '151483314', '369508772']
    
    process_num = len(pids) if len(pids) <= 50 else 50

    with Pool(process_num) as pool:
        pool.map(gen_intermediate_files, pids)