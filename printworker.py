# -*- coding: utf-8 -*-

import win32ui
import win32print
import win32con
import win32api
import json
import os


class PrintWorker(object):
    '打印工作类'

    def __init__(self, config_file_name, print_config_enum):
        # 配置文件路径
        # self.config_file_path = self.__get_config_path(config_file_name)
        self.config_file_path = config_file_name
        # 可用打印配置取值
        self.print_config_enum = print_config_enum
        # 打印配置
        self.config = None

    
    def __get_config_path(self, file_name):
        '获取配置文件路径'
        path = os.path.split(os.path.realpath(__file__))[0]
        file_path = os.path.join(path, file_name)
        return file_path
    

    def __load_config(self):
        '获取打印配置'

        config = None
        # 获取 config
        if os.path.isfile(self.config_file_path):
            try:
                fp = open(self.config_file_path, 'r')
                config = json.load(fp)
                if config != None and isinstance(config, dict):
                    for key in config.iterkeys():
                        # 如果 key 为 str 类型，转为 int 类型，方便取值
                        if isinstance(key, basestring):
                            config[int(key)] = config[key]
                            config.pop(key)
                else:
                    config = None
            except:
                config = None
            finally:
                try:
                    if fp != None:
                        fp.close()
                except:
                    pass
                
        if config != None:
            for value in self.print_config_enum:
                if value not in config:
                    return False
            self.config = config
            return True
        else:
            return False

    
    def __save_config(self):
        '保存配置'

        # 写入配置
        try:
            fp = open(self.config_file_path, 'w+')
            json.dump(self.config, fp)
            fp.close()
            return True
        except BaseException as e:
            try:
                if fp != None:
                    fp.close()
            except:
                pass
        return False
    
    def init_print_config(self):
        '初始化打印配置'

        # 获取打印机列表
        printer_list = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            printer_list.append(printer[2].decode('gbk'))
        
        if len(printer_list) == 0:
            print u'ERROR:未找到可用的打印机'
            return False
        
        # 获取配置
        is_correct = True  # 配置的打印机是否存在
        if self.__load_config() == True:
            for value in self.print_config_enum:
                if self.config[value] not in printer_list:
                    is_correct = False
                    break
        
        # 检查配置
        if self.config == None:
            print ''
            print u'请配置打印机'
        if is_correct == False:
            print ''
            print u'未找到配置文件中指定的打印机，请重新配置'
        if self.config == None or is_correct == False:
            # 配置不存在或有误，重新配置
            self.config = {}
            print u'可用打印机列表：'
            for i, printer in enumerate(printer_list):
                print u'{}. {}'.format(i + 1, printer_list[i])
            for value in self.print_config_enum:
                no = None
                # 检测输入是否有误，如错误重复输入
                while True:
                    print ''
                    print u'请输入当打印配置为 {} 时使用的打印机编号：'.format(value)
                    try:
                        no = int(raw_input())
                        if no < 1 or no > len(printer_list):
                            raise BaseException()
                        else:
                            break
                    except:
                        print u'ERROR:您的输入有误，请检查'
                        continue
                self.config[value] = printer_list[no-1]
            print ''
            
            # 保存配置
            if self.__save_config() == False:
                print u'ERROR:写入配置失败'
                return False
            
        return True

    
    def print_file(self, file_path, print_type):
        '打印文件'

        file_path = file_path.strip('" \t\r\n')
        if not os.path.isfile(file_path):
            print u'ERROR:打印的文件不存在，文件路径：{}'.format(file_path)
            return False
        
        if print_type not in self.config:
            print u'ERROR:打印配置 {} 不存在'.format(print_type)
            return False

        try:
            win32api.ShellExecute(0,'printto', file_path, u'"{}"'.format(self.config[print_type]), '.', 0)
            return True
        except BaseException as e:
            print u'ERROR:执行打印任务出错'
        return False
        










if __name__ == '__main__':
    # 配置文件名称
    config_file_name = 'print_config.txt'
    # 可用打印配置取值
    print_config_enum = [1, 2, 3]
    print_worker = PrintWorker(config_file_name, print_config_enum)
    if print_worker.init_print_config():
        print u'选择打印机配置：'
        no = int(raw_input())
        print u'输入打印的文件路径：'
        file_path = raw_input().decode('gbk')
        if print_worker.print_file(file_path, no):
            print u'打印成功'



