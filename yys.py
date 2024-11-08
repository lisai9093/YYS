import cv2,time,random,os,datetime
import os,sys,traceback
import numpy as np
import mss
import action
from multiprocessing import Process, Queue
#from ui import form,window,app
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
)
from PyQt6.QtCore import QThread,pyqtSignal,QProcess,QMutex,Qt

#global variables
last_click=None
mutex = QMutex()

#以上启动，载入设置
##########################################################
def select_mode():
    global start
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    textBrowser.append("运行时间：{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    print (datetime.datetime.now())

    textBrowser.append('''\n菜单：  按下CTRL+C停止，0退出
        1 结界突破
        2 御魂(司机)
        3 御魂(打手)
        4 御魂/御灵/契灵探查(单刷)
        5 探索(司机)
        6 探索(打手)
        7 探索(单刷)
        8 百鬼夜行
        9 自动斗技
        10 当前活动
        11 厕纸抽卡
        12 秘境召唤
        13 妖气封印/秘闻
        14 契灵boss（单刷）
        15 Debug模式
        ''')
    action.alarm(1)

    mode = [0, tupo, yuhun, yuhun2, yuhundanren,\
            gouliang, gouliang2, gouliang3,\
            baigui, douji, huodong,\
            chouka, mijing, yaoqi,\
            qilingdanren, debug]

    while isRunning[current_index]:
        try:
            raw=input("选择功能模式：")
            index=int(raw)
            if index<0:
                raise Exception('数字超出范围')
            command = mode[index]
        except ValueError:
            textBrowser.append('请输入数字')
            continue
        except:
            textBrowser.append('数字超出范围')
            continue
        else:
            break

    if index==0:
        action.reset_resolution()
        quit()
    else:
        start = time.time()
        try:
            command()
        except KeyboardInterrupt:
            textBrowser.append('已停止！')
            return

##########################################################
def cishu_input():
    while isRunning[current_index]:
        try:
            raw=input("输入挑战次数（1-9999）：")
            cishu=int(raw)
            if cishu<1 or cishu>9999:
                raise Exception('数字超出范围（1-9999）')
        except ValueError:
            textBrowser.append('请输入数字')
            continue
        except:
            textBrowser.append('数字超出范围（1-9999）')
            continue
        else:
            break
    return cishu

#结节突破
def tupo(textBrowser,current_index):
    last_click=''
    cishu = 0
    refresh=0
    liaotu=None
    while isRunning[current_index]:   #直到取消，或者出错
        #print(isRunning)
        #if not isRunning:
        #    break
        #截屏
        #im = np.array(mss.mss().grab(monitor))
        #screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
        screen=action.screenshot(current_index)
        #cv2.imshow("Image", screen)
        #cv2.waitKey(0)

        #寮突破判断
        if liaotu==None:
            want = imgs['liaotupo']
            size = want[0].shape
            h, w , ___ = size
            pts = action.locate(screen,want,0)
            if not len(pts) == 0:
                liaotu=True
                textBrowser.append('寮突破')

            want = imgs['gerentupo']
            size = want[0].shape
            h, w , ___ = size
            pts = action.locate(screen,want,0)
            if not len(pts) == 0:
                liaotu=False
                textBrowser.append('个人突破')
                cishu_max[current_index]=30

        if liaotu==False:
            if cishu >= 31:
                textBrowser.append('进攻次数上限: '+str(cishu)+'/'+str(cishu_max[current_index]))
                return

        #奖励
        for i in ['jujue','queding',\
                  'shibai','ying','jiangli','jixu',\
                  'jingong','jingong2','jingong3',\
                  'lingxunzhang','lingxunzhang2','lingxunzhang4',\
                  'shuaxin','zhunbei']:
            want=imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target=screen
            pts=action.locate(target,want,0)
            if not len(pts)==0:
                if last_click==i:
                    if ('jingong' in i or 'lingxunzhang' in i) and liaotu:
                        refresh=refresh+1
                        textBrowser.append('进攻CD，暂停5分钟')
                        t=60*5
                        if sleep_fast(t,current_index): return
                        last_click=''
                        continue
                    else:
                        refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                if refresh>6:
                    textBrowser.append('进攻次数上限')
                    return
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                t = random.randint(50,100) / 100
                if i == 'shibai':
                    if cishu>0:
                        cishu = cishu - 1
                    textBrowser.append('进攻总次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t = random.randint(50,100) / 100
                elif 'jingong' in i:
                    if refresh==0:
                        cishu=cishu+1
                    textBrowser.append('进攻总次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t = random.randint(500,800) / 100
                textBrowser.append(i)
                if sleep_fast(t,current_index): return
                break

########################################################
#御魂司机
def yuhun(textBrowser,current_index):
    last_click=''
    cishu=0
    refresh=0
    
    while isRunning[current_index]:
        #截屏
        screen=action.screenshot(current_index)
        
        #textBrowser.append('screen shot ok',time.ctime())
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足')
            return

        #自动点击通关结束后的页面
        for i in ['jujue','tiaozhan','tiaozhan2',\
                  'moren','queding','querenyuhun','ying',\
                  'jiangli','jiangli2',\
                  'jixu','shibai']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                elif i=='querenyuhun':
                    refresh=refresh+2
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                if i == 'tiaozhan' or i=='tiaozhan2':
                    if refresh==0:
                        cishu=cishu+1
                    textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t=random.randint(500,750)/100
                else:
                    textBrowser.append(i)
                    t = random.randint(50,100) / 100
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                if sleep_fast(t,current_index): return
                break
    
########################################################
#御魂打手
def yuhun2(textBrowser,current_index):
    last_click=''
    cishu=0
    refresh=0
    while isRunning[current_index]:
        #截屏
        screen=action.screenshot(current_index)
        
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足')
            return

        #如果队友推出则自己也退出
        want = imgs['tiaozhanhuise']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('队友已退出')
            want = imgs['likaiduiwu']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return
                
        
        #自动点击通关结束后的页面
        for i in ['jujue','moren','queding','querenyuhun',\
                  'ying','jiangli','jiangli2','jixu',\
                  'jieshou2','jieshou','shibai']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                elif i=='querenyuhun':
                    refresh=refresh+2
                else:
                    refresh=0
                
                #textBrowser.append('重复次数：',refresh)
                if refresh>6:
                    textBrowser.append('进攻次数上限')
                    return
                elif refresh==0 and 'jiangli' in i and not last_click=='querenyuhun':
                    #textBrowser.append('last',last_click)
                    cishu=cishu+1
                    textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                if 'jieshou' in i:
                    a,b=pts[0]
                    if a<100:
                        break
                    t = random.randint(150,300) / 100
                else:
                    t = random.randint(15,30) / 100
                textBrowser.append(i)
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                last_click=i
                if sleep_fast(t,current_index): return
                break
            

########################################################
#御魂单人
def yuhundanren(textBrowser,current_index):
    last_click=''
    cishu=0
    refresh=0
    
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)
        
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足')
            return

        for i in ['jujue','querenyuhun','ying','jiangli','jiangli2','jixu','zhunbei',\
                  'tiaozhan','tiaozhan2','tiaozhan3','queding','tancha','shibai']:
            want=imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target=screen
            pts=action.locate(target,want,0)
            if not len(pts)==0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                textBrowser.append(i)
                if i == 'tiaozhan' or i=='tiaozhan2' or i=='tiaozhan3' or i=='tancha':
                    if refresh==0:
                        cishu=cishu+1
                    textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t = random.randint(500,800) / 100
                else:
                    t = random.randint(15,30) / 100
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                if sleep_fast(t,current_index): return
                break

########################################################
#探索司机
def gouliang(textBrowser,current_index):
    last_click=''
    cishu=0
    refresh=0
    
    boss_done=False
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)

        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足 ')
            return

        want = imgs['queren']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('确认退出')
            try:
                queding = pts[1]
            except:
                queding = pts[0]
            xy = action.cheat(queding, w, h)
            action.touch(xy,current_index)
            t = random.randint(15,30) / 100
            if sleep_fast(t,current_index): return

        
        #设定目标，开始查找
        #进入后
        want=imgs['guding']

        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('正在地图中')
            for i in ['boss', 'jian']:
                want = imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    if i=='boss':
                        boss_done=True
                        i='jian'
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #textBrowser.append('重复次数：',refresh)
                    if refresh>6:
                        textBrowser.append('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h)
                    action.touch(xy,current_index)
                    time.sleep(0.5)
                    break

            if len(pts)==0:
                if not boss_done:
                    textBrowser.append('向右走')
                    right = (854, 420)
                    xy = action.cheat(right, 10, 10)
                    action.touch(xy,current_index)
                    t = random.randint(100,300) / 100
                    if sleep_fast(t,current_index): return
                    continue
                else:
                    i='tuichu'
                    want = imgs[i]
                    size = want[0].shape
                    h, w , ___ = size
                    #x1,x2 = upleft, (965, 522)
                    #target = action.cut(screen, x1, x2)
                    target = screen
                    pts = action.locate(target,want,0)
                    if not len(pts) == 0:
                        textBrowser.append('退出中'+i)
                        try:
                            queding = pts[1]
                        except:
                            queding = pts[0]
                        xy = action.cheat(queding, w, h)
                        action.touch(xy,current_index)
                        t = random.randint(50,80) / 100
                        if sleep_fast(t,current_index): return
                continue

        for i in ['jujue','queding','ying','querenyuhun',\
                  'jiangli','jixu',\
                  'tiaozhan','ditu']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                if i=='tiaozhan' and refresh==0:
                    boss_done=False
                    cishu=cishu+1
                    textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                #textBrowser.append('重复次数：',refresh)
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return

                textBrowser.append(i)
                xy = action.cheat(pts[0], w, h )
                action.touch(xy,current_index)
                if i=='queding':
                    t = random.randint(150,200) / 100
                else:
                    t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return
                break

########################################################
#探索打手
def gouliang2(textBrowser,current_index):
    last_click=''
    refresh=0
    cishu=0
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)
        
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足 ')
            return
        
        #进入后
        want = imgs['guding']
        pts = action.locate(screen,want,0)
        if not len(pts) == 0:
            textBrowser.append('正在地图中')
            
            want = imgs['xiao']
            pts = action.locate(screen,want,0)
            
            if not len(pts) == 0:
                textBrowser.append('组队状态中')
            else:
                textBrowser.append('退出重新组队')
                
                for i in ['queren', 'queren2','tuichu']:
                    want = imgs[i]
                    size = want[0].shape
                    h, w , ___ = size
                    pts = action.locate(screen,want,0)
                    
                    if not len(pts) == 0:
                        if last_click==i:
                            refresh=refresh+1
                        else:
                            refresh=0
                        last_click=i
                        #textBrowser.append('重复次数：',refresh)
                        if refresh>6:
                            textBrowser.append('进攻次数上限')
                            return
                        
                        textBrowser.append('退出中'+i)
                        try:
                            queding = pts[1]
                        except:
                            queding = pts[0]
                        xy = action.cheat(queding, w, h)
                        action.touch(xy,current_index)
                        t = random.randint(50,80) / 100
                        if sleep_fast(t,current_index): return
                        break
                continue

        for i in ['jujue','jieshou','querenyuhun','ying',\
                  'jiangli','jixu']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                if i=='jieshou':
                    a,b=pts[0]
                    if a<100:
                        break
                    if refresh==0:
                        cishu=cishu+1
                        textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                #textBrowser.append('重复次数：',refresh)
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                textBrowser.append(i)
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                if i=='jieshou' or i=='jieshou1':
                    t = random.randint(150,300) / 100
                else:
                    t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return
                break
            
########################################################
#探索单人
def gouliang3(textBrowser,current_index):
    last_click=''
    cishu=0
    refresh=0
    
    boss_done=False
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)
        
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足')
            return

        want = imgs['queren']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        #x1,x2 = upleft, (965, 522)
        #target = action.cut(screen, x1, x2)
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('确认退出')
            try:
                queding = pts[1]
            except:
                queding = pts[0]
            xy = action.cheat(queding, w, h)
            action.touch(xy,current_index)
            t = random.randint(15,30) / 100
            if sleep_fast(t,current_index): return

        
        #设定目标，开始查找
        #进入后
        want=imgs['guding']

        pts = action.locate(screen,want,0)
        if not len(pts) == 0:
            textBrowser.append('正在地图中')
            for i in ['boss', 'jian']:
                want = imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    if i=='boss':
                        boss_done=True
                        i='jian'
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #textBrowser.append('重复次数：',refresh)
                    if refresh>6:
                        textBrowser.append('进攻次数上限')
                        return
                    
                    textBrowser.append('点击小怪'+i)
                    xy = action.cheat(pts[0], w, h)
                    action.touch(xy,current_index)
                    time.sleep(0.5)
                    break

            if len(pts)==0:
                if not boss_done:
                    textBrowser.append('向右走')
                    right = (854, 420)
                    xy = action.cheat(right, 10, 10)
                    action.touch(xy,current_index)
                    t = random.randint(100,300) / 100
                    if sleep_fast(t,current_index): return
                    continue
                else:
                    i='tuichu'
                    want = imgs[i]
                    size = want[0].shape
                    h, w , ___ = size
                    pts = action.locate(screen,want,0)
                    if not len(pts) == 0:
                        textBrowser.append('退出中'+i)
                        try:
                            queding = pts[1]
                        except:
                            queding = pts[0]
                        xy = action.cheat(queding, w, h)
                        action.touch(xy,current_index)
                        t = random.randint(50,80) / 100
                        if sleep_fast(t,current_index): return
                continue

        for i in ['jujue','querenyuhun',\
                  'tansuo','ying','jiangli','jixu','c28','ditu']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                if refresh==0 and i=='tansuo':
                    cishu=cishu+1
                    textBrowser.append('\n探索次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                textBrowser.append(i)
                xy = action.cheat(pts[0], w, h )
                action.touch(xy,current_index)
                t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return
                break

########################################################
#百鬼
def baigui(textBrowser,current_index):
    last_click=''
    refresh=0
    cishu=0
    
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)

        #设定目标，开始查找
        #进入后
        for i in ['baigui','gailv','douzihuoqu','miaozhun','baiguijieshu']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                refresh=0
                textBrowser.append('点击'+i)
                xy = action.cheat(pts[0], w, h )
                action.touch(xy,current_index)
                t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return
                continue

        want=imgs['inbaigui']
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            #textBrowser.append('正在百鬼中')
            want = imgs['blank']
            target = screen
            pts = action.locate(target,want,0)
            if len(pts) == 0:
                refresh=0
                #小怪出现！
                textBrowser.append('点击小怪')
                pts2 = (640, 450)
                xy = action.cheat(pts2, 100, 80)
                action.touch(xy,current_index)
                time.sleep(0.5)
                continue

        i='jinru'
        want = imgs[i]
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            if last_click==i:
                refresh=refresh+1
            else:
                refresh=0
                last_click=i
            if refresh==0:
                cishu=cishu+1
            if refresh>6 or cishu>cishu_max[current_index]:
                textBrowser.append('进攻次数上限')
                return
            textBrowser.append('进入百鬼:'+str(cishu)+'/'+str(cishu_max[current_index]))
            xy = action.cheat(pts[0], w, h-10 )
            action.touch(xy,current_index)
            t = random.randint(10,20) / 100
            if sleep_fast(t,current_index): return

        i='kaishi'
        want = imgs[i]
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            refresh=0
            textBrowser.append('选择押注界面')
            i='ya'
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts2 = action.locate(target,want,0)
            if not len(pts2) == 0:
                textBrowser.append('点击开始: ',pts[0])
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return
            else:
                #选择押注
                index=random.randint(0,2)
                pts2 = (300+index*340, 500)
                textBrowser.append('选择押注: '+str(index))
                
                xy = action.cheat(pts2, w, h-10 )
                action.touch(xy,current_index)
                t = random.randint(50,100) / 100
                if sleep_fast(t,current_index): return

                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                t = random.randint(15,30) / 100
                if sleep_fast(t,current_index): return


########################################################
#斗技
def douji(textBrowser,current_index):
    last_click=''
    doujipaidui=0
    refresh=0
    cishu=0
    
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)

        for i in ['jujue','shoudong','zidong','queren',\
                  'douji','douji2','douji3','douji4','doujilianxi',\
                  'doujiqueren','doujiend','ying','jixu',\
                  'zhunbei','zhunbei2',\
                  'doujiquxiao']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                #textBrowser.append(i)
                if i in ['douji','douji2','douji3','douji4']:
                    i='douji'
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                if refresh==0 and i=='douji':
                    cishu=cishu+1
                    textBrowser.append('斗技次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t = random.randint(150,300) / 100
                elif i=='doujiquxiao':
                    refresh=0
                    doujipaidui=doujipaidui+1
                    textBrowser.append('斗技搜索:',doujipaidui)
                    if doujipaidui>5:
                        doujipaidui=0
                        textBrowser.append('取消搜索')
                        cishu=cishu-1
                        t = random.randint(15,30) / 100
                    else:
                        break
                else:
                    textBrowser.append(i)
                    t = random.randint(50,100) / 100
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                t = random.randint(50,100) / 100
                if sleep_fast(t,current_index): return
                break

########################################################
#当前活动
def huodong(textBrowser,current_index):
    last_click=''
    cishu=0
    
    refresh=0
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)

        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足 ')
            return
        
        for i in ['jujue','querenyuhun','queding','hdend',\
                  'hdtiaozhan','hdtiaozhan2','hdtiaozhan3','ying','hdsousuo','zhunbei',\
                  'shibai','jixu','liaotianguanbi']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if i=='hdjiacheng':
                    refresh=0
                elif last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                textBrowser.append(i)
                if refresh>6:
                    textBrowser.append('进攻次数上限')
                    return

                t = 1
                if 'hdtiaozhan' in i:
                    if refresh==0:
                        cishu=cishu+1
                        textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t=5
                if i=='hdsousuo':
                    t=5
                if i=='hdend' and False:
                    if refresh==0:
                        textBrowser.append('疲劳度满，休息10分钟')
                        t = 10*60
                        if sleep_fast(t,current_index): return
                xy = action.cheat(pts[0], w, h)
                action.touch(xy,current_index)
                #textBrowser.append('等待时间：',t)
                if sleep_fast(t,current_index): return

##########################################################
#合成结界卡
def card(textBrowser,current_index):
    last_click=''
    refresh=0
    while isRunning[current_index]:
        #截屏
        screen=action.screenshot(current_index)
        
        for i in ['taiyin2','sanshinei','taiyin3']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                if refresh>6:
                    textBrowser.append('进攻次数上限')
                    return
                
                textBrowser.append('结界卡*'+i)
                xy = action.cheat(pts[0], w/2, h-10)
                action.touch(xy,current_index)
                break
        if len(pts) == 0:
                textBrowser.append('结界卡不足')
                return
        

        for i in range(2):
            #截屏
            im = np.array(mss.mss().grab(monitor))
            screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

            want = imgs['taiyin']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if len(pts) == 0:
                textBrowser.append('结界卡不足')
                return
            else:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click='taiyin'
                #textBrowser.append('重复次数：',refresh)
                if refresh>6:
                    textBrowser.append('进攻次数上限')
                    return
                
                textBrowser.append('结界卡'+i)
                xy = action.cheat(pts[0], w/2, h-10 )
                action.touch(xy,current_index)

        #截屏
        screen=action.screenshot(current_index)

        want = imgs['hecheng']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            if last_click==i:
                refresh=refresh+1
            else:
                refresh=0
            last_click='hecheng'
            #textBrowser.append('重复次数：',refresh)
            if refresh>6:
                textBrowser.append('进攻次数上限')
                return
            
            textBrowser.append('合成中。。。')
            xy = action.cheat(pts[0], w, h-10 )
            action.touch(xy,current_index)

        time.sleep(1)

##########################################################
#抽卡
def chouka(textBrowser,current_index):
    last_click=None
    cishu=0
    
    while isRunning[current_index]:
        #截屏
        screen=action.screenshot(current_index)
        
        want = imgs['zaicizhaohuan']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            if cishu>cishu_max[current_index]:
                textBrowser.append('次数上限')
                return
            cishu=cishu+1
            textBrowser.append('抽卡中：'+str(cishu)+'/'+str(cishu_max[current_index]))
            xy = action.cheat(pts[0], w, h-10 )
            action.touch(xy,current_index)
            t = random.randint(10,30) / 100
            if sleep_fast(t,current_index): return

##########################################################
#蓝蛋升级
def shengxing(textBrowser,current_index):
    last_click=''
    cishu=0
    refresh=0
    while isRunning[current_index]:
        #截屏
        screen=action.screenshot(current_index)
            
        for i in ['jineng','jixushengxing',\
                  'jixuyucheng','querenshengxing']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                if refresh>6:
                    textBrowser.append('进攻次数上限')
                    return
                
                textBrowser.append('升级中。。。'+i)
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                if i=='querenshengxing':
                    if refresh==0:
                        cishu=cishu+1
                    textBrowser.append('升级个数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t = random.randint(250,350) / 100
                else:
                    t = random.randint(20,100) / 100
                    
                if sleep_fast(t,current_index): return
                
##########################################################
#秘境召唤
def mijing(textBrowser,current_index):
    last_click=''
    refresh=0
    while isRunning[current_index]:
        #截屏
        screen=action.screenshot(current_index)
        
        #检测聊天界面
        want = imgs['liaotianguanbi']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            #textBrowser.append('搜索秘境车中。。。')

            for i in ['jujue','mijingzhaohuan','mijingzhaohuan2']:
                want = imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #textBrowser.append('重复次数：',refresh)
                    if refresh>6:
                        textBrowser.append('进攻次数上限')
                        return
                    
                    textBrowser.append(i)
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,current_index)
                    #t = random.randint(10,100) / 100
                    #if sleep_fast(t,current_index): return
                    break
        else:
            for i in ['jujue','canjia','liaotian']:
                want = imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #textBrowser.append('重复次数：',refresh)
                    if refresh>6:
                        textBrowser.append('进攻次数上限')
                        return
                    
                    if i=='canjia':
                        textBrowser.append('加入秘境召唤！'+i)
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,current_index)
                    t = random.randint(10,30) / 100
                    if sleep_fast(t,current_index): return
                    break

########################################################
#妖气封印和秘闻
def yaoqi(textBrowser,current_index):
    global isRunning,cishu_max
    last_click=''
    cishu=0
    refresh=0
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)
        
        #委派任务
        for i in ['jujue','jiangli','jixu','zhunbei',\
                  'shibai','zidongpipei','zudui2',\
                  'ying','tiaozhan3','tiaozhan4']:
            want = imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                if i=='zidongpipei' or i=='tiaozhan3' or i=='tiaozhan4':
                    if refresh==0:
                        cishu=cishu+1
                    textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t=100/100
                elif i=='shibai':
                    textBrowser.append('自动结束')
                    return
                else:
                    textBrowser.append(i)
                    t = random.randint(30,80) / 100
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                if sleep_fast(t,current_index): return
                break
        
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足')
            return

########################################################
#契灵单人
def qilingdanren(textBrowser,current_index):
    last_click=''
    cishu=0
    
    refresh=0
    while isRunning[current_index]:   #直到取消，或者出错
        #截屏
        screen=action.screenshot(current_index)
        
        #体力不足
        want = imgs['notili']
        size = want[0].shape
        h, w , ___ = size
        target = screen
        pts = action.locate(target,want,0)
        if not len(pts) == 0:
            textBrowser.append('体力不足')
            return

        for i in ['jujue','ying','jiangli','jixu','queding',\
                  'qiling1','mingqi','queren3',\
                  'tiaozhan5','shibai','xiaozhiren']:
            want=imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target=screen
            pts=action.locate(target,want,0)
            if not len(pts)==0:
                if last_click==i:
                    refresh=refresh+1
                else:
                    refresh=0
                last_click=i
                #textBrowser.append('重复次数：',refresh)
                textBrowser.append(i)
                if i=='tancha' or i=='tiaozhan5':
                    if refresh==0:
                        cishu=cishu+1
                    textBrowser.append('挑战次数：'+str(cishu)+'/'+str(cishu_max[current_index]))
                    t = random.randint(50,150) / 100
                elif i=='queren3':
                    t = random.randint(350,450) / 100
                else:
                    t = random.randint(15,30) / 100
                if refresh>6 or cishu>cishu_max[current_index]:
                    textBrowser.append('进攻次数上限')
                    return
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,current_index)
                if sleep_fast(t,current_index): return
                break
##################################################################
def debug(textBrowser,current_index):
    from PyQt6.QtGui import QPixmap, QImage
    from PyQt6.QtWidgets import QMessageBox
    #截屏
    #screen=action_adb.screenshot()
    screen=action.screenshot(current_index)
    textBrowser.append('screen: '+str(screen.shape[1])+' '+str(screen.shape[0]))
    screen = screen[0:screen.shape[0], 0:screen.shape[1]]
    h, w, ch = screen.shape
    bytesPerLine = ch * w
    image = QImage(screen.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)

    # Create a label to display the image
    label = QLabel()
    label.setPixmap(QPixmap.fromImage(image))

    msg_box = QMessageBox()
    msg_box.setWindowTitle("Image Popup")
    # Set the label as the central widget of the main window
    layout = QVBoxLayout()
    layout.addWidget(label)
    msg_box.setLayout(layout)
    msg_box.exec()
    #time.sleep(3)
    return
####################################################
def sleep_fast(t=0,current_index=None):
    #return value indicates interrupt happens
    if current_index==None:
        #None index
        time.sleep(t)
    else:
        for t_count in range(round(t/0.1)):
            if not isRunning[current_index]:
                return True
            time.sleep(0.1)
    return False
####################################################
#开始/停止按键
def start_stop(window):
    global cishu_max,t,isRunning
    #find current tab index
    current_index = window.tabWidget.currentIndex()
    #change outputs only for current tab
    textBrowser=window.tab[current_index].textBrowser
    listWidget=window.tab[current_index].listWidget
    lineEdit=window.tab[current_index].lineEdit
    pushButton_start=window.tab[current_index].pushButton_start
    pushButton_restart=window.tab[current_index].pushButton_restart

    if isRunning[current_index]:
        #stop running job
        pushButton_start.setText('开始')
        pushButton_start.setEnabled(False)
        mutex.lock()  # Acquire the lock
        isRunning[current_index]=False
        t[current_index].quit()
        if not t[current_index].wait(5000):  # Wait for 5 seconds
            textBrowser.append('已强制停止！')
            t[current_index].terminate()
        mutex.unlock()  # Release the lock
        pushButton_start.setEnabled(True)
        pushButton_restart.setEnabled(True)
    elif listWidget.selectedItems() and not isRunning[current_index]:
        #已选择脚本，开始运行
        textBrowser.append(listWidget.currentItem().text())
        index=listWidget.currentRow()+1
        command = mode[index]
        #设置次数
        if not lineEdit.text() == 'inf':
            try:
                mutex.lock()  # Acquire the lock
                cishu_max[current_index]=int(lineEdit.text())
                mutex.unlock()  # Release the lock
                if cishu_max[current_index]<1 or cishu_max[current_index]>9999:
                    raise Exception('数字超出范围（1-9999）')
            except ValueError:
                textBrowser.append('请输入数字')
                pushButton_start.setText('开始')
                return
            except:
                textBrowser.append('数字超出范围（1-9999）')
                pushButton_start.setText('开始')
                return
        else:
            mutex.lock()  # Acquire the lock
            cishu_max[current_index]=float('inf')
            mutex.unlock()  # Release the lock
            
        if index==15:
            #debug has to be on main thread
            command(textBrowser,current_index)
        else:
            #p = Process(target=command)
            #p.start()
            mutex.lock()  # Acquire the lock
            t[current_index]=MyThread(command,textBrowser,current_index)
            t[current_index].finished.connect(thread_finished)
            isRunning[current_index]=True
            t[current_index].start()
            mutex.unlock()  # Release the lock
            pushButton_start.setText('停止')
            pushButton_restart.setEnabled(False)
            #time.sleep(1)
    elif not listWidget.selectedItems():
        #没有选择任何脚本
        textBrowser.append('无效选项')

def thread_finished(current_index):
    pushButton_start=window.tab[current_index].pushButton_start
    pushButton_restart=window.tab[current_index].pushButton_restart
    textBrowser=window.tab[current_index].textBrowser
    #计时
    t_end = time.time()
    hours, rem = divmod(t_end-t[current_index].t_start, 3600)
    minutes, seconds = divmod(rem, 60)
    textBrowser.append("运行时间：{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    textBrowser.append(str(datetime.datetime.now()))
    #更新日志/按键
    pushButton_start.setText('开始')
    pushButton_restart.setEnabled(True)
    isRunning[current_index]=False
    textBrowser.append('脚本已结束！')
    action.alarm(1)
####################################################
#多线程
class MyThread(QThread):
    finished = pyqtSignal(int)
    def __init__(self, target=None,textBrowser=None,current_index=None):
        super().__init__()
        self.target = target
        self.textBrowser = textBrowser
        self.current_index = current_index
        self.t_start=time.time()
    
    def run(self):
        if self.target:
            self.target(self.textBrowser,self.current_index)
            self.finished.emit(self.current_index)
####################################################
#主窗口
class MainWindow(QMainWindow):
    def __init__(self,nthread):
        super().__init__()
        loadUi("yys.ui", self)
        self.setWindowTitle("YYS脚本 - lisai9093")
        #默认2线程
        self.nthread=nthread
        self.tab=[None]*self.nthread
        # Create the tab widget
        self.tabWidget = QTabWidget()
        # Create two tabs and load the same UI file into each
        for i in range(self.nthread):
            self.tab[i]=loadUi("yys.ui")
            self.tabWidget.addTab(self.tab[i], f"设备{i+1}：桌面版")
            self.tab[i].pushButton_start.clicked.connect(self.click_start)
            self.tab[i].pushButton_clear.clicked.connect(self.click_clear)
            self.tab[i].pushButton_restart.clicked.connect(self.click_restart)
            self.tab[i].listWidget.currentItemChanged.connect(self.click_list)
            self.tab[i].textBrowser.textChanged.connect(lambda value=i: self.text_changed(value))
        #self.tabWidget.currentChanged.connect(self.tab_changed)
        # Set the tab widget as the central widget
        self.setCentralWidget(self.tabWidget)

    #开始/停止按键
    def click_start(self):
        start_stop(self)
    #清空日志按键
    def click_clear(self):
        current_index = self.tabWidget.currentIndex()
        self.tab[current_index].textBrowser.clear()
    #连接/断开按键
    def click_restart(self):
        current_index = self.tabWidget.currentIndex()
        if action.devices_tab[current_index]==None:
            action.startup(self)
        else:
            action.reset_resolution(self)
    #选择脚本同时设置默认次数
    def click_list(self):
        #current tab index
        current_index = self.tabWidget.currentIndex()
        lineEdit=self.tab[current_index].lineEdit
        listWidget=self.tab[current_index].listWidget
        #current list index
        index=listWidget.currentRow()+1
        #设置默认次数
        if index in [1,3,6,11,12,15]:
            lineEdit.setEnabled(False)
            lineEdit.setText('inf')
        else:
            lineEdit.setEnabled(True)
            if index in [2,4,8,10,14]:
                lineEdit.setText('200')
            elif index in [5,7]:
                #探索
                lineEdit.setText('30')
            elif index==9:
                #斗技
                lineEdit.setText('30')
            elif index==13:
                lineEdit.setText('10')
    #自动显示最新日志
    def text_changed(self,current_index):
        #print(current_index)
        #current tab
        #current_index=self.tabWidget.currentIndex()
        textBrowser=self.tab[current_index].textBrowser
        #scroll to bottom
        scrollbar=textBrowser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    def tab_changed(self, index):
        print(f"Tab {index} clicked")
####################################################
if __name__ == '__main__':
    #总设备数量
    nthread=2
    #初始化所有线程
    t=[None]*nthread
    cishu_max=[0]*nthread
    isRunning=[False]*nthread
    action.init_thread_variable(nthread)

    #GUI
    app = QApplication(sys.argv)
    window = MainWindow(nthread)
    window.show()
    
    #检测系统
    print('操作系统: '+sys.platform)
    #自动检测ADB设备
    #action.startup(window)
    #读取文件
    imgs = action.load_imgs()
    #pyautogui.PAUSE = 0.05
    #pyautogui.FAILSAFE=False
    #脚本模式
    mode = [0, tupo, yuhun, yuhun2, yuhundanren,\
        gouliang, gouliang2, gouliang3,\
        baigui, douji, huodong,\
        chouka, mijing, yaoqi,\
        qilingdanren, debug]

    sys.exit(app.exec())

