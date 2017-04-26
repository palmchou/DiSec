#!/usr/bin/python
# -*- coding:utf-8 -*-

import time, Queue
from multiprocessing.managers import BaseManager
import re
import urllib
import urllib2
import os
import json
import socket
import logging
from urllib import quote


def getHtml(keyword, start):
    req_header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 360SE'}
    url = 'http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result' \
          '&queryWord=' + quote(keyword) + '&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0' \
                                    '&word=' + quote(keyword) + '&s=0&se=&tab=&width=&height=&face=1&istype=2&qc=&nc=&fr=%26fr%3D&pn=' + str(
        start) + '&rn=60&1433936881420='
    # url='http://cn.bing.com/images/async?q='+keyword+'&async=content&first='+str(start)+'&count=35&IID=images.1&IG=06fd0edefcfa4c9a8be876677b2cd340&CW=1693&CH=312&dgsrr=false&qft=+filterui:face-face&form=R5IR30'
    req = urllib2.Request(url, None, req_header)
    response = urllib2.urlopen(req)
    html = response.read()
    time.sleep(0.5)
    response.close()
    return html


def decoder(url_src):
    dict = {'w': 'a', 'k': 'b', 'v': 'c', '1': 'd', 'j': 'e',
            'u': 'f', '2': 'g', 'i': 'h', 't': 'i', '3': 'j',
            'h': 'k', 's': 'l', '4': 'm', 'g': 'n', '5': 'o',
            'r': 'p', 'q': 'q', '6': 'r', 'f': 's', 'p': 't',
            '7': 'u', 'e': 'v', 'o': 'w', '8': '1', 'd': '2',
            'n': '3', '9': '4', 'c': '5', 'm': '6', '0': '7',
            'b': '8', 'l': '9', 'a': '0'
            }

    url_src = url_src.replace('_z2C$q', ':')
    url_src = url_src.replace('_z&e3B', '.')
    url_src = url_src.replace('AzdH3F', '/')
    url_list = []
    for i in range(0, len(url_src)):
        key = url_src[i]
        if dict.has_key(key):
            t = dict[key]
        else:
            t = key
        url_list.append(t)
    url = ''.join(url_list)
    return url


def getImg(html, start, imgpath, Info):
    cot = start
    t1 = 'source: '
    t2 = ' dst '
    t3 = ' success'
    t4 = ' fail'
    t5 = ' exist'


    reg = r'objURL":"(.+?)",'
    imgre = re.compile(reg)
    imglist = imgre.findall(html)

    success = 0

    for url in imglist:
        imgurl = decoder(url)
        tt = imgurl.split('/')
        image_name = tt[-1]
        type = image_name.split('.')[-1]
        if type != 'jpg' and type != 'png' and type != 'JPG' and type != 'PNG':
            type += '.unknow'
        name = imgpath + '/' + str(cot) + '.' + type
        cot += 1
        if os.path.exists(name):
            str_print = t1 + imgurl + t2 + name + t5
            print str_print
            print >> Info, str_print
            continue

        try:
            urllib.urlretrieve(imgurl, name)
            tag = 1
        except:
            tag = 0
            pass
        if (tag == 1):
            str_print = t1 + imgurl + t2 + name + t3
            success += 1
        else:
            str_print = t1 + imgurl + t2 + name + t4
        print str_print
        print >> Info, str_print
    return len(imglist), success


class QueueManager(BaseManager):
    pass

QueueManager.register('baidu_queue')
QueueManager.register('feedback_queue')

settings = json.load(open("./local_settings.json"))

server_address = settings["server_address"]
auth_key = settings["auth_key"]
port = settings['port']
manager = QueueManager(address=(server_address, port), authkey=auth_key)
manager.connect()

keyword_queue = manager.baidu_queue()
feedback_queue = manager.feedback_queue()

socket.setdefaulttimeout(10)

step = 60
end_at = settings['end_at']
path = str(settings["path"]) + "/baidu"
# 保存图片路径
img_path = path + "/img"
# 保存爬取图片的信息路径
txt_path = path + "/log"

while True:
    try:
        kw = keyword_queue.get(timeout=2)
        fb_info = {'se': 'baidu', 'id': kw['id'], 'last_acquired': kw['last_acquired'], 'succ_count': 0}
        # let the sever notice this keyword is on working
        feedback_queue.put(fb_info)
        keywords = kw['words'].encode('utf-8')
        last_acqu = kw['last_acquired']
        last_reported_acqu = last_acqu
        start_at = last_acqu + 1
        success_count = 0
        print 'Working on keyword:', keywords, ', starting from', start_at

        # 图像保存地址imgnewpath
        imgnewpath = img_path + '/' + kw['classification'].encode('utf-8') + '/' + keywords
        if not os.path.isdir(imgnewpath):
            os.makedirs(imgnewpath)
            # 信息保存地址txtnewpath
        txtnewpath = txt_path + '/' + kw['classification'].encode('utf-8') + '/' + keywords
        if not os.path.isdir(txtnewpath):
            os.makedirs(txtnewpath)

        for start in range(start_at, end_at, step):
            print keywords, 'start from ', str(start), ' to ', str(start + step - 1)
            html = getHtml(keywords, start)  # 获取源代码
            savename = txtnewpath + '/' + str(start) + '.txt'
            print savename
            Info = open(savename, 'w')
            (acqu_cot, succ_cot) =  getImg(html, start, imgnewpath, Info)  # 获取图像
            Info.close()
            success_count += succ_cot
            last_acqu += acqu_cot
            if (last_acqu - last_reported_acqu) >= 60:
                fb_info['last_acquired'] = last_acqu
                fb_info['succ_count'] = success_count
                feedback_queue.put(fb_info)
                last_reported_acqu = last_acqu
                success_count = 0
            if acqu_cot < step:
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
    except StandardError, e:
        logging.exception(e)
        print "Error Exit"
        exit(1)
print 'exit'
