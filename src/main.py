import os
import json
import shutil
import datetime
from gml2jpg import gml2png
from tqdm import tqdm
from multiprocessing.pool import Pool

from vis_idea_tree_by_dot import gen_dot_vis_idea_tree_png
from gen_KE_and_VD_evolution_pics import top_knowledge_entropy_evolution, visible_depth_evoluation
from init_year_by_year_gml_to_vis import init_year_by_year_gml
from gephi_tool_STL_path_transformer import copy_galaxy_map_gmls_for_gephi_tool, copy_idea_tree_gmls_for_gephi_tool
from gephi_tool_STL_path_transformer import copy_galaxy_map_gmls_from_gephi_tool, copy_idea_tree_gmls_from_gephi_tool
from pic_processor import tag_for_skeleton_tree, tag_for_dot_vis_skeleton_tree, marge_all_pics, topic_detail2png, tag_for_dot_vis_skeleton_tree2

def worker2KE_VD(pid):
	top_knowledge_entropy_evolution(pid)
	visible_depth_evoluation(pid)
	print(pid)

def worker2png(arg):
	source, target = arg[0], arg[1]
	gml2png(source, target, label_flag=True, straight_line=True)
	print(arg[1])

def worker2x_ray(pid):
	portrait_fold = 'geo_topic_portrait'
	pic_list = []
	sorted_all_years = sorted([int(file.split('.')[0]) for file in os.listdir(f'../temp_files/taged_idea_tree_evolution/{pid}')])
	for year in sorted_all_years:
		pic_list.append(f'../temp_files/taged_idea_tree_evolution/{pid}/{year}.png')
	pic_list.append(f'../temp_files/topic_detail_png/{pid}.png')
	# pic_list.append(f'../temp_files/high_KE_node_detail_png/{pid}/{datetime.datetime.now().year}.jpg')
	pic_list.append(f'../temp_files/skeleton_evolution_related_jpg/{pid}/knowledge_entropy_evolution_with_seminal.jpg')
	pic_list.append(f'../temp_files/skeleton_evolution_related_jpg/{pid}/knowledge_entropy_evolution_without_seminal_paper.jpg')
	pic_list.append(f'../temp_files/skeleton_evolution_related_jpg/{pid}/max_visible_depth.jpg')
	# 将主题按照最大可视深度分类
	year2visibledepth = json.load(open(f'../temp_files/year2visible_depth/{pid}.json'))
	max_visible_depth = max([int(year2visibledepth[year]) for year in year2visibledepth])
	if not os.path.exists(f"../output/{portrait_fold}/{max_visible_depth}/{pid}"):
		os.makedirs(f"../output/{portrait_fold}/{max_visible_depth}/{pid}")

	marge_all_pics(pic_list, column_num=5, interval_width=30, save_path=f'../output/{portrait_fold}/{max_visible_depth}/{pid}/topic x-ray(fa2 vis).jpg')
	# 复制detail的latex
	for file in os.listdir(f"../output/final_topic_portrait/{pid}"):
		if file.endswith('.txt'):
			source = f"../output/final_topic_portrait/{pid}/{file}"
			target = f'../output/{portrait_fold}/{max_visible_depth}/{pid}/{file}'
			shutil.copyfile(source, target)
	print(f'../output/{portrait_fold}/{pid}/{max_visible_depth}/topic x-ray(fa2 vis).jpg')

def worker2x_ray_dot_vis(pid):
	portrait_fold = 'geo_topic_portrait'
	pic_list = []
	sorted_all_years = sorted([int(file.split('.')[0]) for file in os.listdir(f'../temp_files/taged_dot_vis_idea_tree_evolution/{pid}')])
	for year in sorted_all_years:
		pic_list.append(f'../temp_files/taged_dot_vis_idea_tree_evolution/{pid}/{year}.png')
	pic_list.append(f'../temp_files/topic_detail_png/{pid}.png')
	# pic_list.append(f'../temp_files/high_KE_node_detail_png/{pid}/{datetime.datetime.now().year}.jpg')
	pic_list.append(f'../temp_files/skeleton_evolution_related_jpg/{pid}/knowledge_entropy_evolution_with_seminal.jpg')
	pic_list.append(f'../temp_files/skeleton_evolution_related_jpg/{pid}/knowledge_entropy_evolution_without_seminal_paper.jpg')
	pic_list.append(f'../temp_files/skeleton_evolution_related_jpg/{pid}/max_visible_depth.jpg')
	# 将主题按照最大可视深度分类
	year2visibledepth = json.load(open(f'../temp_files/year2visible_depth/{pid}.json'))
	max_visible_depth = max([int(year2visibledepth[year]) for year in year2visibledepth])
	if not os.path.exists(f"../output/{portrait_fold}/{max_visible_depth}/{pid}"):
		os.makedirs(f"../output/{portrait_fold}/{max_visible_depth}/{pid}")

	marge_all_pics(pic_list, column_num=5, interval_width=30, save_path=f'../output/{portrait_fold}/{max_visible_depth}/{pid}/topic x-ray(dot vis).jpg')
	# 复制detail的latex
	for file in os.listdir(f"../output/final_topic_portrait/{pid}"):
		if file.endswith('.txt'):
			source = f"../output/final_topic_portrait/{pid}/{file}"
			target = f'../output/{portrait_fold}/{max_visible_depth}/{pid}/{file}'
			shutil.copyfile(source, target)
	print(f'../output/{portrait_fold}/{pid}/{max_visible_depth}/topic x-ray(dot vis).jpg')

def main():
	pids = ['267126213', '457139010', '12014159', '162137477', '180782032', '372732296', '223164844', '1587314', '194520463', '351922417', '364638540', '263480625']
	
	process_num = len(pids) if len(pids) <= 40 else 40
	with Pool(process_num) as pool:
		pool.map(worker2KE_VD, pids)
	print("Gen KE and VD evolution curve finish!")
	##################################################使用graphviz的dot可视化idea tree###########################################################
	# 0. 先用DOT树可视化算法将idea tree可视化
	process_num = len(pids) if len(pids) <= 40 else 40
	with Pool(process_num) as pool:
		pool.map(gen_dot_vis_idea_tree_png, pids)
	print("Idea tree dot vis finish!")

	# 1. 将主题的结构演进缩略图打上tag
	process_num = len(pids) if len(pids) <= 40 else 40
	with Pool(process_num) as pool:
		pool.map(tag_for_dot_vis_skeleton_tree2, pids)
	print("Dot vis idea tree tag finish!")

	# 2. 生成主题详情png
	process_num = len(pids) if len(pids) <= 40 else 40
	with Pool(process_num) as pool:
		pool.map(topic_detail2png, pids)
	print("Topic detail png gen finish!")

	# 3. 拼合使用Dot算法可视化的idea tree，得到topic的X-ray
	process_num = len(pids) if len(pids) <= 40 else 80
	with Pool(process_num) as pool:
		pool.map(worker2x_ray_dot_vis, pids)
	print("Topic X-ray scan finish(dot vis)!")
	
	##################################################使用gephi-tool可视化idea tree##############################################################
	# # 0. 先生成gephi布局的java代码 https://gephi.org/gephi-toolkit/0.9.1/apidocs/
	# gen_code_cmd = 'python3 ../gephi-tool/scripts/gen_code.py ../gephi-tool/idea_tree_config.json'
	# os.system(gen_code_cmd)
	# print('Code generation finish!')

	# # 1. python控制gephi-tool自动可视化最新一年的脉络树，保证演进布局的一致性
	# if os.path.exists(f"../temp_files/rencent_idea_tree_to_layout"):
	# 	shutil.rmtree(f"../temp_files/rencent_idea_tree_to_layout")
	# 	os.makedirs(f"../temp_files/rencent_idea_tree_to_layout")
	# else:
	# 	os.makedirs(f"../temp_files/rencent_idea_tree_to_layout")

	# for pid in tqdm(pids):
	# 	source = f"../temp_files/attributed_idea_tree_by_year/{pid}/{datetime.datetime.now().year}.gml"
	# 	target = f"../temp_files/rencent_idea_tree_to_layout/{pid}.gml"
	# 	shutil.copyfile(source, target)
	# gephi_tool_abs_path = os.path.abspath('../gephi-tool/scripts/run.py') # 重新配置gephi-tool之后只需更改这一行
	# source_abs_path = os.path.abspath("../temp_files/rencent_idea_tree_to_layout")
	# target_abs_path = os.path.abspath("../temp_files/layouted_rencent_idea_tree")
	# layout_cmd = f"python {gephi_tool_abs_path} {source_abs_path} {target_abs_path} 40"
	# os.system(layout_cmd)
	# print('Init layout finish!')

	# # 2. 使用最新一年的图可视化结果初始化待可视化的gml
	# for pid in tqdm(pids):
	# 	init_year_by_year_gml(str(pid), 'idea_tree_map')
	# print("GML init finish!")
	
	# # 3. 将STL项目下的路径转换为gephi-tool能够处理的路径
	# if not os.path.exists(f"../temp_files/inited_idea_tree_gml_by_year_for_gephi_tool"):
	# 	os.makedirs(f"../temp_files/inited_idea_tree_gml_by_year_for_gephi_tool")
	# else:
	# 	shutil.rmtree(f"../temp_files/inited_idea_tree_gml_by_year_for_gephi_tool")
	# 	os.makedirs(f"../temp_files/inited_idea_tree_gml_by_year_for_gephi_tool")
	# for pid in tqdm(pids):
	# 	copy_idea_tree_gmls_for_gephi_tool(pid)
	# print('Path transform for gephi-tool finish!')

	# # 4. python控制gephi-tool自动化布局所有主题的所有年份下的脉络树演进图
	# if not os.path.exists(f"../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool"): # 先清空临时文件夹
	# 	os.makedirs(f"../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool")
	# else:
	# 	shutil.rmtree(f"../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool")
	# 	os.makedirs(f"../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool")
	# gephi_tool_abs_path = os.path.abspath('../gephi-tool/scripts/run.py') # 重新配置gephi-tool之后只需更改这一行
	# source_abs_path = os.path.abspath("../temp_files/inited_idea_tree_gml_by_year_for_gephi_tool")
	# target_abs_path = os.path.abspath("../temp_files/visulized_idea_tree_gml_by_year_from_gephi_tool")
	# layout_cmd = f"python {gephi_tool_abs_path} {source_abs_path} {target_abs_path} 40"
	# os.system(layout_cmd)
	# print('Layout finish!')

	# # 5. 将gephi-tool生成的带有节点位置的gml文件转换到Topic X-ray的文件结构下
	# for pid in tqdm(pids):
	# 	copy_idea_tree_gmls_from_gephi_tool(pid)
	# print('Path transform for Topic X-ray finish!')

 #    # 6. 将所有的可视化好的gml转换为png
	# args = []
	# for pid in tqdm(pids):
	# 	gmls = os.listdir(f'../temp_files/visulized_idea_tree_gml_by_year/{pid}')
	# 	for gml in gmls:
	# 		year = gml.split('.')[0]
	# 		if not os.path.exists(f"../temp_files/idea_tree_evolution/{pid}"):
	# 			os.makedirs(f"../temp_files/idea_tree_evolution/{pid}")
	# 		args.append((f'../temp_files/visulized_idea_tree_gml_by_year/{pid}/{gml}', f'../temp_files/idea_tree_evolution/{pid}/{year}.png'))
    

	# process_num = len(args) if len(args) <= 40 else 40
	# with Pool(process_num) as pool:
	# 	pool.map(worker2png, args)
	# print("GML2PNG finish!")

	# # 7. 主题的结构演进缩略图打上tag
	# process_num = len(pids) if len(pids) <= 40 else 40
	# with Pool(process_num) as pool:
	# 	pool.map(tag_for_skeleton_tree, pids)
	# print("Idea tree tag finish!")

	# # 8. 生成主题详情png
	# process_num = len(pids) if len(pids) <= 40 else 40
	# with Pool(process_num) as pool:
	# 	pool.map(topic_detail2png, pids)
	# print("Topic detail png gen finish!")

	# # 9. 拼合所有与Topic X-ray相关的图片，得到topic的X-ray
	# process_num = len(pids) if len(pids) <= 40 else 40
	# with Pool(process_num) as pool:
	# 	pool.map(worker2x_ray, pids)
	# print("Topic X-ray scan finish!")


if __name__ == "__main__":
	main()