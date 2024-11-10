感谢anywheretogo大佬提供的脚本框架，此脚本在原作基础上加入了很多功能，也修复了一些问题。开发测试均基于体验服，平台为电脑桌面版和安卓（支持模拟器和实体机多开）。本人体验服玩家，所以活动会根据体服尽快更新。

1. 安装python
此脚本兼容Windows/Mac系统，并支持ADB使用模拟器，对于不了解python的用户，首先要安装python官方的必要安装包。下载地址: [Python 3.12.4](https://www.python.org/downloads/release/python-3124/)， 选择对应的系统安装文件。

2. 配置程序环境
安装好python后还需要另外安装4个python库，分别是opencv-python，pyautogui，mss，pyqt6。这个步骤Windows和Mac略有不同：
Windows/Linux：打开命令行（cmd）或者powershell，然后运行：pip install -r requirements.txt
Mac：在终端（terminal）下运行：pip3 install -r requirements.txt

3. 运行脚本
推荐系统自带的终端Terminal，使用python3 yys.py 方式运行。推荐使用雷电模拟器因为会自动设置ADB地址，MuMu模拟器会相对麻烦一些需要手动输入ADB端口。
桌面版必须使用原始分辨率即1136x640（安卓/模拟器会自动设置成桌面版分辨率），其它分辨率则需要重新截图才能正常工作。另外桌面版（非模拟器）游戏窗口务必要移动到左上角。

如果有任何问题请在讨论区发帖。解放双手 Have fun!
