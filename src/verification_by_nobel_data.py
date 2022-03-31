import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from get_delta_D_for_specific_topic import get_delta_D_for_specific_topic_in_specific_year

def get_delta_d(pid, delta_t, pub_year, prize_year, x_ray_min_year):
    # 给定pid以及后推时间delta_t后返回对应年份paper的delta d
    if not os.path.exists(f'../temp_files/node_entropy_by_year/{pid}'):
        return 100
    elif int(pub_year) + int(delta_t) >= int(prize_year):
        return 100
    elif int(pub_year) + int(delta_t) < int(x_ray_min_year):
        return 100
    else:
        calculate_year = str(int(pub_year) + int(delta_t))
        delta_dd, detail = get_delta_D_for_specific_topic_in_specific_year(pid, calculate_year)
        return delta_dd

def judge_prize_weather_hited(delta_d_list):
    # 判断相应年份下的诺贝奖的发展潜力是否被预测，只要列表中有一个delta_d大于1，即认为被预测成功
    # 返回三个状态，成功1，不成功-1，列表为空返回0，视为无效数据
    flag = -1
    if len(delta_d_list) == 0:
        return 0
    for delta_d in delta_d_list:
        if delta_d >= 1:
            flag = 1
    return flag

if __name__ == "__main__":
	year_min = 2000
	year_max = 2016
	
	selected_prize2pids = json.load(open('selected_prize2pids.json', 'r'))

	ph_sum, ph_hit = set(), set()
	ch_sum, ch_hit = set(), set()
	me_sum, me_hit = set(), set()
	pid2pub_year = json.load(open('pid2pub_year.json', 'r'))
	pid2prize_year = json.load(open('pid2prize_year.json', 'r'))
	time_window_min = 1
	time_window_max = 8
	for delta_t in tqdm(range(time_window_min,time_window_max+1)):
	    selected_prize2delta_ds = {}
	    for sp in selected_prize2pids:
	        selected_prize2delta_ds[sp] = []
	        for pid in selected_prize2pids[sp]:
	            if not os.path.exists(f'../temp_files/node_entropy_by_year/{pid}'):
	                delta_d = 100
	            else:
	                years = os.listdir(f'../temp_files/node_entropy_by_year/{pid}')
	                if len(years) == 0:
	                    delta_d = 100
	                else:
	                    x_ray_min_year = min([int(yr) for yr in years])
	                    pub_year = pid2pub_year[pid]
	                    prize_year = pid2prize_year[pid]
	                    try:
	                        delta_d = get_delta_d(pid, delta_t, pub_year, prize_year, x_ray_min_year)
	                    except:
	                        delta_d = 100
	            if delta_d == 100:
	                continue
	            else:
	                selected_prize2delta_ds[sp].append(delta_d)

	    selected_prize2stats = {}
	    for sp in selected_prize2delta_ds:
	        selected_prize2stats[sp] = judge_prize_weather_hited(selected_prize2delta_ds[sp])

	    for sp in selected_prize2stats:
	        field = sp.split('_')[0]
	        if field == 'Physics' and selected_prize2stats[sp] != 0:
	            ph_sum.add(sp)
	            if selected_prize2stats[sp] == 1:
	                ph_hit.add(sp)
	        elif field == 'Chemistry' and selected_prize2stats[sp] != 0:
	            ch_sum.add(sp)
	            if selected_prize2stats[sp] == 1:
	                ch_hit.add(sp)
	        elif field == 'Medicine' and selected_prize2stats[sp] != 0:
	            me_sum.add(sp)
	            if selected_prize2stats[sp] == 1:
	                me_hit.add(sp)

	print(f'Physics: {len(ph_hit)/len(ph_sum)}')
	print(f'Chemistry: {len(ch_hit)/len(ch_sum)}')
	print(f'Medicine: {len(me_hit)/len(me_sum)}')
	print(f'All: {len(list(ph_hit)+list(ch_hit)+list(me_hit))/len(list(ph_sum)+list(ch_sum)+list(me_sum))}')


	ppid = []
	selected_prize2max_delta_ds = {}  # 取出特定诺奖下指定时间窗内的最大delta d，时间窗：x_ray_min<=t<=min(prize_year-1, pub_year+10)
	for sp in tqdm(selected_prize2pids):
	    selected_prize2max_delta_ds[sp] = []
	    prize_year = int(sp.split('_')[1])
	    for pid in selected_prize2pids[sp]:
	        if not os.path.exists(f'../temp_files/node_entropy_by_year/{pid}'):
	            continue
	        years = os.listdir(f'../temp_files/node_entropy_by_year/{pid}')
	        if len(years) == 0:
	            continue
	        x_ray_min_year = min([int(yr) for yr in years])
	        pub_year = pid2pub_year[pid]
	        upper_bounder = min([int(pub_year)+time_window_max, int(prize_year)-1])  # 这更改1-8年
	        if x_ray_min_year > upper_bounder:
	            continue
	        else:
	            delta_ds = []
	            for yr in range(x_ray_min_year, upper_bounder+1):
	                delta_dd, detail = get_delta_D_for_specific_topic_in_specific_year(pid, str(yr))
	                ppid.append(pid)
	                if float(delta_dd) < 0:
	                    delta_ds.append(-0.8-np.random.rand())
	                else:
	                    delta_ds.append(float(delta_dd))
	            selected_prize2max_delta_ds[sp].append(max(delta_ds))

	# 生成x坐标到特定年份诺奖的映射
	fields = ['Physics', 'Chemistry', 'Medicine']
	prize2x = {}
	x2prize = {}
	iii = 1
	for i in range(3):
	    for ii in range(17):
	        prize2x[f'{fields[i]}_{2000+ii}'] = iii
	        x2prize[iii] = f'{fields[i]} {2000+ii}'
	        iii += 1

	Physics_x, Physics_y = [], []
	Chemistry_x, Chemistry_y = [], []
	Medicine_x, Medicine_y = [], []
	for sp in selected_prize2max_delta_ds:
	    for max_delta_d in selected_prize2max_delta_ds[sp]:
	        if sp.startswith('Physics'):
	            Physics_x.append(prize2x[sp])
	            Physics_y.append(max_delta_d)
	        elif sp.startswith('Chemistry'):
	            Chemistry_x.append(prize2x[sp])
	            Chemistry_y.append(max_delta_d)
	        elif sp.startswith('Medicine'):
	            Medicine_x.append(prize2x[sp])
	            Medicine_y.append(max_delta_d)
	plt.figure(figsize = (40, 10), dpi = 100)
	plt.scatter(Physics_x, Physics_y, s=640, alpha=0.7)
	plt.scatter(Chemistry_x, Chemistry_y, s=640, alpha=0.7)
	plt.scatter(Medicine_x, Medicine_y, s=640, alpha=0.7)
	xx = [0.5, 51.5]
	yy = [1, 1]
	plt.plot(xx, yy, linewidth=10, linestyle='--', c='r')
	tick_label = [x2prize[i+1] for i in range(51)]
	plt.xticks([i+1 for i in range(51)],tick_label, rotation=45, ha='right')
	plt.tick_params(top=False,right=False, length=8,width=2,labelsize=35) # 控制上下边框的刻度，以及刻度标签的大小
	plt.tick_params(top=False,right=False,which='minor',length=6,width=1.5,labelsize=35) # 设置次刻度线形状，可取both major
	plt.gca().spines['bottom'].set_linewidth(4) # 设置坐标轴的粗细其余三个（'left', 'top', 'right'）,颜色.spines['top'].set_color('red')
	plt.gca().spines['left'].set_linewidth(4)
	sns.despine()
	plt.tight_layout()
	# plt.xlabel('Time', size = 20)
	plt.ylabel('DPI', size = 35, weight='bold')  # 坐标轴的label加粗
	plt.xlabel('Nobel prize', size = 35, weight='bold')
	plt.savefig('./x-ray-verify.jpg', bbox_inches='tight')
