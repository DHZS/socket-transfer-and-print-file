# -*- coding: utf-8 -*-

'文件发送方'

import socket
import threading
import header
import os
import sys


def transfer_file(sock, file_path, print_type):
    '发送文件'

    # 准备发送文件
    sock.send(header.SEND_FILE)

    # 打开的文件
    fp = None

    while True:
        data = header.unpack_msg(sock.recv(1024))

        if data[0] == header.RECV_FILE:
            # 可以发送文件了，先发送文件信息
            file_size = os.path.getsize(file_path)
            file_name = os.path.split(file_path)[1]
            print u'INFO:文件名: {}, 文件大小: {}'.format(file_name, file_size)

            #发送文件信息
            sock.send(header.FILE_INFO + file_name.encode('utf-8') + header.SPLIT \
              + str(file_size) + header.SPLIT + str(print_type))

        elif data[0] == header.START_TRANSFER:
            # 开始传输文件，读入文件
            try:
                fp = open(file_path, 'rb')
            except:
                raise BaseException(u'读取文件失败')
            
            # 发送第一段数据
            buffer = fp.read(1000)
            sock.send(header.DATA + buffer)
        
        elif data[0] == header.NEXT:
            # 发送下一段数据
            buffer = fp.read(1000)
            if buffer != '':
                sock.send(header.DATA + buffer)
            else:
                # 文件传输完毕
                sock.send(header.STOP_TRANSFER)
                fp.close()
                break
        
        elif data[0] == header.NONE:
            raise BaseException(u'未知的 header')




if __name__ == '__main__':

    try:
        if len(sys.argv) != 4:
            print u'ERROR:参数个数不正确'
            os._exit(0)
        
        # 获取 ip，文件路径，打印类型
        ip, file_path, print_type = sys.argv[1], sys.argv[2].decode('gbk').strip(), int(sys.argv[3])

        if not os.path.isfile(file_path):
            raise BaseException(u'文件不存在')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 建立连接
        s.connect((ip, 8899))

        # 发送文件
        transfer_file(s, file_path, print_type)
        s.close()

        print u'SUCCESS'
    except socket.gaierror as e:
        print u'ERROR:socket 连接错误'
    except BaseException as e:
        message = u'未知错误' if e.message == '' or e.message == None else e.message
        print u'ERROR:{}'.format(message)


