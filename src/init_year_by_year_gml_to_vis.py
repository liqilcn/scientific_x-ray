# ### 通过先得到最新的graph的布局，然后将此图中节点的位置作为前面年份的的节点的初始位置，进而保证星云图演进可视化的节点相对位置保持不变

import os
import shutil
import networkx as nx
from readgml import readgml
from tqdm import tqdm_notebook as tqdm
from networkx.utils import is_string_like


# In[22]:


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
        yield 2*indent+f"value {edge2value[str(u)+'|'+str(v)]}"
        yield 2*indent+f"color #{edge2color[str(u)+'|'+str(v)]}"
        yield indent+"]"
    yield "]"


# In[20]:


def graph_init(recent_nodes, recent_edges, can_nodes, can_edges):
    all_node2detail, all_edge2detail = {}, {}
    global edge2value, edge2color
    edge2value, edge2color = {}, {}
    G = nx.DiGraph()
    for node in recent_nodes:
        all_node2detail[str(node['id'])] = node
    for edge in recent_edges:
        s, t = edge['source'], edge['target']
        all_edge2detail[f"{s}|{t}"] = edge
    attred_nodes_set = set()
    for node in can_nodes:
        if str(node['id']) in all_node2detail:
            attred_nodes_set.add(str(node['id']))
        else:
            attred_nodes_set.add(str(node['id']))
            G.add_node(str(node['id']),graphics = {'w':10,'h':10,'d':10,'x':0,'y':0,'z':0,'fill':'#2e5bff'}, L = '')
            continue
        node = all_node2detail[str(node['id'])]
        G.add_node(str(node['id']),graphics = {'w':node['w'],'h':node['h'],'d':node['d'],'x':node['x'],'y':node['y'],'z':node['z'],'fill':"#"+node['fill']}, L = node['label'])
    for edge in can_edges:
        if str(edge['source']) in attred_nodes_set and str(edge['target']) in attred_nodes_set:
            G.add_edge(str(edge['source']), str(edge['target']))
            s, t = edge['source'], edge['target']
            edge2value[f"{s}|{t}"] = all_edge2detail[f"{s}|{t}"]['value'] if f"{s}|{t}" in all_edge2detail else 1.0
            edge2color[f"{s}|{t}"] = '#'+all_edge2detail[f"{s}|{t}"]['color'] if f"{s}|{t}" in all_edge2detail else '#2e5bff'
    # 需要重新设置节点的大小
    id2in_degree = {}
    max_in_degree = 0
    for node in G.node:
        id2in_degree[node] = G.in_degree(node)
        if G.in_degree(node) > max_in_degree:
            max_in_degree = G.in_degree(node)
    min_node_size = 10 if len(G.nodes)/50 > 10 else (len(G.nodes)/50 + 3)
    max_node_sixe = (10 + len(G.nodes)/5) if (10 + len(G.nodes)/5) < (130 + int((len(G.nodes) - 1000)/100)*2.5) else (130 + int((len(G.nodes) - 1000)/100)*2.5)
    for node in G.node:
        G.node[node]['graphics']['w'] = G.in_degree(node) / max_in_degree * max_node_sixe + min_node_size
        G.node[node]['graphics']['h'] = G.in_degree(node) / max_in_degree * max_node_sixe + min_node_size
        G.node[node]['graphics']['d'] = G.in_degree(node) / max_in_degree * max_node_sixe + min_node_size
    return G


# In[21]:


def tree_init(recent_nodes, recent_edges, can_nodes, can_edges):
    # 删减枝叶的树节点可能年份较晚的早额树的节点并未包含在年份较晚的树的节点当中
    all_node2detail, all_edge2detail = {}, {}
    global edge2value, edge2color
    edge2value, edge2color = {}, {}
    G = nx.DiGraph()
    for node in recent_nodes:
        all_node2detail[str(node['id'])] = node

    for node in can_nodes:
        if str(node['id']) in all_node2detail:
            node_recent = all_node2detail[str(node['id'])]
            G.add_node(str(node['id']),graphics = {'w':node['w'],'h':node['h'],'d':node['d'],'x':node_recent['x'],'y':node_recent['y'],'z':node_recent['z'],'fill':"#"+node['fill']}, L = node['label'])
        else:
            G.add_node(str(node['id']),graphics = {'w':node['w'],'h':node['h'],'d':node['d'],'x':0,'y':0,'z':0,'fill':"#"+node['fill']}, L = node['label'])
            
    for edge in can_edges:
        G.add_edge(str(edge['source']), str(edge['target']))
        s, t = edge['source'], edge['target']
        edge2value[f"{s}|{t}"] = edge['value']
        edge2color[f"{s}|{t}"] = edge['color']
    return G


# In[1]:


def init_year_by_year_gml(spid, map_type):
    if map_type == 'galaxy_map':
        nodes, edges = readgml.read_gml(f"../temp_files/layouted_rencent_galaxy_map/{spid}.gml")
        candidate_gmls = os.listdir(f"../temp_files/source_gml_by_year/{spid}")
        for can_gml in candidate_gmls:
            if can_gml.endswith('.gml'):
                can_nodes, can_edges = readgml.read_gml(f"../temp_files/source_gml_by_year/{spid}/{can_gml}")
                G = graph_init(nodes, edges, can_nodes, can_edges)
                year = can_gml.split('.')[0]
                if not os.path.exists(f"../temp_files/inited_galaxy_map_gml_by_year/{spid}"):
                    os.makedirs(f"../temp_files/inited_galaxy_map_gml_by_year/{spid}")
                with open(f"../temp_files/inited_galaxy_map_gml_by_year/{spid}/{year}.gml", 'w') as fp:
                    for line in generate_gml(G):
                        line+='\n'
                        fp.write(line)
    elif map_type == 'idea_tree_map':
        nodes, edges = readgml.read_gml(f"../temp_files/layouted_rencent_idea_tree/{spid}.gml")
        candidate_gmls = os.listdir(f"../temp_files/attributed_idea_tree_by_year/{spid}")
        for can_gml in candidate_gmls:
            if can_gml.endswith('.gml'):
                can_nodes, can_edges = readgml.read_gml(f"../temp_files/attributed_idea_tree_by_year/{spid}/{can_gml}")
                G = tree_init(nodes, edges, can_nodes, can_edges)
                year = can_gml.split('.')[0]
                if not os.path.exists(f"../temp_files/inited_idea_tree_gml_by_year/{spid}"):
                    os.makedirs(f"../temp_files/inited_idea_tree_gml_by_year/{spid}")
                with open(f"../temp_files/inited_idea_tree_gml_by_year/{spid}/{year}.gml", 'w') as fp:
                    for line in generate_gml(G):
                        line+='\n'
                        fp.write(line)
    else:
        print('Wrong map_type!')