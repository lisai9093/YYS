import sys,time,os,datetime,configparser,importlib,argparse
from functools import partial
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
    QDialog,
)
from PyQt6.QtCore import QThread,pyqtSignal,QProcess,QMutex,Qt
import action


def resource_path(rel_path: str) -> str:
    """Return absolute path to resource, whether running from source or PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # PyInstaller extracts files to _MEIPASS
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel_path)

#global variables
mutex = QMutex()

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
        loadUi(resource_path('main.ui'), self)
        self.setWindowTitle(game_name+'脚本 - lisai9093')
        self.nthread=nthread
        self.tab=[None]*self.nthread
        self.tabWidget = QTabWidget()
        self.workers = [None]*self.nthread  # Lazy init - create on worker thread
        self.threads = [QThread() for i in range(nthread)]
        self.t_start=[None]*self.nthread
        self.isRunning=[False]*self.nthread
        # Create tabs and load the same UI file into each
        for i in range(self.nthread):
            #GUI
            self.tab[i]=loadUi(resource_path('main.ui'))
            self.tabWidget.addTab(self.tab[i], f'设备{i+1}：桌面版')
            #self.tab[i].pushButton_start.clicked.connect(lambda thread_id=i: self.start_stop(thread_id))
            self.tab[i].pushButton_start.clicked.connect(partial(self.start_stop, thread_id=i))
            self.tab[i].pushButton_clear.clicked.connect(partial(self.click_clear, thread_id=i))
            self.tab[i].pushButton_restart.clicked.connect(partial(self.click_restart, thread_id=i))
            self.tab[i].listWidget.currentItemChanged.connect(partial(self.click_list, thread_id=i))
            #self.tab[i].textBrowser.textChanged.connect(lambda thread_id=i: self.text_changed(thread_id))
            self.tab[i].textBrowser.textChanged.connect(partial(self.text_changed, thread_id=i))
            
            #thread - DON'T initialize workers yet (too slow)
            self.threads[i].start()  # Start empty thread
        
        # Load worker list items asynchronously
        # For now, create a dummy worker just to get the function list
        dummy_worker = game.Worker(0)
        for i in range(self.nthread):
            for item in dummy_worker.func:
                self.tab[i].listWidget.addItem(item['description'])
            
            # Connect worker signals AFTER thread setup
            # Workers will be created lazily on first use
        
        #self.tabWidget.currentChanged.connect(self.tab_changed)
        # Set the tab widget as the central widget
        self.setCentralWidget(self.tabWidget)
        #自动检测ADB设备
        action.init_thread_variable(nthread)

    #清空日志按键
    def click_clear(self,thread_id):
        self.tab[thread_id].textBrowser.clear()
    #更新日志按键
    def update_text_browser(self,text,thread_id):
        self.tab[thread_id].textBrowser.append(text)
    #连接/断开按键
    def click_restart(self,thread_id):
        if self.isRunning[thread_id]:
            textBrowser=self.tab[thread_id].textBrowser
            textBrowser.append('脚本运行中，请先停止')
            return
        mutex.lock()  # Acquire the lock
        if action.devices_tab[thread_id]==None:
            action.startup(self)
        else:
            action.reset_resolution(self)
        mutex.unlock()  # Release the lock
    #选择脚本同时设置默认次数
    def click_list(self,thread_id):
        lineEdit=self.tab[thread_id].lineEdit
        listWidget=self.tab[thread_id].listWidget
        #current list index
        index=listWidget.currentRow()
        #Get function list from dummy worker (already created)
        if self.workers[thread_id] is None:
            dummy = game.Worker(thread_id)
            default_count = str(dummy.func[index]['count_default'])
        else:
            default_count = str(self.workers[thread_id].func[index]['count_default'])
        #设置默认次数
        lineEdit.setText(default_count)
    #自动显示最新日志
    def text_changed(self,thread_id):
        #current tab
        textBrowser=self.tab[thread_id].textBrowser
        #scroll to bottom
        scrollbar=textBrowser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    def tab_changed(self, thread_id):
        pass
    #开始/停止按键
    def start_stop(self,thread_id):
        textBrowser=self.tab[thread_id].textBrowser
        listWidget=self.tab[thread_id].listWidget
        lineEdit=self.tab[thread_id].lineEdit
        pushButton_start=self.tab[thread_id].pushButton_start
        pushButton_restart=self.tab[thread_id].pushButton_restart
        if self.threads[thread_id] and self.isRunning[thread_id]:
            #stop running job
            pushButton_start.setText('开始')
            pushButton_start.setEnabled(False)
            mutex.lock()  # Acquire the lock
            self.workers[thread_id].isRunning=False
            self.isRunning[thread_id]=False
            #if not self.threads[thread_id].wait(5000):  # Wait for 10 seconds
                #textBrowser.append('已强制停止！')
                #self.threads[thread_id].terminate()
            mutex.unlock()  # Release the lock
            #pushButton_start.setEnabled(True)
            #pushButton_restart.setEnabled(True)
        elif listWidget.selectedItems() and not self.isRunning[thread_id]:
            #已选择脚本，开始运行
            textBrowser.append(listWidget.currentItem().text())
            index=listWidget.currentRow()
            #设置次数
            if not lineEdit.text() == 'inf':
                try:
                    mutex.lock()  # Acquire the lock
                    cishu_max=int(lineEdit.text())
                    mutex.unlock()  # Release the lock
                    if cishu_max<1 or cishu_max>9999:
                        raise Exception('数字超出范围（1-9999）')
                except ValueError:
                    textBrowser.append('请输入数字')
                    pushButton_start.setText('开始')
                    return
                except Exception as e:
                    textBrowser.append(f'数字超出范围（1-9999）: {e}')
                    pushButton_start.setText('开始')
                    return
            else:
                mutex.lock()  # Acquire the lock
                cishu_max=float('inf')
                mutex.unlock()  # Release the lock

            if index==0:
                #debug has to be on main thread
                self.screen_show(thread_id)
            else:
                #✅ Lazy initialize worker if needed
                if self.workers[thread_id] is None:
                    self.workers[thread_id] = game.Worker(thread_id)
                    self.workers[thread_id].moveToThread(self.threads[thread_id])
                    # CRITICAL: Connect AFTER moveToThread() with QueuedConnection!
                    self.workers[thread_id].start_task.connect(self.workers[thread_id].execute_task, Qt.ConnectionType.QueuedConnection)
                    self.workers[thread_id].finished.connect(partial(self.thread_finished, thread_id=thread_id))
                    self.workers[thread_id].progress.connect(self.update_text_browser)
                
                # ✅ Emit signal to worker thread (queued, non-blocking)
                self.t_start[thread_id]=time.time()
                self.workers[thread_id].start_task.emit(index, cishu_max)
                self.isRunning[thread_id]=True
                self.workers[thread_id].isRunning=True
                pushButton_start.setText('停止')
                pushButton_restart.setEnabled(False)
        elif not listWidget.selectedItems():
            #没有选择任何脚本
            textBrowser.append('无效选项')
    def worker_finished(self,thread_id):
        self.tab[thread_id].textBrowser.append('Worker finished')
        #self.workers[thread_id].quit()  # Wait for thread to fully exit
        return
    def thread_finished(self,thread_id):
        textBrowser=self.tab[thread_id].textBrowser
        pushButton_start=self.tab[thread_id].pushButton_start
        pushButton_restart=self.tab[thread_id].pushButton_restart
        # Thread stays alive - just update UI (don't quit or delete)
        self.workers[thread_id].isRunning=False
        self.isRunning[thread_id]=False

        #计时
        t_end = time.time()
        if self.t_start[thread_id]:
            hours, rem = divmod(t_end-self.t_start[thread_id], 3600)
            minutes, seconds = divmod(rem, 60)
            textBrowser.append('运行时间：{:0>2}:{:0>2}:{:0>2}'.format(int(hours),int(minutes),int(seconds)))
        textBrowser.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        #更新日志/按键
        pushButton_start.setText('开始')
        pushButton_restart.setEnabled(True)
        textBrowser.append('脚本已结束！')
        action.alarm(1)
        
        pushButton_start.setEnabled(True)
        pushButton_restart.setEnabled(True)
    
    #屏幕截图和保存
    def screen_show(self,thread_id):
        from PyQt6.QtGui import QPixmap, QImage
        textBrowser=self.tab[thread_id].textBrowser
        #截屏
        screen=action.screenshot(thread_id)
        if isinstance(screen, int) and screen == -1:
            textBrowser.append('截图失败')
            return
        textBrowser.append(f'截图分辨率: {screen.shape[1]}x{screen.shape[0]}')
        screen = screen[0:screen.shape[0], 0:screen.shape[1]]
        h, w, ch = screen.shape
        bytesPerLine = ch * w
        image = QImage(screen.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        #save image
        if image.save('screenshot.png'):
            textBrowser.append('已保存截图到 screenshot.png')
        else:
            textBrowser.append('保存截图失败')

        # Create a popup window to display the screenshot
        popup = QDialog()
        popup.setWindowTitle('屏幕截图')
        popup_label = QLabel()
        popup_label.setPixmap(QPixmap.fromImage(image))
        popup_layout = QVBoxLayout()
        popup_layout.addWidget(popup_label)
        popup.setLayout(popup_layout)
        popup.adjustSize()
        popup.exec()
        
####################################################
if __name__ == '__main__':
    # 初始化设置
    # Try multiple locations for config.ini: current working dir, bundled resources, script dir
    candidates = [os.path.join(os.getcwd(), 'config.ini'), resource_path('config.ini'), os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')]
    config_path = None
    for c in candidates:
        if os.path.exists(c):
            config_path = c
            break
    if not config_path:
        print('config.ini not found; using built-in defaults')
        # Provide reasonable defaults so the exe can run without external config
        config = configparser.ConfigParser(inline_comment_prefixes=';')
        config['general'] = {
            'Nthread': '2',
            'debug': 'False',
            'game': 'yys'
        }
    else:
        print('Using config:', config_path)
        config = configparser.ConfigParser(inline_comment_prefixes=';')
        config.sections()
        config.read(config_path)
    #inputs from terminal
    parser = argparse.ArgumentParser(description='Input parameters')
    parser.add_argument('-game', '--game', help='游戏名称')
    parser.add_argument('-debug', '--debug', type=int, help='Debug模式')
    parser.add_argument('--gui-test', action='store_true', help='Show a simple GUI test message box and exit')
    args = parser.parse_args()
    #debug模式
    debug_enabled = config['general']['debug'].lower() in ['true', '1', 'yes']
    if args.debug is not None:
        debug_enabled = str(args.debug) in ['1']
    if debug_enabled:
        import faulthandler
        faulthandler.enable()
    #游戏名
    game_name=config['general']['game']
    if args.game:
        game_name=args.game
    print(f'加载游戏脚本文件: {game_name}')
    # Add directory into module search list. When bundled, put the extracted resources path.
    game_path_candidate = resource_path(game_name)
    if os.path.isdir(game_path_candidate):
        sys.path.insert(0, game_path_candidate)
    else:
        # Fall back to original behavior (development environment)
        sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), game_name))

    # Import the game module and log detailed errors if it fails
    try:
        game = importlib.import_module(game_name)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log_path = resource_path('error.log') if getattr(sys, 'frozen', False) else os.path.join(os.path.abspath(os.path.dirname(__file__)), 'error.log')
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('Failed to import game module:\n')
                f.write(tb)
        except Exception:
            pass
        print('Error importing game module:', e)
        print('Traceback written to', log_path)
        sys.exit(1)
    #总设备数量
    nthread=int(config['general']['Nthread'])
    print('线程总数量：',nthread)
    #初始化所有线程
    #action.init_thread_variable(nthread)
    #GUI
    app = QApplication(sys.argv)
    # Quick GUI test if requested (helps verify bundled Qt works)
    if args.gui_test:
        QMessageBox.information(None, 'GUI Test', 'GUI is working (test).')
        sys.exit(0)
    window = MainWindow(nthread)
    window.show()
    #检测系统
    print(f'操作系统: {sys.platform}')
    
    #pyautogui.PAUSE = 0.05
    #pyautogui.FAILSAFE=False

    sys.exit(app.exec())

