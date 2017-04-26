#!/usr/bin/python
# -*- coding: utf-8 -*-
import Queue
from multiprocessing.managers import BaseManager
import socket
import time
import httplib
from bs4 import BeautifulSoup
from urlparse import urlparse
from urllib import urlretrieve
from urllib import quote
import os
import json


def get_img_keyword(keyword, start, file_object, dst):
    conn = httplib.HTTPSConnection('www.google.com.hk', 443)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        # 'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'referer': 'https://www.google.com.hk/'
    }
    req_url = str("https://www.google.com.hk/search?q=" + quote(keyword) +
                 "&tbs=itp:face&newwindow=1&safe=active&hl=en&biw=1920&bih=955&site=imghp&tbm=isch&ijn=3"
                 "&ei=azx1VYvkBqGzmwXs04LoDg&start=" + str(start))
    conn.request("GET", req_url, headers=headers)

    r1 = conn.getresponse()
    htmltext = r1.read()
    time.sleep(0.5)
    conn.close()

    img_urls = []
    formatted_images = []

    soup = BeautifulSoup(htmltext)
    results = soup.findAll("a")

    cot = start
    t1 = 'source: '
    t2 = ' dst '
    t3 = ' success'
    t4 = ' fail'
    t5 = ' exist'

    succ_cot = 0

    for r in results:
        try:
            if "imgres?imgurl" in r['href']:
                img_urls.append(r['href'])
        except:
            a = 0

    for im in img_urls:
        refer_url = urlparse(str(im))
        image_f = refer_url.query.split("&")[0].replace("imgurl=", "")
        formatted_images.append(image_f)

        tt = image_f.split('/')
        image_name = tt[-1]
        # name = dst + '/' + date + '_' + image_name

        type = image_name.split('.')[-1]
        if type != 'jpg' and type != 'png' and type != 'JPG' and type != 'PNG':
            type += '.unknow'
        name = dst + '/' + str(cot) + '.' + type

        # type = image_name.split('.')[-1]
        # name = dst + '/' + image_name[0:len(image_name)-len(type)-1] + '_' + str(cot) + '.' + type

        if os.path.exists(name):
            str_print = t1 + image_f + t2 + name + t5
            print str_print
            print >> file_object, str_print
            continue

        try:
            urlretrieve(image_f, name)
            succ_cot += 1
            tag = 1
        except:
            tag = 0
            pass

        if (tag == 1):
            str_print = t1 + image_f + t2 + name + t3
        else:
            str_print = t1 + image_f + t2 + name + t4

        print str_print
        print >> file_object, str_print
        cot += 1

    return (formatted_images, succ_cot)


class QueueManager(BaseManager):
    pass

QueueManager.register('google_queue')
QueueManager.register('feedback_queue')

settings = json.load(open("./local_settings.json"))
socket.setdefaulttimeout(10)

server_address = settings["server_address"]
auth_key = settings["auth_key"]
port = settings['port']
manager = QueueManager(address=(server_address, port), authkey=auth_key)
manager.connect()

keyword_queue = manager.google_queue()
feedback_queue = manager.feedback_queue()

end_at = settings['end_at']
step = 21
path = str(settings["path"]) + "/google"
# 保存图片路径
dst = path + "/img"
# 保存爬取图片的信息路径
txt_dst = path + "/log"

i = 0
while True:
    try:
        kw = keyword_queue.get(timeout=2)
        fb_info = {'se': 'google', 'id': kw['id'], 'last_acquired': kw['last_acquired'], 'succ_count': 0}
        # let the sever notice this keyword is on working
        feedback_queue.put(fb_info)
        keywords = kw['words'].encode('utf-8')
        last_acqu = kw['last_acquired']
        last_reported_acqu = last_acqu
        start_at = last_acqu + 1
        success_count = 0
        print 'Working on keyword:', keywords, ', starting from', start_at
        # 以关键字命名文件夹（存放爬取的图片）
        save_dst = dst + '/' + keywords
        save_dst = dst + '/' + kw['classification'].encode('utf-8') + '/' + keywords
        if not os.path.exists(save_dst):
            os.makedirs(save_dst)

        # 以关键字命名文件夹（存放爬取的图片的txt信息）
        save_txt_dst = txt_dst + '/' + kw['classification'].encode('utf-8') + '/' + keywords
        if not os.path.exists(save_txt_dst):
            os.makedirs(save_txt_dst)

        for start in range(start_at, end_at + step, step):
            last_acqu = start - 1
            link_txt = save_txt_dst + '/' + str(start) + '.txt'

            if os.path.exists(link_txt):
                file_tmp = open(link_txt, 'rU')
                count = len(file_tmp.readlines())
                file_tmp.close()
            else:
                count = 0

            if count == step:
                print link_txt, 'was finished, go to next one'
                continue

            # 保存某一个start开始的step个图片的信息（原链接，保存本地路径，是否爬取成功）
            file_object = open(link_txt, 'w')

            print keywords, 'start from ', str(start), ' to ', str(start + step - 1)
            # 爬取某一个start开始的step个图片
            (ret, succ_cot) = get_img_keyword(keywords, start, file_object, save_dst)
            file_object.close()
            success_count += succ_cot
            last_acqu += len(ret)
            if last_acqu - last_reported_acqu >= 60:
                fb_info['last_acquired'] = last_acqu
                fb_info['succ_count'] = success_count
                feedback_queue.put(fb_info)
                last_reported_acqu = last_acqu
                success_count = 0

            # 当爬取完某一个关键字后，跳出循环到下一个关键字
            if len(ret) < step:
                print 'it is finished for the keywords (web cralwer): ', keywords
                fb_info['last_acquired'] = end_at
                feedback_queue.put(fb_info)
                last_reported_acqu = end_at
                break
            if last_acqu >= end_at:
                print 'it is finished for the keywords (web cralwer): ', keywords
                fb_info['last_acquired'] = end_at
                feedback_queue.put(fb_info)
                last_reported_acqu = end_at
                break
    except Queue.Empty:
        print 'task finished'
        break
print 'exit'
