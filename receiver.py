# -*- coding: utf-8 -*-

'文件接收方'

import socket
import threading
import header
import os

from printworker import PrintWorker


def transfer_file(sock, path):
    '接收文件'

    # 文件大小
    file_size = None
    # 已接收文件大小
    recv_size = 0
    # 待保存文件的路径
    save_file_path = None
    # 接收的文件
    fp = None
    # 打印类型
    print_type = None
    
    while True:
        data = header.unpack_msg(sock.recv(1024))
    
        if data[0] == header.SEND_FILE:
            # 收到准备发送文件信息，回复消息，可以开始发送了
            sock.send(header.RECV_FILE)
        
        elif data[0] == header.FILE_INFO:
            # 收到文件信息
            # 文件名
            file_name = data[1]
            file_size = data[2]
            print_type = data[3]
            print u'INFO:文件名: {}, 文件大小: {}, 打印类型: {}'.format(file_name, file_size, print_type)

            # 检查文件名是否存在
            name_ext = os.path.splitext(file_name)
            i = 0
            while True:
                node = ' (' + str(i) + ')' if i != 0 else ''
                save_file_path = os.path.join(path, name_ext[0] + node + name_ext[1])
                if os.path.exists(save_file_path) or os.path.exists(save_file_path + '.tmp'):
                    # 文件已存在
                    i += 1
                    continue
                else:
                    file_name = name_ext[0] + node + name_ext[1]
                    break
            
            # 创建文件
            try:
                fp = open(save_file_path + '.tmp', 'wb+')
            except:
                raise BaseException(u'创建文件 {} 失败'.format(file_name + '.tmp'))
            
            # 发送消息，开始传输
            sock.send(header.START_TRANSFER)
        
        elif data[0] == header.DATA:
            # 接收到数据
            fp.write(data[1])
            recv_size += data[2]

            # print u'INFO:接收数据 {}/{}'.format(recv_size, file_size)

            sock.send(header.NEXT)
        
        elif data[0] == header.STOP_TRANSFER:
            # 文件接收完毕
            fp.close()
            os.rename(save_file_path + '.tmp', save_file_path)
            break
        
        elif data[0] == header.NONE:
            raise BaseException(u'未知的 header')
    
    # 接收文件完毕，返回保存路径，打印类型
    return save_file_path, print_type


if __name__ == '__main__':
    # 打印配置
    # 配置文件名称
    config_file_name = 'print_config.txt'
    cur_path = os.path.split(os.path.realpath(__file__))[0]
    config_file_path = os.path.join(cur_path, config_file_name)
    # 可用打印配置取值
    print_config_enum = [1, 2, 3]
    print_worker = PrintWorker(config_file_path, print_config_enum)
    if print_worker.init_print_config() == False:
        os._exit(0)

    # socket
    s = None

    # 获取用户目录
    path = os.path.expanduser('~').decode('gbk').strip()
    print u'INFO:用户目录 {}\n'.format(path)

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 监听端口
            s.bind(('0.0.0.0', 8899))
            # 最大监听数量
            s.listen(1)

            while True:
                # 接受一个新连接
                sock, addr = s.accept()

                # 接收文件
                save_file_path, print_type = transfer_file(sock, path)
                print u'INFO:文件目录:{}, 打印类型:{}'.format(save_file_path, print_type)
                if print_worker.print_file(save_file_path, print_type):
                    print u'INFO:文件打印成功'
                    print u'SUCCESS\n'
                else:
                    print u'ERROR:文件打印失败\n'
        
        except BaseException as e:
            message = u'未知错误' if e.message == '' or e.message == None else e.message
            print u'ERROR:{}\n'.format(message)
        finally:
            if s != None:
                try:
                    s.close()
                except:
                    pass



