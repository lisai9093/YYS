import sys,random,time
from PyQt6.QtCore import QObject,pyqtSignal
import action

class Worker(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(str,int)
    
    def __init__(self,thread_id=None,index=None,cishu_max=None):
        super().__init__()
        self.game_name='nsh'
        self.thread_id = thread_id
        #设置默认功能和次数
        self.func=[{'description':'0 屏幕截图并保存','func_name':0,'count_default':'inf'},\
        {'description':'1 组队司机','func_name':self.huodong,'count_default':'inf'},\
        {'description':'2 组队打手','func_name':self.huodong2,'count_default':'inf'},
        {'description':'3 刷视频','func_name':self.shua,'count_default':'inf'}]
        #功能序号
        self.index=index
        self.cishu_max=cishu_max
        self.isRunning=False
        #读取文件
        self.imgs = action.load_imgs(self.game_name)

    def run(self):
        #self.progress.emit('Thread is '+str(self.thread_id),self.thread_id)
        #self.progress.emit('Call function index '+str(self.index)+' with max count of '+str(self.cishu_max),self.thread_id)
        command=self.func[self.index]['func_name']
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
    #司机
    def huodong(self):
        last_click=''
        cishu=0
        refresh=0
        
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)

            #自动点击通关结束后的页面
            for i in ['duihua','chuanjianduiwu','chukuimenjin','dagou',\
                      'duiwujiaren','guanbi','tiaozhanshijian',\
                      'tuichujian',\
                      'yaoqing1','yaoqing2','tuihuijiantou']:
                want = self.imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    self.message_output(i)
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #self.message_output('重复次数：',refresh)
                    self.message_output(i)
                    t = random.randint(200,300) / 100
                    if cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    for index in range(len(pts)):
                        xy = action.cheat(pts[index], w, h-10 )
                        action.touch(xy,self.thread_id)
                        if self.sleep_fast(t): return
                    break
        
    #打手
    def huodong2(self):
        last_click=''
        cishu=0
        refresh=0
        
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)

            #自动点击通关结束后的页面
            for i in ['dagou','daiji']:
                want = self.imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    self.message_output(i)
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #self.message_output('重复次数：',refresh)
                    self.message_output(i)
                    t = random.randint(50,100) / 100
                    if cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    for index in range(len(pts)):
                        xy = action.cheat(pts[index], w, h-10 )
                        action.touch(xy,self.thread_id)
                        if self.sleep_fast(t): return

    #刷视频
    def shua(self):
        last_click=''
        cishu=0
        refresh=0
        t=3
        w=640
        h=1136

        while self.isRunning:
            xy = random.randint(1, w),random.randint(101, h)
            action.swipe(xy,self.thread_id)
            if self.sleep_fast(t): return
