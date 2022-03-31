#!/usr/bin/env python
# coding: utf-8

# In[45]:


import os
import csv
import json
import datetime
import MySQLdb
import MySQLdb.cursors
from tqdm import tqdm

from get_delta_D_for_specific_topic import get_delta_D_for_specific_topic


# In[43]:


def get_paper_title(pid):
    db = MySQLdb.connect(
        host = '10.10.10.10',
        user = 'readonly',
        password = 'readonly',
        db = 'am_paper',
        port = 3306,
        charset = 'utf8mb4',
        cursorclass=MySQLdb.cursors.SSCursor
        )
    sql = f"SELECT title FROM `am_paper`.`am_paper` WHERE paper_id = {pid}"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    db.close()
    return result[0]


def get_paper_citation(pid):
    db = MySQLdb.connect(
        host = '10.10.10.10',
        user = 'readonly',
        password = 'readonly',
        db = 'am_analysis',
        port = 3306,
        charset = 'utf8mb4',
        cursorclass=MySQLdb.cursors.SSCursor
        )
    sql = f"SELECT citation_count FROM `am_analysis`.`am_paper_analysis` WHERE paper_id = {pid}"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    db.close()
    return result[0]

# In[59]:


def main(tpids):
    # 使用scientific X-ray度量给定主题列表的发展潜力，并给出排名后的csv文件
    pid2topic_delta_D = {}
    for p_id in tqdm(tpids):
        topic_delta_D, detail= get_delta_D_for_specific_topic(p_id)
        try:
            topic_delta_D, detail= get_delta_D_for_specific_topic(p_id)
        except:
            continue
        pid2topic_delta_D[p_id] = topic_delta_D
    sorted_pid2topic_delta_D = sorted(pid2topic_delta_D.items(), key = lambda item:item[1], reverse=True)
    
    dt = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    with open(f'topic_potential_ranking_{dt}.csv', 'w', encoding='utf-8') as fp:
        csv_writer = csv.writer(fp)
        csv_writer.writerow(('Leading paper','Delta D', 'Citation'))
        for pid, delta_D in tqdm(sorted_pid2topic_delta_D):
            print(pid, get_paper_title(pid))
            csv_writer.writerow((get_paper_title(pid), delta_D, str(get_paper_citation(pid))))


# In[58]:


if __name__ == "__main__":
    tpids = json.load(open('covid_high_citation_pids.json', 'r'))
    tpids = ['470780090',
             '187139104',
             '242975836',
             '193690222',
             '200599618',
             '219704643',
             '76205213',
             '477291171',
             '298754821',
             '496604792'
            ]
    main(tpids)

