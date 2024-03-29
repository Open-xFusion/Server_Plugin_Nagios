# coding=utf-8

import ConfigParser
import getpass
import os
import sys
import const_info
import data_info
import commands

'''
' 文件操作类异常
' handle: 处理文件操作异常信息类, 
'''


class FileExcept(Exception):
    pass


'''
' 读取文件信息
' methods: readKey 读取目标文件信息
' return: 返回文件信息    
'''


def find_nagiosdir():
    # return nagios directory
    cmd = "source /etc/profile;echo $NAGIOSHOME"
    procs = commands.getoutput(cmd)
    return procs


def readKey():
    file = None
    try:
        # k文件路径
        kfilepath = find_nagiosdir() + os.path.sep + 'etc' + os.path.sep \
                    + 'XFUSION_server' + os.path.sep \
                    + 'configInfo.cfg'
        file = open(kfilepath, const_info.FILE_R)
        key = file.readline()
    
    except IOError, err:
        raise FileExcept(data_info.WRITE_FILE_ERROR + str(err))
    except Exception, err:
        raise FileExcept(
            data_info.WRITE_FILE_UNKNOWN + str(err))
    finally:
        if file is not None:
            file.close()
    if key is not None:
        return key
    else:
        return const_info.DATA_CONS


'''
' 加密信息
' methods: encryptKey 待加密字符串
' return: 返回加密字符串    
'''


def encryptKey(pkey, rootkey):
    encryptStr = None
    if rootkey is not None:
        encryptStr = os.popen(
            "echo " + "'" + pkey + "'" + " | openssl aes-256-cbc -k " + "'" + rootkey + "'" + " -base64") \
            .read().strip()
    return encryptStr


'''
' 解密信息
' methods: encryptKey 解密加密字符串
' return: 返回解密字符串    
'''


def dencryptKey(pkey, rootkey):
    encryptStr = None
    if rootkey is not None:
        encryptStr = os.popen("echo " + "'" + pkey + "'"
                              + " | openssl aes-256-cbc -d -k " + "'"
                              + rootkey + "'" + " -base64").read().strip()
    return encryptStr


'''
' 读取文件信息
' methods: genRootKeyStr 读取目标文件信息
' return: 返回文件信息
'''


def genRootKeyStr():
    file = None
    configfilepath = find_nagiosdir() + os.path.sep + 'etc' + os.path\
        .sep + 'XFUSION_server' + os.path.sep + 'initial.cfg'
    parser = ConfigParser.ConfigParser()
    configdata = {}
    try:
        file = open(configfilepath, const_info.FILE_R)
        parser.readfp(file)
        for section in parser.sections():
            for (key, value) in parser.items(section):
                configdata[key] = value
        rootkey = configdata.get(const_info.NAGIOS_CONTANT3)

    except IOError, err:
        file.close()
        raise FileExcept(data_info.OPEN_FILE_ERROR + '\n' + str(err))
    except FileExcept, err:
        file.close()
        raise
    except Exception, err:
        file.close()
        raise FileExcept(data_info.INITIAL_FILE + '\n' + str(err))
    finally:
        if file is not None:
            file.close()
    try:
        if rootkey is not None:
            key = data_info.CONSTANT1 + rootkey + const_info.CONSTANT2
            return key
    except Exception, err:
        raise FileExcept(data_info.ROOTKEY_UNKNOWN + '\n' + str(err))


'''
' 工具方法，加密用户密码信息
' methods: encryptPwd 加密用户需要的信息
' return: 加密密文
'''


def encryptPwd():
    if len(sys.argv) == 2 and "encryptPwd" == sys.argv[1]:
        pkey = getpass.getpass(data_info.INPUT_PWD)
        
        try:
            if pkey is not None:
                key = readKey()
                rootKey = genRootKeyStr()
                k = dencryptKey(key, rootKey)
                print encryptKey(pkey, k)
                return
        except FileExcept:
            print data_info.PWD_UNKNOWN


encryptPwd()
