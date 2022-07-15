import os
import json
from tqdm import tqdm

from get_high_node_entropy_node_and_subtree_nodes import get_high_node_entropy_and_subtree_nodes_without_exceed

THRESHOLD = 10

class MyNode:
	def __init__(self,ID,label,year):
		self.ID = ID
		self.Label = label
		self.Year = year
		self.Cite = []
		self.BeCited = []
		self.OriginCite = []
		self.OriginBeCited = []

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

	def AppendOriginCite(self,paper):
		self.OriginCite.append(paper)

	def AppendOriginBeCited(self,paper):
		self.OriginBeCited.append(paper)

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
	
	def ReturnOriginCite(self):
		return self.OriginCite

	def ReturnOriginBeCited(self):
		return self.OriginBeCited

	def ReturnOriginCiteTimes(self):
		return len(self.OriginCite)

	def ReturnOriginBeCitedTimes(self):
		return len(self.OriginBeCited)


def get_survey_paper_by_title():
	pid2title = json.load(open('pid2title.json', 'r'))
	pids5000 = json.load(open('pids_7_13.json', 'r'))
	survey_pids = []
	for p_id in pids5000:
		title_lower = pid2title[p_id].lower()
		if 'survey' in title_lower or 'book' in title_lower or 'review' in title_lower or 'summary' in title_lower or 'software' in title_lower or 'introduction' in title_lower:
			survey_pids.append(p_id)
	return survey_pids

def get_VD(pid):
	pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(2021), 'r'))
	tree_node_deep = json.load(open('../temp_files/tree_deep_by_year/'+str(pid)+'/{}'.format(2021), 'r'))
	visible_depths = [] # 将包含点熵大于10的深度值加入，然后取最大值得最大可视深度
	for deep in tree_node_deep:
		for p_id in tree_node_deep[deep]:
			if float(pid2node_entropy[str(p_id)]) >= THRESHOLD:
				visible_depths.append(int(deep))
				break
	max_visible_depth = 0 if len(visible_depths) == 0 else len(visible_depths)-1
	return max_visible_depth


def ispattern2(pid):
	selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes_without_exceed(pid)
	tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/{2021}', 'r'))
	pid2depth = {}
	for dp in tree_node_deep:
		for p_id in tree_node_deep[dp]:
			pid2depth[str(p_id)] = dp
	pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/{2021}', 'r'))
	selected_child_id = []
	selected_pid2subtree_depth = {}
	for p_id in selected_pid2subtree_nodes:
		for child_id in selected_pid2subtree_nodes[p_id]:
			if pid2node_entropy[child_id] >= THRESHOLD:
				selected_child_id.append(child_id)
		selected_child_id_depth = []
		leading_node_depth = int(pid2depth[p_id])
		for s_id in selected_child_id:
			selected_child_id_depth.append(int(pid2depth[s_id]) - leading_node_depth)  # 减去引领文章的深度得到孩子节点在子树中的深度
		selected_pid2subtree_depth[p_id] = len(set(selected_child_id_depth)) if len(set(selected_child_id_depth)) > 0 else 0 # 上面统计主题的可视深度稍有不同，上面是从seminal paper开始，故需要减1，下面是同孩子节点开始，故不需要间
	ispattern2_flag = False
	for p_id in selected_pid2subtree_depth:
		if selected_pid2subtree_depth[p_id] >= 1:
			ispattern2_flag = True
	return ispattern2_flag

def ispattern3(pid):
	pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/2021', 'r'))
	highke_pids = []
	id2node = {}
	NodeList = []
	for p_id in pid2node_entropy:
		if pid2node_entropy[p_id] >= THRESHOLD:
			highke_pids.append(p_id)
	if pid in highke_pids:
		highke_pids.remove(pid)
	node_detail = json.load(open(f'../temp_files/skeleton_tree_by_year/{pid}/2021', 'r'))
	for node in node_detail:
		ID = str(node)
		node = str(node)
		label = node_detail[node]['label']
		year = node_detail[node]['year']
		NewNode = MyNode(ID,label,year)
		id2node[node] = NewNode

	for node in id2node:
		for nd in node_detail[node]['cite']:
			id2node[node].AppendCite(id2node[str(nd)])
		for nd in node_detail[node]['becited']:
			id2node[node].AppendBeCited(id2node[str(nd)])
		NodeList.append(id2node[node])

	highke_pids_set = set(highke_pids)
	highke_pid2highke_pids_in_path = {}
	for p_id in highke_pids:
		Node = id2node[p_id]
		highke_pid2highke_pids_in_path[p_id] = []
		while Node.ReturnCiteTimes() == 1:
			parent_id = Node.ReturnCite()[0].ReturnID()
			if parent_id in highke_pids_set:
				highke_pid2highke_pids_in_path[p_id].append(parent_id)
			Node = Node.ReturnCite()[0]
	
	ispattern3_flag = False
	for p_id in highke_pid2highke_pids_in_path:
		if len(highke_pid2highke_pids_in_path[p_id]) >= 3:
			ispattern3_flag = True
	return ispattern3_flag

def ispattern4(pid):
	pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/2021', 'r'))
	over_powered_pid = ''
	for p_id in pid2node_entropy:
		if pid2node_entropy[p_id] >= pid2node_entropy[pid] and pid != p_id:
			over_powered_pid = p_id
	if over_powered_pid == '':
		return False
	else:
		selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes_without_exceed(pid)
		tree_node_deep = json.load(open(f'../temp_files/tree_deep_by_year/{pid}/{2021}', 'r'))
		pid2depth = {}
		for dp in tree_node_deep:
			for p_id in tree_node_deep[dp]:
				pid2depth[str(p_id)] = dp
		selected_child_id = []
		selected_pid2subtree_depth = -1
		for child_id in selected_pid2subtree_nodes[over_powered_pid]:
			if pid2node_entropy[child_id] >= THRESHOLD:
				selected_child_id.append(child_id)
		selected_child_id_depth = []
		leading_node_depth = int(pid2depth[over_powered_pid])
		for s_id in selected_child_id:
			selected_child_id_depth.append(int(pid2depth[s_id]) - leading_node_depth)  # 减去引领文章的深度得到孩子节点在子树中的深度
		selected_pid2subtree_depth = len(set(selected_child_id_depth)) if len(set(selected_child_id_depth)) > 0 else 0
		if selected_pid2subtree_depth <= 2:
			return True
		else:
			return False

def ispattern5(pid):
	pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/2021', 'r'))
	highke_pids = []
	for p_id in pid2node_entropy:
		if pid2node_entropy[p_id] >= THRESHOLD and pid != p_id:
			highke_pids.append(p_id)
	if len(highke_pids) < 2:
		return False
	else:
		sorted_highke_pids = sorted(highke_pids, key = lambda item:pid2node_entropy[item], reverse=True)
		top1kepid, top2kepid = sorted_highke_pids[0], sorted_highke_pids[1]
		selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes_without_exceed(pid)
		top1kepid2children = selected_pid2subtree_nodes[top1kepid]
		if top2kepid not in set(top1kepid2children):
			return False
		else:
			node_detail = json.load(open(f'../temp_files/skeleton_tree_by_year/{pid}/2021', 'r'))
			pid2year = {}
			for node in node_detail:
				ID = str(node)
				node = str(node)
				year = node_detail[node]['year']
				pid2year[ID] = year
			if int(pid2year[top1kepid]) > int(pid2year[top2kepid]):
				return True
			else:
				return False

def ispattern6(pid):
	pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/2021', 'r'))
	vd = get_VD(pid)
	if not (vd >= 5 and vd <= 6):
		return False
	else:
		highke_pids = []
		for p_id in pid2node_entropy:
			if pid2node_entropy[p_id] >= THRESHOLD and pid != p_id:
				highke_pids.append(p_id)
		if len(highke_pids) >= 7:
			return True
		else:
			return False

def isother_pattern(pid):
	# 所有高KE节点均未能产生孩子节点，且VD大于等于2
	selected_pid2subtree_nodes = get_high_node_entropy_and_subtree_nodes_without_exceed(pid)
	pid2node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/2021', 'r'))
	highke_pids = []
	for p_id in pid2node_entropy:
		if pid2node_entropy[p_id] >= THRESHOLD and pid != p_id:
			highke_pids.append(p_id)
	other_pattern_flag = 0
	for p_id in selected_pid2subtree_nodes:
		children_nodes = selected_pid2subtree_nodes[p_id]
		if len(set(children_nodes).intersection(set(highke_pids))) >= 1:
			other_pattern_flag = 1
	if other_pattern_flag == 0:
		return True
	else:
		return False





if __name__ == "__main__":
	survey_pids = get_survey_paper_by_title()
	pattern1_pids = []
	for p_id in survey_pids:
		vd = get_VD(p_id)
		if vd <= 1:
			pattern1_pids.append(p_id)
	print(f'pattern1:{len(pattern1_pids)}')

	selected_pids2 = []
	for p_id in tqdm(json.load(open('pids_7_13.json', 'r'))):
		if get_VD(p_id) >= 2:
			selected_pids2.append(p_id)
	print(len(selected_pids2))

	pattern2_pids = []
	for p_id in tqdm(selected_pids2):
		if ispattern2(p_id):
			pattern2_pids.append(p_id)
	print(f'pattern2:{len(pattern2_pids)}')

	pattern3_pids = []
	for p_id in tqdm(selected_pids2):
		if ispattern3(p_id):
			pattern3_pids.append(p_id)
	print(f'pattern3:{len(pattern3_pids)}')

	pattern4_pids = []
	for p_id in tqdm(selected_pids2):
		if ispattern4(p_id):
			pattern4_pids.append(p_id)
	print(f'pattern4:{len(pattern4_pids)}')

	pattern5_pids = []
	for p_id in tqdm(selected_pids2):
		if ispattern5(p_id):
			pattern5_pids.append(p_id)
	print(f'pattern5:{len(pattern5_pids)}')

	pattern6_pids = []
	for p_id in tqdm(selected_pids2):
		if ispattern6(p_id):
			pattern6_pids.append(p_id)
	print(f'pattern6:{len(pattern6_pids)}')

	hitted_pid_num = len(set(pattern1_pids+pattern2_pids+pattern3_pids+pattern4_pids+pattern5_pids+pattern6_pids))
	sum_num = len(pattern1_pids) + len(selected_pids2)
	print(hitted_pid_num)
	print(sum_num)
	print(hitted_pid_num/sum_num)

	other_pattern_pids = []
	for p_id in tqdm(selected_pids2):
		if isother_pattern(p_id):
			other_pattern_pids.append(p_id)
	print(f'other:{len(other_pattern_pids)}')














