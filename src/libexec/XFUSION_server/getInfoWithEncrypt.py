# coding=utf-8
import os
import sys
import commands
import time
import re
import ConfigParser
from optparse import OptionParser

from getInfoForBlade import InfoHandler as bladeInfoHandler
from getInfo import InfoHandler as rackInfoHandler
from getInfoForBlade import MSG_HEASTATUS

STATUS_UNKNOWN = 3
COMPONENT_POWER = "power"
COMPONENT_BLADE = "blade"
COMPONENT_FAN = "fan"
COMPONENT_SYS = "system"
COMPONENT_SWI = "switch"
COMPONENT_SMM = "smm"
COMPONENT_SHELF = "shelf"
COMPONENT_CPU = "cpu"
COMPONENT_MEMORY = "memory"
COMPONENT_DISK = "hardDisk"
COMPONENT_RAID = "raid"


class FileExcept(Exception):
    pass


def find_nagiosdir():
    '''return nagios directory'''
    cmd = "source /etc/profile;echo $NAGIOSHOME"
    procs = commands.getoutput(cmd)
    return procs


nagiosHome = find_nagiosdir()
genkeyPath = nagiosHome + os.path.sep + "bin" + os.path.sep + "XFUSION_server"
sys.path.append(genkeyPath)

TRAP_BINDING_VALUE_SEP = "[,;/-]"
BINDING_KEY_VALUE_SEP = ':'
CMD_FILE_NAME_SEP = '_'
CMD_FILE_CONTENT_SEP = '&'
NAGIOS_CMD_SEP = ';'
NAGIOS_CMD_SIGN = 'PROCESS_SERVICE_CHECK_RESULT'
NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT = '['
NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT = ']'


def constructMessage(host, service, status, info):
    return NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT \
           + str(time.time()) \
           + NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT + ' ' \
           + NAGIOS_CMD_SIGN + NAGIOS_CMD_SEP \
           + host + NAGIOS_CMD_SEP \
           + service + NAGIOS_CMD_SEP \
           + str(status) + NAGIOS_CMD_SEP \
           + info \
           + '\n'


def getCmdfilePath():
    nagioscmd_file = None
    initfilePath = os.path.normpath(sys.path[
                                        0]) + "/../.." + os.path.sep + "etc" + os.path.sep + "XFUSION_server/initial.cfg"
    initial_cfg = open(initfilePath)
    for pro in initial_cfg:
        if re.findall(r'^\s*nagios_cmd_file\s*=\s*/', pro):
            nagioscmd_file = re.sub(r'\s*$', '', pro.split('=')[1])
    if nagioscmd_file is not None:
        return nagioscmd_file
    else:
        return None


def writeCmd(host, service, status, info):
    file = None
    try:
        file = open(getCmdfilePath(), 'a')
        nagioscmd = constructMessage(host, service, status, info)
        file.write(nagioscmd)
    except Exception, err:
        print "writeCmd error: " + str(err)
    finally:
        if file is not None:
            file.close()


def dencrypt(str):
    k = dencryptKey(readKey(), genRootKeyStr())
    decryotStr = dencryptKey(str, k)

    if decryotStr is None:
        return ''
    else:
        return decryotStr


def genRootKeyStr():
    file = None
    configfilepath = find_nagiosdir() + os.path.sep + 'etc' + os.path.sep\
                     + 'XFUSION_server' + os.path.sep\
                     + 'initial.cfg'
    parser = ConfigParser.ConfigParser()
    configdata = {}
    try:
        file = open(configfilepath, 'r')
        parser.readfp(file)
        for section in parser.sections():
            for (key, value) in parser.items(section):
                configdata[key] = value
        rootkey = configdata.get("nagios_costant3")
        if rootkey is not None:
            key = 'Hu' + rootkey + '#$'
            return key
    except IOError, err:
        raise FileExcept('Open initial file error.\n' + str(err))
    except Exception, err:
        raise FileExcept('Initial file invalid. Unknown error when read rootKey. Cause:\n' + str(err))
    finally:
        if file is not None:
            file.close()


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
        file = open(kfilepath, 'r')
        key = file.readline()
        if key is not None:
            return key
        else:
            return 'U2FsdGVkX1+WNo4EfeY33VTp5dLeaUh5vKeQ44sUCzE='
    except IOError, err:
        raise FileExcept('Write warning file error. Cause: \n' + str(err))
    except Exception, err:
        raise FileExcept(
            'Unknown error when writing warning file. Cause: \n' + str(err))
    finally:
        if file is not None:
            file.close()


def dencryptKey(pkey, rootkey):
    encryptStr = None
    if rootkey is not None:
        encryptStr = os.popen("echo " + "'" + pkey + "'"
                              + " | openssl aes-256-cbc -d -k " + "'"
                              + rootkey + "'" + " -base64").read().strip()
    return encryptStr


def commandParse():
    opts = {}
    parser = OptionParser()
    parser.add_option("-c", "--component", dest="component",
                      help="component for check  as (hardDisk,cpu,memory,power,cpu,memory,fan,system,hardDisk)",
                      default="system")
    parser.add_option("-H", "--host", dest="host",
                      help="Hostname or IP address of the host to check",
                      default=None)
    parser.add_option("-v", "--version", dest="version",
                      help="SNMP Version to use (1, 2c or 3)", default="3")
    parser.add_option("-u", "--user", dest="user",
                      help="SNMP username (only with SNMP v3)", default=None)
    parser.add_option("-C", "--community", dest="community",
                      help="SNMP Community (only with SNMP v1|v2c)",
                      default=None)
    parser.add_option("-p", "--port", dest="port",
                      help="port for SNMP", default="161")
    parser.add_option("-A", "--apwd", dest="apwd",
                      help="SNMP authentication password (only with SNMP v3)",
                      default=None)
    parser.add_option("-a", "--aprotocol", dest="aprotocol",
                      help="SNMP authentication protocol (SHA only with SNMP v3)",
                      default="SHA")
    parser.add_option("-X", "--ppwd", dest="ppwd",
                      help="SNMP privacy password (only with SNMP v3)",
                      default=None)
    parser.add_option("-x", "--pprotocol", dest="pprotocol",
                      help="SNMP privacy protocol AES||DES (only with SNMP v3)",
                      default='AES')
    parser.add_option("-l", "--seclevel", dest="seclevel",
                      help="SNMP security level (only with SNMP v3) (noAuthNoPriv|authNoPriv|authPriv)",
                      default="authPriv")
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="Timeout in seconds for SNMP", default="10")
    parser.add_option("-T", "--type", dest="type",
                      help="service types as (blade, rack)", default="blade")
    parser.add_option("-r", "--retry", dest="retry",
                      help="Timeout in seconds for SNMP", default="2")
    parser.add_option("-o", "--vendorid", dest="vendorid",
                      help="vendor id. 1, 2 or None", default=None)
    (opts, args) = parser.parse_args()
    compenlist = [COMPONENT_POWER, COMPONENT_FAN, COMPONENT_SYS,
                  COMPONENT_SWI, COMPONENT_SMM, COMPONENT_SHELF, COMPONENT_BLADE]
    if opts.type.upper() == "RACK" or opts.type.upper() == "HIGHDENSITY":
        compenlist = [COMPONENT_POWER, COMPONENT_FAN, COMPONENT_SYS,
                      COMPONENT_CPU, COMPONENT_MEMORY, COMPONENT_DISK, COMPONENT_RAID]
    if opts.host is None:
        print "please input Hostname or IP "
        exit(STATUS_UNKNOWN)
    if opts.version == '3' and opts.user is None:
        print "please input SNMP username  "
        exit(STATUS_UNKNOWN)
    if opts.ppwd is None:
        opts.ppwd = opts.apwd
    if opts.component not in compenlist:
        print " -c  only support as : "
        for eachitem in compenlist:
            print eachitem
        exit(STATUS_UNKNOWN)
    if opts.apwd is not None:
        opts.apwd = dencrypt(opts.apwd)
    if opts.ppwd is not None:
        opts.ppwd = dencrypt(opts.ppwd)
    if opts.community is not None:
        opts.community = dencrypt(opts.community)

    return opts


if __name__ == '__main__':
    opts = commandParse()

    try:
        if opts.type.lower() == 'blade':
            infoHandler = bladeInfoHandler(opts)
            status, info = infoHandler.getAllStatus(
                infoHandler._Parm.component)
            writeCmd(infoHandler._Parm.host,
                     infoHandler._Parm.component.lower(), status,
                     ("%s HealthStatus: %s " % (
                         str(infoHandler.Parm.component),
                         MSG_HEASTATUS[status])) + info.replace('\n', "===="))
        else:
            infoHandler = rackInfoHandler(opts)
            status, info = infoHandler.getRaidStatus()
        print "%s HealthStatus: %s " % (
            str(infoHandler._Parm.component), MSG_HEASTATUS[status])
        print "=============================== info " \
              "============================= "
        print info
        exit(status)
    except Exception, e:
        print "Unhandled exception while running script: %s" % e
        exit(STATUS_UNKNOWN)
