import sys,random,time
from PyQt6.QtCore import QObject,pyqtSignal
import action

class Worker(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(str,int)
    
    def __init__(self,thread_id=None,index=None,cishu_max=None):
        super().__init__()
        self.game_name='yys'
        self.thread_id = thread_id
        #设置默认功能和次数
        self.func=[{'description':'0 屏幕截图并保存','func_name':0,'count_default':'inf'},\
        {'description':'1 结界突破','func_name':self.tupo,'count_default':'inf'},\
        {'description':'2 御魂(司机)','func_name':self.yuhun,'count_default':200},\
        {'description':'3 御魂(打手)','func_name':self.yuhun2,'count_default':'inf'},\
        {'description':'4 御魂/御灵/契灵探查(单刷)','func_name':self.yuhundanren,'count_default':200},\
        {'description':'5 探索(司机)','func_name':self.gouliang,'count_default':30},\
        {'description':'6 探索(打手)','func_name':self.gouliang2,'count_default':'inf'},\
        {'description':'7 探索(单刷)','func_name':self.gouliang3,'count_default':30},\
        {'description':'8 百鬼夜行','func_name':self.baigui,'count_default':200},\
        {'description':'9 自动斗技','func_name':self.douji,'count_default':30},\
        {'description':'10 当前活动','func_name':self.huodong,'count_default':200},\
        {'description':'11 厕纸抽卡','func_name':self.chouka,'count_default':'inf'},\
        {'description':'12 秘境召唤','func_name':self.mijing,'count_default':'inf'},\
        {'description':'13 妖气封印/秘闻','func_name':self.yaoqi,'count_default':10},\
        {'description':'14 契灵boss（单刷）','func_name':self.qilingdanren,'count_default':200}]
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
    #结节突破
    def tupo(self):
        last_click=''
        cishu = 0
        refresh=0
        liaotu=None
        while self.isRunning:   #直到取消，或者出错
            #if not isRunning:
            #    break
            #截屏
            #im = np.array(mss.mss().grab(monitor))
            #screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
            screen=action.screenshot(self.thread_id)
            #cv2.imshow("Image", screen)
            #cv2.waitKey(0)

            #寮突破判断
            if liaotu==None:
                want = self.imgs['liaotupo']
                size = want[0].shape
                h, w , ___ = size
                pts = action.locate(screen,want,0)
                if not len(pts) == 0:
                    liaotu=True
                    self.message_output('寮突破')

                want = self.imgs['gerentupo']
                size = want[0].shape
                h, w , ___ = size
                pts = action.locate(screen,want,0)
                if not len(pts) == 0:
                    liaotu=False
                    self.message_output('个人突破')
                    self.cishu_max=30

            if liaotu==False:
                if cishu >= 31:
                    self.message_output('进攻次数上限: '+str(cishu)+'/'+str(self.cishu_max))
                    return

            #奖励
            for i in ['jujue','queding',\
                      'shibai','ying','jiangli','jixu',\
                      'jingong','jingong2','jingong3',\
                      'lingxunzhang','lingxunzhang2','lingxunzhang4',\
                      'shuaxin','zhunbei']:
                want=self.imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target=screen
                pts=action.locate(target,want,0)
                if not len(pts)==0:
                    if last_click==i:
                        if ('jingong' in i or 'lingxunzhang' in i) and liaotu:
                            refresh=refresh+1
                            self.message_output('进攻CD，暂停5分钟')
                            t=60*5
                            if self.sleep_fast(t): return
                            last_click=''
                            continue
                        else:
                            refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    if refresh>6:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    t = random.randint(50,100) / 100
                    if i == 'shibai':
                        if cishu>0:
                            cishu = cishu - 1
                        self.message_output('进攻总次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t = random.randint(50,100) / 100
                    elif 'jingong' in i:
                        if refresh==0:
                            cishu=cishu+1
                        self.message_output('进攻总次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t = random.randint(500,800) / 100
                    self.message_output(i)
                    if self.sleep_fast(t): return
                    break

    ########################################################
    #御魂司机
    def yuhun(self):
        last_click=''
        cishu=0
        refresh=0
        
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #self.message_output('screen shot ok',time.ctime())
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足')
                return

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
                    if i == 'tiaozhan' or i=='tiaozhan2':
                        if refresh==0:
                            cishu=cishu+1
                        self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t=random.randint(500,750)/100
                    else:
                        self.message_output(i)
                        t = random.randint(50,100) / 100
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if self.sleep_fast(t): return
                    break
        
    ########################################################
    #御魂打手
    def yuhun2(self):
        last_click=''
        cishu=0
        refresh=0
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足')
                return

            #如果队友推出则自己也退出
            want = self.imgs['tiaozhanhuise']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('队友已退出')
                want = self.imgs['likaiduiwu']
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                    
            
            #自动点击通关结束后的页面
            for i in ['jujue','moren','queding','querenyuhun',\
                      'ying','jiangli','jiangli2','jixu',\
                      'jieshou2','jieshou','shibai']:
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
                    
                    #self.message_output('重复次数：',refresh)
                    if refresh>6:
                        self.message_output('进攻次数上限')
                        return
                    elif refresh==0 and 'jiangli' in i and not last_click=='querenyuhun':
                        #self.message_output('last',last_click)
                        cishu=cishu+1
                        self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                    if 'jieshou' in i:
                        a,b=pts[0]
                        if a<100:
                            break
                        t = random.randint(150,300) / 100
                    else:
                        t = random.randint(15,30) / 100
                    self.message_output(i)
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    last_click=i
                    if self.sleep_fast(t): return
                    break
                

    ########################################################
    #御魂单人
    def yuhundanren(self):
        last_click=''
        cishu=0
        refresh=0
        
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足')
                return

            for i in ['jujue','querenyuhun','ying','jiangli','jiangli2','jixu','zhunbei',\
                      'tiaozhan','tiaozhan2','tiaozhan3','queding','tancha','shibai']:
                want=self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    self.message_output(i)
                    if i == 'tiaozhan' or i=='tiaozhan2' or i=='tiaozhan3' or i=='tancha':
                        if refresh==0:
                            cishu=cishu+1
                        self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t = random.randint(500,800) / 100
                    else:
                        t = random.randint(15,30) / 100
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if self.sleep_fast(t): return
                    break

    ########################################################
    #探索司机
    def gouliang(self):
        last_click=''
        cishu=0
        refresh=0
        
        boss_done=False
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)

            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足 ')
                return

            want = self.imgs['queren']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('确认退出')
                try:
                    queding = pts[1]
                except:
                    queding = pts[0]
                xy = action.cheat(queding, w, h)
                action.touch(xy,self.thread_id)
                t = random.randint(15,30) / 100
                if self.sleep_fast(t): return

            
            #设定目标，开始查找
            #进入后
            want=self.imgs['guding']

            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('正在地图中')
                for i in ['boss', 'jian']:
                    want = self.imgs[i]
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
                        #self.message_output('重复次数：',refresh)
                        if refresh>6:
                            self.message_output('进攻次数上限')
                            return
                        xy = action.cheat(pts[0], w, h)
                        action.touch(xy,self.thread_id)
                        time.sleep(0.5)
                        break

                if len(pts)==0:
                    if not boss_done:
                        self.message_output('向右走')
                        right = (854, 420)
                        xy = action.cheat(right, 10, 10)
                        action.touch(xy,self.thread_id)
                        t = random.randint(100,300) / 100
                        if self.sleep_fast(t): return
                        continue
                    else:
                        i='tuichu'
                        want = self.imgs[i]
                        size = want[0].shape
                        h, w , ___ = size
                        #x1,x2 = upleft, (965, 522)
                        #target = action.cut(screen, x1, x2)
                        target = screen
                        pts = action.locate(target,want,0)
                        if not len(pts) == 0:
                            self.message_output('退出中'+i)
                            try:
                                queding = pts[1]
                            except:
                                queding = pts[0]
                            xy = action.cheat(queding, w, h)
                            action.touch(xy,self.thread_id)
                            t = random.randint(50,80) / 100
                            if self.sleep_fast(t): return
                    continue

            for i in ['jujue','queding','ying','querenyuhun',\
                      'jiangli','jixu',\
                      'tiaozhan','ditu']:
                want = self.imgs[i]
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
                        self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                    #self.message_output('重复次数：',refresh)
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return

                    self.message_output(i)
                    xy = action.cheat(pts[0], w, h )
                    action.touch(xy,self.thread_id)
                    if i=='queding':
                        t = random.randint(150,200) / 100
                    else:
                        t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                    break

    ########################################################
    #探索打手
    def gouliang2(self):
        last_click=''
        refresh=0
        cishu=0
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足 ')
                return
            
            #进入后
            want = self.imgs['guding']
            pts = action.locate(screen,want,0)
            if not len(pts) == 0:
                self.message_output('正在地图中')
                
                want = self.imgs['xiao']
                pts = action.locate(screen,want,0)
                
                if not len(pts) == 0:
                    self.message_output('组队状态中')
                else:
                    self.message_output('退出重新组队')
                    
                    for i in ['queren', 'queren2','tuichu']:
                        want = self.imgs[i]
                        size = want[0].shape
                        h, w , ___ = size
                        pts = action.locate(screen,want,0)
                        
                        if not len(pts) == 0:
                            if last_click==i:
                                refresh=refresh+1
                            else:
                                refresh=0
                            last_click=i
                            #self.message_output('重复次数：',refresh)
                            if refresh>6:
                                self.message_output('进攻次数上限')
                                return
                            
                            self.message_output('退出中'+i)
                            try:
                                queding = pts[1]
                            except:
                                queding = pts[0]
                            xy = action.cheat(queding, w, h)
                            action.touch(xy,self.thread_id)
                            t = random.randint(50,80) / 100
                            if self.sleep_fast(t): return
                            break
                    continue

            for i in ['jujue','jieshou','querenyuhun','ying',\
                      'jiangli','jixu']:
                want = self.imgs[i]
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
                            self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                    #self.message_output('重复次数：',refresh)
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    self.message_output(i)
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if i=='jieshou' or i=='jieshou1':
                        t = random.randint(150,300) / 100
                    else:
                        t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                    break
                
    ########################################################
    #探索单人
    def gouliang3(self):
        last_click=''
        cishu=0
        refresh=0
        
        boss_done=False
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足')
                return

            want = self.imgs['queren']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            #x1,x2 = upleft, (965, 522)
            #target = action.cut(screen, x1, x2)
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('确认退出')
                try:
                    queding = pts[1]
                except:
                    queding = pts[0]
                xy = action.cheat(queding, w, h)
                action.touch(xy,self.thread_id)
                t = random.randint(15,30) / 100
                if self.sleep_fast(t): return

            
            #设定目标，开始查找
            #进入后
            want=self.imgs['guding']

            pts = action.locate(screen,want,0)
            if not len(pts) == 0:
                self.message_output('正在地图中')
                for i in ['boss', 'jian']:
                    want = self.imgs[i]
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
                        #self.message_output('重复次数：',refresh)
                        if refresh>6:
                            self.message_output('进攻次数上限')
                            return
                        
                        self.message_output('点击小怪'+i)
                        xy = action.cheat(pts[0], w, h)
                        action.touch(xy,self.thread_id)
                        time.sleep(0.5)
                        break

                if len(pts)==0:
                    if not boss_done:
                        self.message_output('向右走')
                        right = (854, 420)
                        xy = action.cheat(right, 10, 10)
                        action.touch(xy,self.thread_id)
                        t = random.randint(100,300) / 100
                        if self.sleep_fast(t): return
                        continue
                    else:
                        i='tuichu'
                        want = self.imgs[i]
                        size = want[0].shape
                        h, w , ___ = size
                        pts = action.locate(screen,want,0)
                        if not len(pts) == 0:
                            self.message_output('退出中'+i)
                            try:
                                queding = pts[1]
                            except:
                                queding = pts[0]
                            xy = action.cheat(queding, w, h)
                            action.touch(xy,self.thread_id)
                            t = random.randint(50,80) / 100
                            if self.sleep_fast(t): return
                    continue

            for i in ['jujue','querenyuhun',\
                      'tansuo','ying','jiangli','jixu','c28','ditu']:
                want = self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    if refresh==0 and i=='tansuo':
                        cishu=cishu+1
                        self.message_output('探索次数：'+str(cishu)+'/'+str(self.cishu_max))
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    self.message_output(i)
                    xy = action.cheat(pts[0], w, h )
                    action.touch(xy,self.thread_id)
                    t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                    break

    ########################################################
    #百鬼
    def baigui(self):
        last_click=''
        refresh=0
        cishu=0
        
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)

            #设定目标，开始查找
            #进入后
            for i in ['baigui','gailv','douzihuoqu','miaozhun','baiguijieshu',\
                    'jinru']:
                want = self.imgs[i]
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
                    if i=='jinru':
                        if refresh==0:
                            cishu=cishu+1
                            self.message_output('进入百鬼:'+str(cishu)+'/'+str(self.cishu_max))
                        if cishu>self.cishu_max:
                            self.message_output('进攻次数上限')
                            return
                    self.message_output('点击'+i)
                    xy = action.cheat(pts[0], w, h )
                    action.touch(xy,self.thread_id)
                    t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                    continue

            i='inbaigui'
            want=self.imgs[i]
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                #self.message_output('正在百鬼中')
                i='blank'
                want = self.imgs[i]
                target = screen
                pts = action.locate(target,want,0)
                if len(pts) == 0:
                    refresh=0
                    #小怪出现！
                    self.message_output('点击小怪')
                    pts2 = (640, 450)
                    xy = action.cheat(pts2, 100, 80)
                    action.touch(xy,self.thread_id)
                    t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                    continue

            i='kaishi'
            want = self.imgs[i]
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                refresh=0
                last_click=i
                self.message_output('选择押注界面')
                i='ya'
                want = self.imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts2 = action.locate(target,want,0)
                if not len(pts2) == 0:
                    self.message_output('点击开始')
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    t = random.randint(15,30) / 100
                    if self.sleep_fast(t): return
                else:
                    #选择押注
                    index=random.randint(0,2)
                    pts2 = (300+index*340, 500)
                    self.message_output('选择押注: '+str(index))
                    xy = action.cheat(pts2, w, h-10 )
                    action.touch(xy,self.thread_id)
                    t = random.randint(100,300) / 100
                    if self.sleep_fast(t): return

                    self.message_output('点击开始')
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    t = random.randint(100,200) / 100
                    if self.sleep_fast(t): return


    ########################################################
    #斗技
    def douji(self):
        last_click=''
        doujipaidui=0
        refresh=0
        cishu=0
        
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)

            for i in ['jujue','shoudong','zidong','queren',\
                      'douji','douji2','douji3','douji4','doujilianxi',\
                      'doujiqueren','doujiend','ying','jixu',\
                      'zhunbei','zhunbei2',\
                      'doujiquxiao']:
                want = self.imgs[i]
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if not len(pts) == 0:
                    #self.message_output(i)
                    if i in ['douji','douji2','douji3','douji4']:
                        i='douji'
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click=i
                    #self.message_output('重复次数：',refresh)
                    if refresh==0 and i=='douji':
                        cishu=cishu+1
                        self.message_output('斗技次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t = random.randint(150,300) / 100
                    elif i=='doujiquxiao':
                        refresh=0
                        doujipaidui=doujipaidui+1
                        self.message_output('斗技搜索:'+str(doujipaidui))
                        if doujipaidui>5:
                            doujipaidui=0
                            self.message_output('取消搜索')
                            cishu=cishu-1
                            t = random.randint(15,30) / 100
                        else:
                            break
                    else:
                        self.message_output(i)
                        t = random.randint(50,100) / 100
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    t = random.randint(50,100) / 100
                    if self.sleep_fast(t): return
                    break

    ########################################################
    #当前活动
    def huodong(self):
        last_click=''
        cishu=0
        
        refresh=0
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)

            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足 ')
                return
            
            for i in ['jujue','querenyuhun','queding','hdend',\
                      'hdtiaozhan','hdtiaozhan2','hdtiaozhan3','ying','hdsousuo','zhunbei',\
                      'shibai','jixu','liaotianguanbi']:
                want = self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    self.message_output(i)
                    if refresh>6:
                        self.message_output('进攻次数上限')
                        return

                    t = 1
                    if 'hdtiaozhan' in i:
                        if refresh==0:
                            cishu=cishu+1
                            self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t=5
                    if i=='hdsousuo':
                        t=5
                    if i=='hdend' and False:
                        if refresh==0:
                            self.message_output('疲劳度满，休息10分钟')
                            t = 10*60
                            if self.sleep_fast(t): return
                    xy = action.cheat(pts[0], w, h)
                    action.touch(xy,self.thread_id)
                    #self.message_output('等待时间：',t)
                    if self.sleep_fast(t): return

    ##########################################################
    #合成结界卡
    def card(self):
        last_click=''
        refresh=0
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)
            
            for i in ['taiyin2','sanshinei','taiyin3']:
                want = self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    if refresh>6:
                        self.message_output('进攻次数上限')
                        return
                    
                    self.message_output('结界卡*'+i)
                    xy = action.cheat(pts[0], w/2, h-10)
                    action.touch(xy,self.thread_id)
                    break
            if len(pts) == 0:
                    self.message_output('结界卡不足')
                    return
            

            for i in range(2):
                #截屏
                im = np.array(mss.mss().grab(monitor))
                screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

                want = self.imgs['taiyin']
                size = want[0].shape
                h, w , ___ = size
                target = screen
                pts = action.locate(target,want,0)
                if len(pts) == 0:
                    self.message_output('结界卡不足')
                    return
                else:
                    if last_click==i:
                        refresh=refresh+1
                    else:
                        refresh=0
                    last_click='taiyin'
                    #self.message_output('重复次数：',refresh)
                    if refresh>6:
                        self.message_output('进攻次数上限')
                        return
                    
                    self.message_output('结界卡'+i)
                    xy = action.cheat(pts[0], w/2, h-10 )
                    action.touch(xy,self.thread_id)

            #截屏
            screen=action.screenshot(self.thread_id)

            want = self.imgs['hecheng']
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
                #self.message_output('重复次数：',refresh)
                if refresh>6:
                    self.message_output('进攻次数上限')
                    return
                
                self.message_output('合成中。。。')
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,self.thread_id)

            time.sleep(1)

    ##########################################################
    #抽卡
    def chouka(self):
        last_click=None
        cishu=0
        
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)
            
            want = self.imgs['zaicizhaohuan']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                if cishu>self.cishu_max:
                    self.message_output('次数上限')
                    return
                cishu=cishu+1
                self.message_output('抽卡中：'+str(cishu)+'/'+str(self.cishu_max))
                xy = action.cheat(pts[0], w, h-10 )
                action.touch(xy,self.thread_id)
                t = random.randint(10,30) / 100
                if self.sleep_fast(t): return

    ##########################################################
    #蓝蛋升级
    def shengxing(self):
        last_click=''
        cishu=0
        refresh=0
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)
                
            for i in ['jineng','jixushengxing',\
                      'jixuyucheng','querenshengxing']:
                want = self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    if refresh>6:
                        self.message_output('进攻次数上限')
                        return
                    
                    self.message_output('升级中。。。'+i)
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if i=='querenshengxing':
                        if refresh==0:
                            cishu=cishu+1
                        self.message_output('升级个数：'+str(cishu)+'/'+str(self.cishu_max))
                        t = random.randint(250,350) / 100
                    else:
                        t = random.randint(20,100) / 100
                        
                    if self.sleep_fast(t): return
                    
    ##########################################################
    #秘境召唤
    def mijing(self):
        last_click=''
        refresh=0
        while self.isRunning:
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #检测聊天界面
            want = self.imgs['liaotianguanbi']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                #self.message_output('搜索秘境车中。。。')

                for i in ['jujue','mijingzhaohuan','mijingzhaohuan2']:
                    want = self.imgs[i]
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
                        #self.message_output('重复次数：',refresh)
                        if refresh>6:
                            self.message_output('进攻次数上限')
                            return
                        
                        self.message_output(i)
                        xy = action.cheat(pts[0], w, h-10 )
                        action.touch(xy,self.thread_id)
                        #t = random.randint(10,100) / 100
                        #if self.sleep_fast(t): return
                        break
            else:
                for i in ['jujue','canjia','liaotian']:
                    want = self.imgs[i]
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
                        #self.message_output('重复次数：',refresh)
                        if refresh>6:
                            self.message_output('进攻次数上限')
                            return
                        
                        if i=='canjia':
                            self.message_output('加入秘境召唤！'+i)
                        xy = action.cheat(pts[0], w, h-10 )
                        action.touch(xy,self.thread_id)
                        t = random.randint(10,30) / 100
                        if self.sleep_fast(t): return
                        break

    ########################################################
    #妖气封印和秘闻
    def yaoqi(self):
        global isRunning,cishu_max
        last_click=''
        cishu=0
        refresh=0
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #委派任务
            for i in ['jujue','jiangli','jixu','zhunbei',\
                      'shibai','zidongpipei','zudui2',\
                      'ying','tiaozhan3','tiaozhan4']:
                want = self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    if i=='zidongpipei' or i=='tiaozhan3' or i=='tiaozhan4':
                        if refresh==0:
                            cishu=cishu+1
                        self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t=100/100
                    elif i=='shibai':
                        self.message_output('自动结束')
                        return
                    else:
                        self.message_output(i)
                        t = random.randint(30,80) / 100
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if self.sleep_fast(t): return
                    break
            
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足')
                return

    ########################################################
    #契灵单人
    def qilingdanren(self):
        last_click=''
        cishu=0
        
        refresh=0
        while self.isRunning:   #直到取消，或者出错
            #截屏
            screen=action.screenshot(self.thread_id)
            
            #体力不足
            want = self.imgs['notili']
            size = want[0].shape
            h, w , ___ = size
            target = screen
            pts = action.locate(target,want,0)
            if not len(pts) == 0:
                self.message_output('体力不足')
                return

            for i in ['jujue','ying','jiangli','jixu','queding',\
                      'qiling1','mingqi','queren3',\
                      'tiaozhan5','shibai','xiaozhiren']:
                want=self.imgs[i]
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
                    #self.message_output('重复次数：',refresh)
                    self.message_output(i)
                    if i=='tancha' or i=='tiaozhan5':
                        if refresh==0:
                            cishu=cishu+1
                        self.message_output('挑战次数：'+str(cishu)+'/'+str(self.cishu_max))
                        t = random.randint(50,150) / 100
                    elif i=='queren3':
                        t = random.randint(350,450) / 100
                    else:
                        t = random.randint(15,30) / 100
                    if refresh>6 or cishu>self.cishu_max:
                        self.message_output('进攻次数上限')
                        return
                    xy = action.cheat(pts[0], w, h-10 )
                    action.touch(xy,self.thread_id)
                    if self.sleep_fast(t): return
                    break
