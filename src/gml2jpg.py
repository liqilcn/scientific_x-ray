from readgml import readgml
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os
import re
import sys
import json
from tqdm import tqdm
from multiprocessing.pool import Pool

def draw_path(path):
    # 此函数仅用于对dot布局产生的脉络树svg的path进行绘制
    # path的值是多个三阶贝塞尔曲线的组合，故其参数长度必定为3*n + 1（包含M参数的点）
    # 当完成另一个曲线的绘制后，最后的点作为下一条曲线绘制的起点
    path_split = re.split('M|C', path)
    path_c = []
    p_0_x = ((float(path_split[1].split(',')[0])) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
    p_0_y = ((float(path_split[1].split(',')[1])) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
    path_c.append((p_0_x, p_0_y))
    path_c_split = path_split[2].split(' ')
    for p in path_c_split:
        x = ((float(p.split(',')[0])) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
        y = ((float(p.split(',')[1])) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
        point = (x, y)
        path_c.append(point)
    # 生成未加限制点的贝塞尔曲线散点
    ts = np.linspace(0, 1, 301)
    args = np.array([((1 - t)**3, 3 * t * ((1 - t)**2), 3 * (t**2) * (1 - t), t**3) for t in ts]) # dot生成的svg中含有多个三阶贝塞尔曲线的组合   
    points = []
    for i in range(int((len(path_c)-1)/3)):
        ctrl_point = [path_c[3*i], path_c[3*i+1], path_c[3*i+2], path_c[3*i+3]]
        xs = (args * [i[0] for i in ctrl_point]).sum(1).tolist()
        ys = (args * [i[1] for i in ctrl_point]).sum(1).tolist()
        points.extend(list(zip(xs, ys)))
    
    return points
    
def pathd(x1, y1, x2, y2, bezierCurveness=0.2):
    # 计算贝塞尔曲线的P0P1P2P3
    length = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    factor = bezierCurveness * length
    v1_X = ((x2 - x1 + y2 - y1) * factor + x1 * length) / length
    v1_Y = ((y2 - y1 + x1 - x2) * factor + y1 * length) / length
    v2_X = ((x1 - x2 + y2 - y1) * factor + x2 * length) / length
    v2_Y = ((y1 - y2 + x1 - x2) * factor + y2 * length) / length
    return [(x1, y1), (v1_X, v1_Y), (v2_X, v2_Y), (x2, y2)]


def gml2png(gml_input_path, png_output_path, label_flag=True, straight_line=False, bg_type=1):

    # bg_type = 1黑色，0白色
    im_size = 2000
    nodes, edges = readgml.read_gml(gml_input_path)
    graph = {}
    graph['nodes'] = {}
    graph['edges'] = []
    for node in nodes:
        if node['id'] not in graph['nodes']:
            graph['nodes'][node['id']] = {}
        graph['nodes'][node['id']]['x'] = node['x']
        graph['nodes'][node['id']]['y'] = node['y']
        graph['nodes'][node['id']]['fill'] = node['fill']
        graph['nodes'][node['id']]['r'] = node['w']
        graph['nodes'][node['id']]['label'] = node['label']
    for edge in edges:
        graph['edges'].append(edge)

    min_x = min(float(graph['nodes'][node]['x']) for node in graph['nodes'])
    min_y = min(float(graph['nodes'][node]['y']) for node in graph['nodes'])
    max_x = max(float(graph['nodes'][node]['x']) for node in graph['nodes'])
    max_y = max(float(graph['nodes'][node]['y']) for node in graph['nodes'])
    max_r = max(float(graph['nodes'][node]['r']) for node in graph['nodes'])
    global bbox,im_w,im_h,im_s
    bbox = [min_x - max_r - 100, min_y - max_r - 100, max_x + max_r + 100, max_y + max_r + 100]

    im_w = im_size * 4  # image的x方向长度
    im_h = int(im_w * ((bbox[3] - bbox[1]) / (bbox[2] - bbox[0])))  # image的y方向长度
    im_s = int(max(im_w, im_h))  # 保证图片为方形
    if bg_type == 1:
        im = Image.new('RGB', (im_s, im_s), '#000000')
    elif bg_type == 0:
        im = Image.new('RGB', (im_s, im_s), '#ffffff')
    draw = ImageDraw.Draw(im)

    # draw edges
    ts = np.linspace(0, 1, 301)
    args = np.array([((1 - t)**3, 3 * t * ((1 - t)**2), 3 * (t**2) * (1 - t), t**3) for t in ts])
    for edge in graph['edges']:
        if 'path' not in edge:
            p = {}
            p['xs'] = []
            p['ys'] = []
            # 对原始gml中的坐标进行变换到当前位图绘制坐标系内，以下代码同理
            x1 = ((graph['nodes'][edge['source']]['x']) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
            y1 = ((graph['nodes'][edge['source']]['y']) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
            x2 = ((graph['nodes'][edge['target']]['x']) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
            y2 = ((graph['nodes'][edge['target']]['y']) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
            if straight_line:
                pd = pathd(x1, y1, x2, y2, bezierCurveness=0)
            else:
                pd = pathd(x1, y1, x2, y2)
            for i in range(4):
                p['xs'].append(pd[i][0])
                p['ys'].append(pd[i][1])
            xs = (args * [i for i in p['xs']]).sum(1).tolist()
            ys = (args * [i for i in p['ys']]).sum(1).tolist()
            points = list(zip(xs, ys))
        else:
            points = draw_path(edge['path'])
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill='#' + edge['color'], width=int(edge['value']))

    # draw nodes
    for node in graph['nodes']:
        r = graph['nodes'][node]['r']
        x1 = ((graph['nodes'][node]['x'] - r) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
        y1 = ((graph['nodes'][node]['y'] - r) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
        x2 = ((graph['nodes'][node]['x'] + r) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
        y2 = ((graph['nodes'][node]['y'] + r) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
        draw.ellipse([x1, y1, x2, y2], fill='#' + graph['nodes'][node]['fill'])

    # draw labels
    for node in graph['nodes']:
        if not label_flag:
            break
        if graph['nodes'][node]['label'] == '':
            continue
        r = graph['nodes'][node]['r']
        x1 = ((graph['nodes'][node]['x'] - r) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
        y1 = ((graph['nodes'][node]['y'] - r) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
        x2 = ((graph['nodes'][node]['x'] + r) - bbox[0]) / (bbox[2] - bbox[0]) * im_w + (im_s - im_w) / 2
        y2 = ((graph['nodes'][node]['y'] + r) - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
        # font_size = int((x2 - x1) / 0.9)  # 待定
        # print(font_size)
        font_size = 700
        font = ImageFont.truetype("./arial.ttf", font_size)
        w, h = draw.textsize(graph['nodes'][node]['label'], font)
        # 标题的缩略显示
        text_start = [(x1 + x2) / 2 - w / 2, (y1 + y2) / 2 - h / 2]
        center = [(x1 + x2) / 2, (y1 + y2) / 2]
        if (x1 + x2) / 2 > (im_w + (im_s - im_w) / 2) / 2:
            min_d = im_w + (im_s - im_w) / 2 - (x1 + x2) / 2
        else:
            min_d = (x1 + x2) / 2
        if w / 2 < min_d:
            if bg_type == 1:
                draw.text(text_start, graph['nodes'][node]['label'], fill="#000000", font=font)
            elif bg_type == 0:
                draw.text(text_start, graph['nodes'][node]['label'], fill="#3b98c9", font=font)
        else:
            label = ''
            w0, h0 = draw.textsize('…', font)  # 省略号在该字体下的长度
            for i in graph['nodes'][node]['label']:
                w, h = draw.textsize(label + i + i + i + i, font)
                if (w + w0) / 2 < min_d:
                    label += i
                else:
                    label = label + '…'
                    break
            w, h = draw.textsize(label, font)
            text_start = [(x1 + x2) / 2 - w / 2, (y1 + y2) / 2 - h / 2]
            if bg_type == 1:
                draw.text(text_start, label, fill="#000000", font=font)
            elif bg_type == 0:
                draw.text(text_start, label, fill="#3b98c9", font=font)
    im.thumbnail((im_w / 4, im_w / 4))
    im.save(png_output_path, "PNG")
#     maxY = (bbox[3] - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
#     minY = (bbox[1] - bbox[1]) / (bbox[3] - bbox[1]) * im_h + (im_s - im_h) / 2
#     graph_dy = abs(maxY - minY)
#     if graph_dy/4 >= im_size:
#         im.save(png_output_path, "PNG")
#     else:
#         start_y = im_size/2 - graph_dy/8
#         end_y = im_size - start_y
#         im_c = im.crop((0, start_y, im_size, end_y)) 
#         im_c.save(png_output_path, "PNG")