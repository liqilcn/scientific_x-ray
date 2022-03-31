import os, json
import MySQLdb
import MySQLdb.cursors

from tqdm import tqdm_notebook as tqdm
from readgml import readgml
from PIL import Image, ImageDraw, ImageFont
from get_delta_D_for_specific_topic import get_delta_D_for_specific_topic, get_delta_D_for_specific_topic_in_specific_year

# ### 在星云图脉络树的图片上打上标签，其中包括切片的年份，该年份下网络的节点连边数量，以及主题深度


def tag_for_galaxy_map(spid):
    # 需要事先把所有的可视化完成的gml转成图片
    # 给星云图打标签，包括时间（右上角），节点数，连边数（左下角）
    candidates_pics = os.listdir(f"../temp_files/galaxy_map_evolution/{spid}")
    for pic in candidates_pics:
        if pic.endswith('.png'):
            year = pic.split('.')[0]
            nodes, edges = readgml.read_gml(f"../temp_files/inited_galaxy_map_gml_by_year/{spid}/{year}.gml")
            nodes_num, edges_num = len(nodes), len(edges)
            im = Image.open(f"../temp_files/galaxy_map_evolution/{spid}/{pic}")
            im_w = im.size[0]
            im_h = im.size[1]
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype('./arial.ttf', int(im_w*0.07))  # 第二个参数是字体的尺寸， 使用相对距离
            delta = 5  # 两个标签的文本框与图片边框的具体，可后期调节，但为了美观，四个距离都是一致的
            w, h = draw.textsize(str(year), ttf)
            draw.text((im_w-w-2*delta,delta), str(year), fill = (255, 255, 255), font=ttf)
            w, h = draw.textsize(f"Nodes: {nodes_num} Edges: {edges_num}", ttf)
            draw.text((delta,im_h-h-2*delta), f"Nodes: {nodes_num} Edges: {edges_num}", fill = (255, 255, 255), font=ttf)
            if not os.path.exists(f"../temp_files/taged_galaxy_map_evolution/{spid}"):
                os.makedirs(f"../temp_files/taged_galaxy_map_evolution/{spid}")
            im.save(f"../temp_files/taged_galaxy_map_evolution/{spid}/{year}.png", quality = 100)


def tag_for_skeleton_tree(spid):
    # 需要事先把所有的可视化完成的gml转成图片
    # 给脉络树打标签，包括时间（右上角），主题深度（左下角）
    candidates_pics = os.listdir(f"../temp_files/idea_tree_evolution/{spid}")
    year2visible_depth = json.load(open(f'../temp_files/year2visible_depth/{spid}.json', 'r'))
    for pic in candidates_pics:
        if pic.endswith('.png'):
            year = pic.split('.')[0]
            im = Image.open(f"../temp_files/idea_tree_evolution/{spid}/{pic}")
            im_w = im.size[0]
            im_h = im.size[1]
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype('./arial.ttf', int(im_w*0.07))  # 第二个参数是字体的尺寸， 使用相对距离
            delta = 5  # 两个标签的文本框与图片边框的距离，可后期调节，但为了美观，四个距离都是一致的
            w, h = draw.textsize(str(year), ttf)
            draw.text((im_w-w-2*delta,delta), str(year), fill = (255, 255, 255), font=ttf)
            w, h = draw.textsize(f"Visbile Depth: {year2visible_depth[year]}", ttf)
            draw.text((delta,im_h-h-2*delta), f"Visible Depth: {year2visible_depth[year]}", fill = (255, 255, 255), font=ttf)
            if not os.path.exists(f"../temp_files/taged_idea_tree_evolution/{spid}"):
                os.makedirs(f"../temp_files/taged_idea_tree_evolution/{spid}")
            im.save(f"../temp_files/taged_idea_tree_evolution/{spid}/{year}.png", quality = 100)
            print(f"../temp_files/taged_idea_tree_evolution/{spid}/{year}.png")

def tag_for_dot_vis_skeleton_tree(spid):
    # 需要事先把所有的可视化完成的gml转成图片
    # 给脉络树打标签，包括时间（右上角），主题深度（左下角）
    candidates_pics = os.listdir(f"../temp_files/dot_vis_idea_tree_evolution/{spid}")
    year2visible_depth = json.load(open(f'../temp_files/year2visible_depth/{spid}.json', 'r'))
    for pic in candidates_pics:
        if pic.endswith('.png'):
            year = pic.split('.')[0]
            im = Image.open(f"../temp_files/dot_vis_idea_tree_evolution/{spid}/{pic}")
            im_w = im.size[0]
            im_h = im.size[1]
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype('./arial.ttf', int(im_w*0.07))  # 第二个参数是字体的尺寸， 使用相对距离
            delta = 5  # 两个标签的文本框与图片边框的距离，可后期调节，但为了美观，四个距离都是一致的
            w, h = draw.textsize(str(year), ttf)
            draw.text((im_w-w-2*delta,delta), str(year), fill = (0, 0, 0), font=ttf)
            w, h = draw.textsize(f"Valid Depth: {year2visible_depth[year]}", ttf)
            draw.text((delta,im_h-h-2*delta), f"Valid Depth: {year2visible_depth[year]}", fill = (0, 0, 0), font=ttf)
            if not os.path.exists(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}"):
                os.makedirs(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}")
            im.save(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}/{year}.png", quality = 100)
            print(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}/{year}.png")

def tag_for_dot_vis_skeleton_tree2(spid):
    # 需要事先把所有的可视化完成的gml转成图片
    # 给脉络树打标签，包括DPI（右上角），VD（左下角）
    candidates_pics = os.listdir(f"../temp_files/dot_vis_idea_tree_evolution/{spid}")
    year2visible_depth = json.load(open(f'../temp_files/year2visible_depth/{spid}.json', 'r'))
    for pic in candidates_pics:
        if pic.endswith('.png'):
            year = pic.split('.')[0]
            im = Image.open(f"../temp_files/dot_vis_idea_tree_evolution/{spid}/{pic}")
            im_w = im.size[0]
            im_h = im.size[1]
            draw = ImageDraw.Draw(im)
            ttf = ImageFont.truetype('./arial.ttf', int(im_w*0.07))  # 第二个参数是字体的尺寸， 使用相对距离
            delta = 5  # 两个标签的文本框与图片边框的距离，可后期调节，但为了美观，四个距离都是一致的
            dpi, detail = get_delta_D_for_specific_topic_in_specific_year(spid,2021)
            w, h = draw.textsize(f"DPI: {round(dpi, 3)}", ttf)
            draw.text((im_w-w-2*delta,delta), f"DPI: {round(dpi, 3)}", fill = (0, 0, 0), font=ttf)
            w, h = draw.textsize(f"VD: {year2visible_depth[year]}", ttf)
            draw.text((delta,im_h-h-2*delta), f"VD: {year2visible_depth[year]}", fill = (0, 0, 0), font=ttf)
            if not os.path.exists(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}"):
                os.makedirs(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}")
            im.save(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}/{year}.png", quality = 100)
            print(f"../temp_files/taged_dot_vis_idea_tree_evolution/{spid}/{year}.png")

# ### 拼合瓦片，进而得到类似Nature论文中的图片网格，可拼合星云图与脉络树
# 需要事先生成瓦片文件list，按照顺序

def marge_all_pics(pic_list, column_num, interval_width, save_path):
    # pic_list自行生成好的pic列表
    pic_num = len(pic_list)
    row_num = pic_num // column_num + (1 if pic_num % column_num > 0 else 0)
    # 默认所有瓦片的像素相同，且为方形，先取一个瓦片计算尺寸
    pic = Image.open(pic_list[0])
    pic_w, pic_h = pic.size[0], pic.size[1]
    target = Image.new('RGB', ((pic_w+interval_width)*column_num+interval_width, (pic_h+interval_width)*row_num+interval_width),'#ffffff')
    tile_x, tile_y = 0, 0
    for i in range(row_num):
        tile_y += interval_width
        tile_x = 0
        for j in range(column_num):
            tile_x += interval_width
            if j+column_num*i >= pic_num:
                break
            im = Image.open(pic_list[j+column_num*i])
            target.paste(im, (tile_x, tile_y))
            tile_x += pic_w
        tile_y += pic_h
    target.save(save_path, quality = 100)

# 在2000*2000的空白瓦片上写上主题的detail
class ImgText:
    font = ImageFont.truetype("./arial.ttf", 150)
    def __init__(self, text):
        # 预设宽度 可以修改成你需要的图片宽度
        self.width = 2000
        # 文本
        self.text = text
        # 段落 , 行数, 行高
        self.duanluo, self.note_height, self.line_height = self.split_text()
    def get_duanluo(self, text):
        txt = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        duanluo = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            width, height = draw.textsize(char, ImgText.font)
            sum_width += width
            if sum_width > self.width: # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count
    def split_text(self):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return allText, total_height, line_height
    def draw_text(self, save_path):
        """
        绘图以及文字
        :return:
        """
        note_img = Image.new('RGB', (2000, 2000), '#000000')
        draw = ImageDraw.Draw(note_img)
        # 左上角开始
        x, y = 0, 0
        for duanluo, line_count in self.duanluo:
            draw.text((x, y), duanluo, fill=(255, 0, 0), font=ImgText.font)
            y += self.line_height * line_count
        note_img.save(save_path)

def topic_detail2png(seminal_pid):
    # 将主题的detail写入图片中
    db = MySQLdb.connect(
            host = '10.10.10.10',
            user = 'readonly',
            password = 'readonly',
            db = 'am_paper',
            port = 3306,
            charset = 'utf8mb4',
            cursorclass=MySQLdb.cursors.SSCursor)
    sql = f"SELECT title FROM `am_paper`.`am_paper` WHERE paper_id = {seminal_pid}"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    title = result[0]
    db.close()

    db = MySQLdb.connect(
            host = '10.10.10.10',
            user = 'readonly',
            password = 'readonly',
            db = 'am_analysis',
            port = 3306,
            charset = 'utf8mb4',
            cursorclass=MySQLdb.cursors.SSCursor
    )
    sql = f"SELECT citation_count FROM `am_analysis`.`am_paper_analysis` WHERE paper_id = {seminal_pid}"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    citaion = result[0]
    db.close()
    text = f"Seminal paper ID: {seminal_pid}\nCitation: {citaion}\nSeminal paper title: {title}"
    print(text)
    text2draw = ImgText(text)
    if not os.path.exists(f"../temp_files/topic_detail_png"):
        os.makedirs(f"../temp_files/topic_detail_png")
    save_path = f"../temp_files/topic_detail_png/{seminal_pid}.png"
    text2draw.draw_text(save_path)


if __name__ == '__main__':
    topic_detail2png('4726315')
