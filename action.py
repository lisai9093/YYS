import cv2,time,os,random,sys,mss,copy,subprocess,pyautogui
import numpy
from PyQt6.QtWidgets import QMessageBox,QPushButton,QInputDialog

#global variables
devices_tab=[None]
adb_enable=[False]
adb_path=None
scalar=False
scaling_factor=1
monitor=None
#截屏，并裁剪以加速
upleft = (0, 0)
downright = (1136, 700)
#默认桌面版
if sys.platform=='darwin':
    scalar=True
    scaling_factor=1/2
else:
    scalar=False
    scaling_factor=1
a,b = upleft
c,d = downright
monitor = {"top": b, "left": a, "width": c, "height": d}

#initialization thread
def init_thread_variable(nthread):
    global devices_tab,adb_enable
    devices_tab=[None]*nthread
    adb_enable=[False]*nthread

def startup(window):
    global scalar,scaling_factor,monitor,adb_enable,adb_path,devices_tab
    thread_id=window.tabWidget.currentIndex()
    textBrowser=window.tab[thread_id].textBrowser
    pushButton_restart=window.tab[thread_id].pushButton_restart
    #检测ADB
    if sys.platform=='win32':
        textBrowser.append('检测模拟器')
        mumu_path="C:\\Program Files\\Netease\\MuMuPlayer-12.0\\shell\\adb.exe"
        ld_path="C:\\leidian\\LDPlayer9\\adb.exe"
        if os.path.isfile(ld_path):
            textBrowser.append('检测到雷电模拟器')
            adb_path=ld_path
        elif os.path.isfile(mumu_path):
            textBrowser.append('检测到MuMu模拟器')
            adb_path=mumu_path
            #获取端口信息
            port, ok = QInputDialog.getInt(window, '模拟器端口', '输入MuMu模拟器端口（默认7555）：',7555,0,65535,1)
            if ok:
                textBrowser.append('模拟器端口：'+str(port))
                mumu_ip='127.0.0.1:'+str(port)
                comm=[adb_path,'connect',mumu_ip]
                out=subprocess.run(comm,shell=False,capture_output=True,check=False)
                out=out.stdout.decode('utf-8')
                textBrowser.append(out)
        else:
            #无模拟器
            adb_path=''
            out=''
    else:
        adb_path='adb'

    if len(adb_path)>0:
        comm=[adb_path,'devices']
        #textBrowser.append(comm)
        try:
            out=subprocess.run(comm,capture_output=True,timeout=1)
            out=out.stdout.decode('utf-8')
        except:
            textBrowser.append('ADB error')
            out=''
        textBrowser.append(out)
        out=out.splitlines()
    if len(out)>2:
        textBrowser.append('监测到ADB设备，默认使用安卓截图')
        adb_enable[thread_id]=True
        #check number of devices
        devices=[]
        for device in out:
            device=device.split()
            if len(device)==2:
                devices.append(device[0])
        if len(devices)==1:
            device=devices[0]
        else:
            #popup window
            msg_box = QMessageBox()
            msg_box.setText("选择安卓设备")
            # Change the button texts
            for device in devices:
                button = QPushButton(device)
                msg_box.addButton(button, QMessageBox.ButtonRole.ActionRole)
            result = msg_box.exec()
            device=devices[result-2]

        textBrowser.append('使用设备：'+device)
        devices_tab[thread_id]=device
        window.tabWidget.setTabText(thread_id, '设备'+str(thread_id+1)+'：'+device)
        pushButton_restart.setText('断开ADB')
        #change resolution
        screen=screenshot(thread_id)
        w=screen.shape[0]
        h=screen.shape[1]
        textBrowser.append('原始分辨率：'+str(w)+'x'+str(h))
        if (w==640 and h==1136) or (h==640 and w==1136):
            textBrowser.append('无需修改分辨率')
        else:
            if w>h:
                comm=[adb_path,"-s",device,"shell","wm","size","1136x640"]
                subprocess.run(comm,shell=False)
                textBrowser.append('修改成桌面版分辨率: 1136x640')
            elif w<=h:
                comm=[adb_path,"-s",device,"shell","wm","size","640x1136"]
                subprocess.run(comm,shell=False)
                textBrowser.append('修改成桌面版分辨率: 640x1136')
    else:
        textBrowser.append('未监测到ADB设备，默认使用桌面版')
        textBrowser.append('请把桌面版窗口移动到第一个屏幕的左上角')
        adb_enable[thread_id]=False
        pyautogui.FAILSAFE=False

    #检测系统
    if sys.platform=='darwin' and not adb_enable[thread_id]:
        scalar=True
        scaling_factor=1/2
    else:
        scalar=False
        scaling_factor=1

    #截屏，并裁剪以加速
    upleft = (0, 0)
    if scalar==True:
        downright = (1136,750)
    else:
        downright = (1136, 700)
    a,b = upleft
    c,d = downright
    monitor = {"top": b, "left": a, "width": c, "height": d}

def reset_resolution(window):
    thread_id = window.tabWidget.currentIndex()
    textBrowser=window.tab[thread_id].textBrowser
    pushButton_restart=window.tab[thread_id].pushButton_restart
    if adb_enable[thread_id]:
        textBrowser.append('重置安卓分辨率')
        comm=[adb_path,"-s",devices_tab[thread_id],"shell","wm","size","reset"]
        subprocess.run(comm,shell=False)
        #remove device info
        devices_tab[thread_id]=None
        adb_enable[thread_id]=False
        #日志更新
        textBrowser.append('已断开连接')
        window.tabWidget.setTabText(thread_id, '设备'+str(thread_id+1)+'：桌面版')
        pushButton_restart.setText('连接ADB')

def screenshot(thread_id):
    #ADB截屏
    if adb_enable[thread_id]:
        comm=[adb_path,"-s",devices_tab[thread_id],"shell","screencap","-p"]
        #隐藏终端窗口
        if sys.platform=='win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
            invisibledict = {
                "startupinfo": startupinfo,
                "creationflags": creationflags,
                "start_new_session": True,
            }
            image_bytes = subprocess.run(comm,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**invisibledict)
        else:
            image_bytes = subprocess.run(comm,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        image_bytes=image_bytes.stdout
        image_array=numpy.frombuffer(image_bytes, numpy.uint8)
        #sometime numpy returns None
        if image_array is not None:
            screen=cv2.imdecode(image_array,cv2.IMREAD_COLOR)
        else:
            screen=None
        if screen is None:
            image_bytes = image_bytes.replace(b'\r\n', b'\n')
            screen = cv2.imdecode(numpy.frombuffer(image_bytes, numpy.uint8),cv2.IMREAD_COLOR)
    else:
        #桌面版截屏
        with mss.mss() as sct:
            if scalar:
                #{"top": b, "left": a, "width": c, "height": d}
                #shrink monitor to half due to macOS default DPI scaling
                monitor2=copy.deepcopy(monitor)
                monitor2["width"]=int(monitor2["width"]*scaling_factor)
                monitor2["height"]=int(monitor2["height"]*scaling_factor)
                screen=sct.grab(monitor2)
                #mss.tools.to_png(screen.rgb, screen.size, output="screenshot.png")
                screen = numpy.array(screen)
                #textBrowser.append('Screen size: ',screen.shape)
                #MuMu助手默认拉伸4/3倍
                screen = cv2.resize(screen, (int(screen.shape[1]*0.75), int(screen.shape[0]*0.75)),
                                    interpolation = cv2.INTER_LINEAR)
            else:
                screen = numpy.array(sct.grab(monitor))

    #all else failed
    if screen is None:
        return screen
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    return screen

#在背景查找目标图片，并返回查找到的结果坐标列表，target是背景，want是要找目标
def locate(target,want, show=bool(0), msg=bool(0)):
    loc_pos=[]
    want,treshold,c_name=want[0],want[1],want[2]
    if target is None:
        return loc_pos
    result=cv2.matchTemplate(target,want,cv2.TM_CCOEFF_NORMED)
    location=numpy.where(result>=treshold)
    #textBrowser.append(location)

    if msg:  #显示正式寻找目标名称，调试时开启
        textBrowser.append(c_name,'searching... ')

    h,w=want.shape[:-1] #want.shape[:-1]

    n,ex,ey=1,0,0
    for pt in zip(*location[::-1]):    #其实这里经常是空的
        x,y=pt[0]+int(w/2),pt[1]+int(h/2)
        if (x-ex)+(y-ey)<15:  #去掉邻近重复的点
            continue
        ex,ey=x,y

        cv2.circle(target,(x,y),10,(0,0,255),3)

        if msg:
            textBrowser.append(c_name,'we find it !!! ,at',x,y)

        if scalar:
            x,y=int(x*scaling_factor),int(y*scaling_factor)
        else:
            x,y=int(x),int(y)
            
        loc_pos.append([x,y])

    if show:  #在图上显示寻找的结果，调试时开启
        textBrowser.append('Debug: show action.locate')
        cv2.imshow('we get',target)
        cv2.waitKey(0) 
        cv2.destroyAllWindows()

    if len(loc_pos)==0:
        #textBrowser.append(c_name,'not find')
        pass

    return loc_pos


#按【文件内容，匹配精度，名称】格式批量聚聚要查找的目标图片，精度统一为0.95，名称为文件名
def load_imgs(game_name):
    mubiao = {}
    acc=0.95
    path = os.getcwd()+'/'+game_name+'/png'
    file_list = os.listdir(path)
    for file in file_list:
        if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        name = file.split('.')[0]
        file_path = path + '/' + file
        a = [cv2.cvtColor(cv2.imread(file_path),cv2.COLOR_BGR2RGB),acc,name]
        mubiao[name] = a
    return mubiao

#蜂鸣报警器，参数n为鸣叫次数
def alarm(n):
    frequency = 1500
    duration = 500

    if os.name=='nt':
        import winsound
        winsound.Beep(frequency, duration)
    else:
        #os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        sys.stdout.write('\a')
        sys.stdout.flush()

#裁剪图片以缩小匹配范围，screen为原图内容，upleft、downright是目标区域的左上角、右下角坐标
def cut(screen,upleft,downright): 

    a,b=upleft
    c,d=downright
    screen=screen[b:d,a:c]

    return screen

#随机偏移坐标，防止游戏的外挂检测。p是原坐标，w、n是目标图像宽高，返回目标范围内的一个随机坐标
def cheat(p, w, h):
    a,b = p
    if scalar:
        w, h = int(w/3/2), int(h/3/2)
    else:
        w, h = int(w/3), int(h/3)
    if h<0:
        h=1
    c,d = random.randint(-w, w),random.randint(-h, h)
    e,f = a + c, b + d
    y = [e, f]
    return(y)

# 点击屏幕，参数pos为目标坐标
def touch(pos,thread_id):
    x, y = pos
    if adb_enable[thread_id]:
        comm=[adb_path,"-s",devices_tab[thread_id],"shell","input","tap",str(x),str(y)]
        #textBrowser.append('Command: ',comm)
        subprocess.run(comm,shell=False)
    else:
        pyautogui.click(pos)




