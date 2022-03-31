import json
import os
import queue

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

TREE_JSON_FILE_PATH = '../temp_files/skeleton_tree_by_year/'
TREE_DEEP_PATH = '../temp_files/tree_deep_by_year/'
SIMPLIED_TREE_JSON_FILE_PATH = '../temp_files/simplied_skeleton_tree_by_year/'
THRESHOLD = 10

def subtree_node_num(Node):
    # 获取根节点A的子树内的节点数量
    NodeList = []
    MyQueue = queue.Queue()
    MyQueue.put(Node)
    while (not(MyQueue.empty())):
        NodeNow = MyQueue.get()
        NodeList.append(NodeNow)
        for NodeLinked in NodeNow.ReturnBeCited():
            MyQueue.put(NodeLinked)
    return len(NodeList)

def get_subtree_pids(Node):
    NodeIDList = [Node.ReturnID()]
    MyQueue = queue.Queue()
    MyQueue.put(Node)
    while (not(MyQueue.empty())):
        NodeNow = MyQueue.get()
        NodeIDList.append(NodeNow.ReturnID())
        for NodeLinked in NodeNow.ReturnBeCited():
            MyQueue.put(NodeLinked)
    return NodeIDList

def get_nodes_in_path2seminal_paper(node):
    # 包含node节点的id，但不包含seminal_paper的id
    selected_pids = []
    selected_pids.append(node.ReturnID())
    while (not node.ReturnCiteTimes() == 0):
        selected_pids.append(str(node.ReturnCite()[0].ReturnID()))
        node = node.ReturnCite()[0]
    return selected_pids




def simply_skeleton_tree_2(pid, yr, rescale_len=25):
    # 第二种简化脉络树的方法
    # 根据最近年份最宽的层来rescale以往年份所有的层，且保留原始idea tree的shape
    # 先保留当前的所有高知识熵节点，以及通往seminal paper的路径上的所有节点，保持连通性
    pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(pid)+'/{}'.format(yr), 'r'))
    all_high_ke_nodes = [] # 不包含seminal_paper
    for p_id in pid2node_entropy:
        if str(pid) == str(p_id):
            continue
        if pid2node_entropy[p_id] >= THRESHOLD:
            all_high_ke_nodes.append(str(p_id))

    node_detail = json.load(open(TREE_JSON_FILE_PATH+str(pid)+'/'+str(yr), 'r'))
    id2node = {}
    NodeList = []
    for node in node_detail:
        ID = node
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

    all_path_pids = []
    for p_id in all_high_ke_nodes:
        all_path_pids += get_nodes_in_path2seminal_paper(id2node[p_id])

    all_path_pids = list(set(all_path_pids))
    all_path_pids_set = set(all_path_pids)

    max_year = 2021
    last_tree_deep = json.load(open(TREE_DEEP_PATH+str(pid)+'/'+str(max_year), 'r'))
    max_tree_width = 0
    for dp in last_tree_deep:
        if len(last_tree_deep[dp]) >= max_tree_width:
            max_tree_width = len(last_tree_deep[dp])
    rescale_factor = rescale_len/max_tree_width  # 至此，将所有idea树都归一化到最大宽度为rescale_len

    tree_deep = json.load(open(TREE_DEEP_PATH+str(pid)+'/'+str(yr), 'r'))

    # 筛选最终保留的pids
    selected_pids = [str(pid)]
    for depth in range(0,len(tree_deep)):
        if depth == 0:
            next_layer_pids = []
            next_layer_selected_pids = []
            for node in id2node[str(tree_deep[str(depth)][0])].ReturnBeCited():
                if str(node.ReturnID()) in all_path_pids_set:
                    selected_pids.append(str(node.ReturnID()))
                    next_layer_selected_pids.append(str(node.ReturnID()))
                    continue
                next_layer_pids.append(str(node.ReturnID()))
            p_id2subtree_node_num = {}
            for p_id in next_layer_pids:
                p_id2subtree_node_num[str(p_id)] = subtree_node_num(id2node[str(p_id)])
            sorted_tuple = sorted(p_id2subtree_node_num.items(), key=lambda item:item[1], reverse=True)
            
            for i in range(int(len(sorted_tuple)*rescale_factor)):
                next_layer_selected_pids.append(sorted_tuple[i][0])
                selected_pids.append(sorted_tuple[i][0])
        else:
            current_layer_pids = next_layer_selected_pids
            next_layer_pids = []
            next_layer_selected_pids = []
            for p_id in current_layer_pids:
                for node in id2node[p_id].ReturnBeCited():
                    if str(node.ReturnID()) in all_path_pids_set:
                        selected_pids.append(str(node.ReturnID()))
                        next_layer_selected_pids.append(str(node.ReturnID()))
                        continue
                    next_layer_pids.append(str(node.ReturnID())) 
            p_id2subtree_node_num = {}
            for p_id in next_layer_pids:
                p_id2subtree_node_num[str(p_id)] = subtree_node_num(id2node[str(p_id)])
            sorted_tuple = sorted(p_id2subtree_node_num.items(), key=lambda item:item[1], reverse=True)
            
            for i in range(int(len(sorted_tuple)*rescale_factor)):
                next_layer_selected_pids.append(sorted_tuple[i][0])
                selected_pids.append(sorted_tuple[i][0])

    print(len(selected_pids), len(pid2node_entropy))
    new_node_list = []
    new_id2node = {}
    
    for node in node_detail:
        if str(node) in selected_pids:
            ID = node
            node = str(node)
            label = node_detail[node]['label']
            year = node_detail[node]['year']
            NewNode = MyNode(ID,label,year)
            new_id2node[node] = NewNode
            
    for node in new_id2node:
        for nd in node_detail[node]['cite']:
            if str(node) in selected_pids and str(nd) in selected_pids:
                new_id2node[node].AppendCite(new_id2node[str(nd)])
        for nd in node_detail[node]['becited']:
            if str(node) in selected_pids and str(nd) in selected_pids:
                new_id2node[node].AppendBeCited(new_id2node[str(nd)])
        if len(new_id2node[node].ReturnCite()) == 0 and new_id2node[node].ReturnID() != str(pid):
            continue
        new_node_list.append(new_id2node[node])
    
    node_detail = {}
    for node in new_node_list:
        if node.ReturnID() not in node_detail:
            node_detail[str(node.ReturnID())] = {}
        node_detail[str(node.ReturnID())]['label'] = node.ReturnLabel()
        node_detail[str(node.ReturnID())]['year'] = node.ReturnYear()[0:4]
        node_detail[str(node.ReturnID())]['cite'] = [node.ReturnID() for node in node.ReturnCite()]
        node_detail[str(node.ReturnID())]['becited'] = [node.ReturnID() for node in node.ReturnBeCited()]
    print(len(node_detail))
    if not os.path.exists(SIMPLIED_TREE_JSON_FILE_PATH+str(pid)):
        os.makedirs(SIMPLIED_TREE_JSON_FILE_PATH+str(pid))
    json.dump(node_detail, open(SIMPLIED_TREE_JSON_FILE_PATH+str(pid)+'/'+str(yr), 'w'))





def simply_skeleton_tree(pid, yr, simply_ratio=0.05):
    # 根据上述三个原则对脉络树进行精简
    node_detail = json.load(open(TREE_JSON_FILE_PATH+str(pid)+'/'+str(yr), 'r'))
    id2node = {}
    NodeList = []
    for node in node_detail:
        ID = node
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
    tree_deep = json.load(open(TREE_DEEP_PATH+str(pid)+'/'+str(yr), 'r'))

    selected_pids = set(list(id2node.keys()))
    for depth in range(1,len(tree_deep)):
        p_id2subtree_node_num = {}
        for p_id in tree_deep[str(depth)]:
            p_id = str(p_id)
            if p_id in selected_pids:
                p_id2subtree_node_num[p_id] = subtree_node_num(id2node[p_id])
        sorted_tuple = sorted(p_id2subtree_node_num.items(), key=lambda item:item[1], reverse=True)
        for i in range(int(simply_ratio*len(sorted_tuple)), len(sorted_tuple)): #留下前三个子树  佛光普照型取140个子树
            s_pids = get_subtree_pids(id2node[sorted_tuple[i][0]])
            for p_id in s_pids:
                if p_id in selected_pids:
                    selected_pids.remove(p_id)
    
    new_node_list = []
    new_id2node = {}
    
    for node in node_detail:
        if str(node) in selected_pids:
            ID = node
            node = str(node)
            label = node_detail[node]['label']
            year = node_detail[node]['year']
            NewNode = MyNode(ID,label,year)
            new_id2node[node] = NewNode
            
    for node in new_id2node:
        for nd in node_detail[node]['cite']:
            if str(node) in selected_pids and str(nd) in selected_pids:
                new_id2node[node].AppendCite(new_id2node[str(nd)])
        for nd in node_detail[node]['becited']:
            if str(node) in selected_pids and str(nd) in selected_pids:
                new_id2node[node].AppendBeCited(new_id2node[str(nd)])
        if len(new_id2node[node].ReturnCite()) == 0 and new_id2node[node].ReturnID() != str(pid):
            continue
        new_node_list.append(new_id2node[node])
    
    node_detail = {}
    for node in new_node_list:
        if node.ReturnID() not in node_detail:
            node_detail[str(node.ReturnID())] = {}
        node_detail[str(node.ReturnID())]['label'] = node.ReturnLabel()
        node_detail[str(node.ReturnID())]['year'] = node.ReturnYear()[0:4]
        node_detail[str(node.ReturnID())]['cite'] = [node.ReturnID() for node in node.ReturnCite()]
        node_detail[str(node.ReturnID())]['becited'] = [node.ReturnID() for node in node.ReturnBeCited()]
    
    print(len(node_detail))
    if not os.path.exists(SIMPLIED_TREE_JSON_FILE_PATH+str(pid)):
    	os.makedirs(SIMPLIED_TREE_JSON_FILE_PATH+str(pid))
    json.dump(node_detail, open(SIMPLIED_TREE_JSON_FILE_PATH+str(pid)+'/'+str(yr), 'w'))