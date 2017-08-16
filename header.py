# -*- coding: utf-8 -*-

'标识信息'

'准备发送'
SEND_FILE = '[SEND]'
'准备接收'
RECV_FILE = '[RECV]'
'文件信息'
FILE_INFO = '[INFO]'
'数据分隔符'
SPLIT = '[SPLT]'
'开始传输'
START_TRANSFER = '[STAR]'
'传输数据'
DATA = '[DATA]'
'请求下一段数据'
NEXT = '[NEXT]'
'结束传输'
STOP_TRANSFER = '[STOP]'
'未知header'
NONE = '[NONE]'


def unpack_msg(msg):
    '解包消息'
    length = len(msg)
    if length < 6:
        return (NONE, )
    
    header = msg[0:6]

    if header in (SEND_FILE, RECV_FILE, START_TRANSFER, STOP_TRANSFER, NEXT):
        return (header, )
    
    if header == FILE_INFO:
        pos1 = msg.find(SPLIT)
        if pos1 == -1:
            return (NONE, )
        pos2 = msg.find(SPLIT, pos1 + 1)
        if pos2 == -1:
            return (NONE, )
        file_name = msg[6:pos1].decode('utf-8').strip()
        file_size = msg[pos1+6:pos2]
        print_type = msg[pos2+6:]
        return (FILE_INFO, file_name, int(file_size), int(print_type))
    
    if header == DATA:
        return (DATA, msg[6:], len(msg[6:]))
    
    return (NONE, )
    

