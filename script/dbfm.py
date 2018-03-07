#!/usr/bin/python

#import gevent
#from gevent import monkey; monkey.patch_socket()
import urllib2
import yajl
import os, sys, socket
#from multiprocessing import Process, Queue, Value, Array

sock_file = '/tmp/dbfm.sock'
mypid = "mypid"

def down_mp3(url, ssid):
    fu = urllib2.urlopen(url)
    data = fu.read()
    with open('/tmp/%s.mp3'%ssid, 'wb') as f:
        f.write(data)

def play_mp3(ssid):
    os.system('cvlc /tmp/%s.mp3 --play-and-exit >/dev/null 2>&1'%ssid)

def down_list():
    pl_url = "https://douban.fm/j/v2/playlist?channel=-10&kbps=192&client=s%3Amainsite%7Cy%3A3.0&app_name=radio_website&version=100&type=n"
    #pl_url = "http://douban.fm/j/mine/playlist?type=n&h=|432599:p&channel=1&from=mainsite&r=ecc38a4d94"
    pl_f = urllib2.urlopen(pl_url)
    data = pl_f.read()
    pl = yajl.loads(data)
    pl_f.close()
    return pl['song']

def listening():
    current_status = 'init'
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(sock_file)
        s.listen(5)
        while True:
            conn, addr = s.accept()
            try:
                conn.settimeout(5)
                data = conn.recv(1024)
                if data == 'get':
                    conn.send(current_status)
                elif data.startswith('set'):
                    current_status = data.split(':')[1]
                    conn.send('OK')
                elif data == 'stop':
                    print str(os.getpid()) + ' listener stoped'
                    break
            except socket.timeout:
                pass
                print 'time out'
            conn.close
    finally:
        os.unlink(sock_file)

def play_list():
    while True:
        pl = down_list()
        for song in pl:
            try:
                s_url, s_ssid, s_title = song['url'], song['ssid'], song['title']
                down_mp3(s_url, s_ssid)
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(sock_file)
                s.send("set:%s"%s_title.encode('utf-8'))
                data = s.recv(1024)
                s.close()
            except IOError as e:
                print str(os.getpid()) + ' player stopped'
                return
            try:
                play_mp3(s_ssid)
                #print s_url, s_ssid, s_title
            except BaseException as e:
                print e
                continue

def check_status():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock_file)
    s.send("get")
    data = s.recv(1024, 0)
    s.close()
    print '[%s]'%data

def main():
    global mypid

    if os.path.exists(sock_file):
        try:
            check_status()
            print mypid + ' checked status and returned'
            return 'Tks God'
        except BaseException as e:
            print e
    else:
        print 'starting with everything clear'

    pid = os.fork()
    if pid:
        print mypid + ' forked ' + str(pid) + ' and returned'
        return 'init'

    mypid = str(os.getpid())
    pid2 = os.fork()
    if pid2:
        print mypid + ' forked ' + str(pid2) + ' and is listening' 
        listening()
    else:
        print str(os.getpid()) + ' is playing list'
        play_list()

def stop():
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(sock_file)
        s.send("stop")
        data = s.recv(1024, 0)
        s.close()
        os.system("ps -ef|grep vlc|grep mp3|awk '{print $2}'|xargs kill")
    except IOError as e:
        pass
    finally:
        print 'stop signal has been sent'

mypid = str(os.getpid())
print 'my pid is ' + mypid

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == 'stop':
        stop()
    else:
        main()

