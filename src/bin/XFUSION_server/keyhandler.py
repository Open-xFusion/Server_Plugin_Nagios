# coding=utf-8

import os
import sys
import getpass
import ConfigParser
import re
import const_info
import data_info

'''
' 字符串校验异常类
' handle: 处理文件操作异常信息类, 
'''


class CheckExcept(Exception):
    pass


'''
' 文件操作类异常
' handle: 处理文件操作异常信息类, 
'''


class FileExcept(Exception):
    pass


'''
' 读取文件信息
' methods: genRootKeyStr 读取目标文件信息
' return: 返回文件信息
'''


def genRootKeyStr():
    configfilepath = '../../etc' + os.path.sep \
                     + 'XFUSION_server' + os.path.sep \
                     + 'initial.cfg'
    parser = ConfigParser.ConfigParser()
    configdata = {}
    file = None
    try:
        file = open(configfilepath, const_info.FILE_R)
        parser.readfp(file)
        for section in parser.sections():
            for (key, value) in parser.items(section):
                configdata[key] = value
        rootkey = configdata.get(const_info.NAGIOS_CONTANT3)

    except IOError, err:
        raise FileExcept(data_info.OPEN_FILE_ERROR + '\n' + str(err))
    except FileExcept:
        raise
    except Exception, err:
        raise FileExcept(data_info.INITIAL_FILE + '\n' + str(err))
    finally:
        if file is not None:
            file.close()

    if rootkey is not None:
        key = data_info.CONSTANT1 + rootkey + const_info.CONSTANT2
        return key
    else:
        return ""


'''
' 写入文件信息
' methods: writeKey 写入目标文件
' return: void
'''


def writeKey(pkey):
    file = None
    try:
        if pkey == "":
            pkey = const_info.DATA_CONS
        kfilepath = '../../etc' + os.path.sep \
                    + 'XFUSION_server' + os.path.sep \
                    + 'configInfo.cfg'
        file = open(kfilepath, const_info.FILE_W)
        file.write(pkey)
    except IOError, err:
        raise FileExcept(data_info.WRITE_FILE_ERROR
                         + str(err))
    except Exception, err:
        raise FileExcept(data_info.WRITE_FILE_UNKNOWN + str(err))
    finally:
        if file is not None:
            file.close()


'''
' 加密信息
' methods: encryptKey 加密信息
' return: 加密密文
'''


def encryptKey(pkey, rootkey):
    global encryptStr
    if rootkey is not None:
        encryptStr = os.popen(
            "echo " + "'" + pkey + "'" + " | openssl aes-256-cbc -k " + "'" + rootkey + "'" + " -base64") \
            .read().strip()
    return encryptStr


# 判断密码长度
def checklen(key):
    return 8 <= len(key) <= 32


# 判断密码是否存在大写字母
def checkContainUpper(key):
    pattern = re.compile('[A-Z]+')
    match = pattern.findall(key)
    if match:
        return True
    else:
        return False


# 判断密码是否存在小写字母
def checkContainLower(key):
    pattern = re.compile('[a-z]+')
    match = pattern.findall(key)
    if match:
        return True
    else:
        return False


# 判断密码是否存在数字
def checkContainNum(key):
    pattern = re.compile('[0-9]+')
    match = pattern.findall(key)
    if match:
        return True
    else:
        return False


# 判断是否存在特殊文字
def checkSymbol(key):
    pattern = re.compile('[^a-z0-9A-Z]+')
    match = pattern.findall(key)
    if match:
        return True
    else:
        return False


# 校验密码安全性
def checkKeyInfo(key):
    lenOk = checklen(key)
    upperOk = checkContainUpper(key)
    lowerOk = checkContainLower(key)
    numOk = checkContainNum(key)
    symbolOk = checkSymbol(key)

    return lenOk and upperOk and lowerOk and numOk and symbolOk


'''
' 工具方法，设置秘钥信息
' methods: setKey 设置用户秘钥信息
' return: 加密密文
'''


def setKey():
    if (len(sys.argv) == 2 and (
            'setKey' == sys.argv[1] or 'setkey' == sys.argv[1])):
        pkey = getpass.getpass(data_info.INPUT_KEY)

        rootkey = genRootKeyStr()
        try:
            if pkey is not None and checkKeyInfo(pkey):
                encryptStr = encryptKey(pkey, rootkey)
                writeKey(encryptStr)
                print encryptStr
                return
            else:
                print data_info.MSG_KEYWORD1
                print data_info.MSG_KEYWORD2
        except CheckExcept:
            print data_info.MSG_KEYWORD1
            print data_info.MSG_KEYWORD2


setKey()
