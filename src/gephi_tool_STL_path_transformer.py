import os
import json
import shutil
import datetime
from multiprocessing.pool import Pool
from gml2jpg import gml2png
from tqdm import tqdm_notebook as tqdm


def copy_galaxy_map_gmls_for_gephi_tool(pid):
    # 为gephi-tool构造工作路径
    gml_files = os.listdir(f'../temp_files/inited_galaxy_map_gml_by_year/{pid}') 
    for gml in gml_files:
        source_path = f'../temp_files/inited_galaxy_map_gml_by_year/{pid}/{gml}'
        target_path = f'../temp_files/inited_galaxy_map_gml_by_year_for_gephi_tool/{pid}_{gml}'
        shutil.copyfile(source_path, target_path)

def copy_idea_tree_gmls_for_gephi_tool(pid):
    # 为gephi-tool构造工作路径
    gml_files = os.listdir(f'../temp_files/inited_idea_tree_gml_by_year/{pid}') 
    for gml in gml_files:
        source_path = f'../temp_files/inited_idea_tree_gml_by_year/{pid}/{gml}'
        target_path = f'../temp_files/inited_idea_tree_gml_by_year_for_gephi_tool/{pid}_{gml}'
        shutil.copyfile(source_path, target_path)   


def copy_galaxy_map_gmls_from_gephi_tool(pid):
    # 将从gephi-tool得到的gml再次按照pid分文件夹存储
    gml_files = os.listdir(f'../temp_files/visulized_galaxy_map_gml_by_year_from_gephi_tool')
    for gml in gml_files:
        if gml.startswith(str(pid)):
            p_id = gml.split('_')[0]
            gml_file_name = gml.split('_')[1]
            if not os.path.exists(f"../temp_files/visulized_galaxy_map_gml_by_year/{p_id}"):
                os.makedirs(f"../temp_files/visulized_galaxy_map_gml_by_year/{p_id}")
            source_path = f'../temp_files/visulized_galaxy_map_gml_by_year_from_gephi_too/{gml}'
            target_path = f'../temp_files/visulized_galaxy_map_gml_by_year/{p_id}/{gml_file_name}'
            shutil.copyfile(source_path, target_path)

def copy_idea_tree_gmls_from_gephi_tool(pid):
    # 将从gephi-tool得到的gml再次按照pid分文件夹存储
    gml_files = os.listdir(f'../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool')
    for gml in gml_files:
        if gml.startswith(str(pid)):
            p_id = gml.split('_')[0]
            gml_file_name = gml.split('_')[1]
            if not os.path.exists(f"../temp_files/visulized_idea_tree_gml_by_year/{p_id}"):
                os.makedirs(f"../temp_files/visulized_idea_tree_gml_by_year/{p_id}")
            source_path = f'../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool/{gml}'
            target_path = f'../temp_files/visulized_idea_tree_gml_by_year/{p_id}/{gml_file_name}'
            shutil.copyfile(source_path, target_path)

if __name__ == "__main__":
    pids = json.load(open('pids2process.json', 'r'))
    for pid in pids:
        copy_idea_tree_gmls_for_gephi_tool(pid)
