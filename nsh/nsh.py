import sys,random,time
from PyQt6.QtCore import QObject,pyqtSignal,QMutex
import action

#global variables
last_click=None
mutex = QMutex()

class Worker(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(str,int)
    
    def __init__(self,thread_id=None,index=None,cishu_max=None):
        super().__init__()
        self.game_name='nsh'
        self.thread_id = thread_id
        self.mode = [0, self.tupo, self.yuhun, self.yuhun2, self.yuhundanren,\
                    self.gouliang, self.gouliang2, self.gouliang3,\
                    self.baigui, self.douji, self.huodong,\
                    self.chouka, self.mijing, self.yaoqi,\
                    self.qilingdanren]
        self.func_names=['0 屏幕截图并保存',\
        '1 结界突破',\
        '2 御魂(司机)',\
        '3 御魂(打手)',\
        '4 御魂/御灵/契灵探查(单刷)',\
        '5 探索(司机)',\
        '6 探索(打手)',\
        '7 探索(单刷)',\
        '8 百鬼夜行',\
        '9 自动斗技',\
        '10 当前活动',\
        '11 厕纸抽卡',\
        '12 秘境召唤',\
        '13 妖气封印/秘闻',\
        '14 契灵boss（单刷）']
        self.index=index
        self.cishu_max=cishu_max
        self.isRunning=False
        #读取文件
        self.imgs = action.load_imgs(self.game_name)

    def run(self):
        #self.progress.emit('Thread is '+str(self.thread_id),self.thread_id)
        #self.progress.emit('Call function index '+str(self.index)+' with max count of '+str(self.cishu_max),self.thread_id)
        command=self.mode[self.index]
        command()
        self.finished.emit(self.thread_id)
    
    def message_output(self,msg):
        self.progress.emit(msg,self.thread_id)
    
    #暂停并支持提前停止
    def sleep_fast(self,t=0):
        #return value indicates interrupt happens
        for t_count in range(round(t/0.1)):
            if not self.isRunning:
                return True
            time.sleep(0.1)
        return False
    
    ####################################################
    #以下是脚本功能代码
    ####################################################
    ########################################################
    #御魂司机
    def yuhun():
        last_click=''
        cishu=0
        refresh=0
        
        while self.isRunning:
            #截屏
            screen=action.screenshot()

            #自动点击通关结束后的页面
            for i in ['jujue','tiaozhan','tiaozhan2',\
                      'moren','queding','querenyuhun','ying',\
                      'jiangli','jiangli2',\
                      'jixu','shibai']:
                want = self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    self.message_output(i)
                    t = random.randint(50,100) / 100
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if self.sleep_fast(t): return
                    break
        
   
