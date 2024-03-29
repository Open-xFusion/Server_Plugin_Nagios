# coding=utf-8
'''
Created on 2018-1-18

'''

import sys
import os
import re
import commands
import ConfigParser
import genKey
from optparse import OptionParser
import time
from model.host import Host
from base.channel import Channel
from constant.constant import NAGIOS_ERROR_SUCCESS

from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACMD5AuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmDESPrivProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACSHAAuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmAesCfb128Protocol
from xml.dom import minidom
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import OctetString, IpAddress
from pysnmp.proto.rfc1902 import Integer

############## PLUGIN VERSION ###########################

VERSTION_STR = "XFUSION PLUGIN V1.1.2"
################################################

DEBUG = False


def debugPrint(StrforPrint):
    if DEBUG:
        print StrforPrint
    else:
        pass
    
    # +++++++++++++const for cmd options ++++++++++++++++++++++++++++


CFG_NODE_KEY_HOST_NAME = "hostName"
CFG_NODE_KEY_DEVTYPE = "type"
CFG_NODE_KEY_VENDORID = "vendorId"
CFG_NODE_KEY_PPORT = "port"
CFG_NODE_KEY_CSNMPVERSION = "CSnmp"
CFG_NODE_KEY_CUSER = "CUser"
CFG_NODE_KEY_CPWD = "CPass"
CFG_NODE_KEY_CPRIV_PWD = "CPrivPass"
CFG_NODE_KEY_CAUTH = "CAuth"
CFG_NODE_KEY_CPRIV = "CPriv"
CFG_NODE_KEY_CCNMTY = "Ccommunity"
CFG_NODE_KEY_TSNMPVERSION = "TSnmp"
CFG_NODE_KEY_TUSER = "TUser"
CFG_NODE_KEY_TPWD = "TPass"
CFG_NODE_KEY_TPRIV_PWD = "TPrivPass"
CFG_NODE_KEY_TAUTH = "TAuth"
CFG_NODE_KEY_TPRIV = "TPriv"
CFG_NODE_KEY_TCNMTY = "Tcommunity"
CFG_NODE_KEY_IP = "IP"
OPTION_CMD_LIST = [CFG_NODE_KEY_IP, CFG_NODE_KEY_HOST_NAME,
                   CFG_NODE_KEY_DEVTYPE, CFG_NODE_KEY_PPORT,
                   CFG_NODE_KEY_CSNMPVERSION, CFG_NODE_KEY_CUSER,
                   CFG_NODE_KEY_CPWD, CFG_NODE_KEY_CAUTH, CFG_NODE_KEY_CPRIV,
                   CFG_NODE_KEY_CCNMTY, CFG_NODE_KEY_TSNMPVERSION,
                   CFG_NODE_KEY_TUSER, CFG_NODE_KEY_TPWD, CFG_NODE_KEY_TAUTH,
                   CFG_NODE_KEY_TPRIV, CFG_NODE_KEY_TCNMTY]
# --------------------ends cmd options ----------------------------------

# ------------------------- cmds -------------------------------------
NAME_FUNTION_ADD = "ADD"
NAME_FUNTION_BATCH = "BATCH"
NAME_FUNTION_DEL = "DEL"
NAME_FUNTION_INQUIRY = "INQUIRY"
NAME_FUNTION_VERSION = "VERSION"
NAME_FUNTION_RESETSERVER = "RESETSERVER"
NAME_FUNTION_UPDATE = "UPDATE"
CMD_LIST = [NAME_FUNTION_ADD, NAME_FUNTION_BATCH, NAME_FUNTION_DEL,
            NAME_FUNTION_INQUIRY, NAME_FUNTION_VERSION,
            NAME_FUNTION_RESETSERVER, NAME_FUNTION_UPDATE]
# -------------------------funtion cmd-------------------------------------
# +++++++++++++const for xml parse  ++++++++++++++++++++++++++++
HOST_CFG_KEY_DEVICETYPE = 'devicetype'
HOST_CFG_KEY_VENDORID = 'vendorid'
HOST_CFG_KEY_PORT = 'port'
HOST_CFG_KEY_HOST = 'host'
HOST_CFG_KEY_HOSTNAME = 'hostname'
HOST_CFG_KEY_COLLECT = 'collect'
HOST_CFG_KEY_ALARM = 'alarm'
HOST_CFG_KEY_DEVICE = 'device'
HOST_CFG_KEY_IP = 'ipaddress'
HOST_CFG_KEY_NAME = 'name'
HOST_CFG_KEY_USER = 'user'
HOST_CFG_KEY_PASS = 'pass'
HOST_CFG_KEY_PRIVPASS = 'privpass'
HOST_CFG_KEY_AUTHPROTOCOL = 'authprotocol'
HOST_CFG_KEY_PRIVPROTOCOL = 'privprotocol'
HOST_CFG_KEY_COMMUNITY = 'community'
HOST_CFG_KEY_SNMPVERSION = 'snmpversion'
HOST_CFG_KEY_TRAPSNMPVERSION = 'snmpversion'
HOST_CFG_KEY_TRAPCOMMUNITY = 'community'
HOST_CFG_KEY_TYPE = 'type'
# --------------------ends xml parse----------------------------------


# --------------------cfg for oid -------------------------
SERVER_TYPE_OID_KEY = 'server_type_oid'
SERVER_TRAP_SETTING_IP_BMC_KEY = 'server_trap_setting_ip_bmc'
SERVER_TRAP_SETTING_PORT_BMC_KEY = 'server_trap_setting_port_bmc'
SERVER_TRAP_SETTING_ENABLE_BMC_KEY = 'server_trap_setting_enable_bmc'
SERVER_TRAP_SETTING_USER_BMC_KEY = 'server_trap_setting_user_bmc'
SERVER_TRAP_SETTING_TRAPVERSION_BMC_KEY = 'server_trap_setting_trapversion_bmc'
SERVER_TRAP_SETTING_TRAPMODE_BMC_KEY = 'server_trap_setting_trapmode_bmc'
SERVER_TRAP_SETTING_COMMUNITY_BMC_KEY = 'server_trap_setting_trapcommunity_bmc'
SERVER_TRAP_SETTING_TRAPENABLE_BMC_KEY = 'server_trap_setting_trapenable_bmc'
SERVER_TRAP_SETTING_IP_SMM_KEY = 'server_trap_setting_ip_smm'
SERVER_TRAP_SETTING_PORT_SMM_KEY = 'server_trap_setting_port_smm'
SERVER_TRAP_SETTING_ENABLE_SMM_KEY = 'server_trap_setting_enable_smm'
SERVER_TRAP_SETTING_USER_SMM_KEY = "server_trap_setting_user_smm"
SERVER_TRAP_SETTING_VERSION_SMM_KEY = "server_trap_setting_version_smm"
SERVER_TRAP_SETTING_TRAPMODE_SMM_KEY = "server_trap_setting_format_smm"
SERVER_TRAP_SETTING_COMMUNITY_SMM_KEY = "server_trap_setting_community_smm"
SERVER_TRAP_SETTING_TRAP_BOB_ENABLE_BMC_KEY = 'server_trap_setting_trap_bob_enable_bmc'


# --------------------------end cfg for oid ------------------------

# --------------------------------const oid Key -----------

### -----------Exception define ----------------------------------
class pareExcept(Exception):
    pass


class IPExcept(Exception):
    pass


# ---------------------------------end


def main():
    MSG_USAGE = ''' add   %prog add -i IPADDRESS [] ..
                    batch %prog batch -i IPADDRESS [] ..
                    del  %prog del -i IPADDRESS [] ..
                    inquiry   %prog inquiry
                    version %prog version
                    update %prog update
                    resetserver %prog resetserver -i IPADDRESS [] ..                  
                '''
    optParser = OptionParser(MSG_USAGE)
    
    optParser.add_option("-i", "--ip", dest="ip",
                         help=" IP address " + "example:192.168.1.1, "
                                               "192.168.2.* ,192.168.1-10",
                         default=None
                         )
    
    optParser.add_option("-H", "--hostName", dest=CFG_NODE_KEY_HOST_NAME,
                         help="name of devices" + "default: hostname = ipaddr",
                         default=None
                         )
    optParser.add_option("-t", "--type", dest=CFG_NODE_KEY_DEVTYPE,
                         help="deviceType,suppport :Rack Blade HighDensity default: Rack",
                         default="Rack"
                         )
    optParser.add_option("-p", "--port", dest=CFG_NODE_KEY_PPORT,
                         help="snmp service Port" + "default: 161",
                         default="161"
                         )
    optParser.add_option("-v", "--CSnmp", dest=CFG_NODE_KEY_CSNMPVERSION,
                         help="SnmpVersion for collecting infomation celloct"
                              + "example: v1,v2,v3", default="v3"
                         )
    optParser.add_option("-u", "--CUser", dest=CFG_NODE_KEY_CUSER,
                         help="Snmp user  for collecting infomation celloct"
                              + "", default=None
                         )
    optParser.add_option("-a", "--CPass", dest=CFG_NODE_KEY_CPWD,
                         help="Snmp passwd for collecting infomation celloct "
                              + "", default=None
                         )
    optParser.add_option("-e", "--CPrivPass", dest=CFG_NODE_KEY_CPRIV_PWD,
                         help="Snmp privPasswd for collecting infomation celloct "
                              + "", default=None
                         )
    optParser.add_option("-x", "--CAuth", dest=CFG_NODE_KEY_CAUTH,
                         help="authprotocol of snmp to collect infomation; options:MD5|SHA"
                              + "", default="SHA"
                         )
    optParser.add_option("-d", "--CPriv", dest=CFG_NODE_KEY_CPRIV,
                         help="privprotocol of snmp to collect infomation ; options:AES|DES"
                              + "", default="AES"
                         )
    optParser.add_option("-c", "--Ccommunity", dest=CFG_NODE_KEY_CCNMTY,
                         help="community of snmp to collect infomation " + "",
                         default=None
                         )
    optParser.add_option("-V", "--TSnmp", dest=CFG_NODE_KEY_TSNMPVERSION,
                         help="SnmpVersion to get trap" + "example: v1,v2,v3",
                         default="v3"
                         )
    optParser.add_option("-U", "--TUser", dest=CFG_NODE_KEY_TUSER,
                         help="Snmp user  to get trap" + "", default=None
                         )
    optParser.add_option("-A", "--TPass", dest=CFG_NODE_KEY_TPWD,
                         help="  Snmp passwd to get trap " + "", default=None
                         )
    optParser.add_option("-E", "--TPrivPass", dest=CFG_NODE_KEY_TPRIV_PWD,
                         help="Snmp privPasswd to get trap " + "", default=None
                         )
    optParser.add_option("-X", "--TAuth", dest=CFG_NODE_KEY_TAUTH,
                         help="authprotocol of snmp to get trap ;options:MD5|SHA"
                              + "", default=None
                         )
    optParser.add_option("-D", "--TPriv", dest=CFG_NODE_KEY_TPRIV,
                         help="privprotocol of snmp to get trap ;options:AES|DES "
                              + "", default=None
                         )
    optParser.add_option("-C", "--Tcommunity", dest=CFG_NODE_KEY_TCNMTY,
                         help="community of snmp to get trap" + "",
                         default=None
                         )
    
    options, args = optParser.parse_args()
    
    if not len(args) == 1:
        optParser.print_help()
        return
    if args[0].upper() not in CMD_LIST:
        optParser.print_help()
        return
    if args[0].upper() in [NAME_FUNTION_ADD, NAME_FUNTION_BATCH]:
        if options.ip is None:
            print "IP mush be set "
            return
        if options.CUser is None and options.CSnmp.lower() == 'v3':
            print "when use SNMP v3 user mush be set "
            return
        if options.CPass is None and options.CSnmp.lower() == 'v3':
            print "when use SNMP v3 password mush be set "
            return
        if options.Ccommunity is None and options.CSnmp.lower() in ['v2',
                                                                    'v1']:
            print "when use SNMP v2 v1 community mush be set "
            return
        if options.CAuth is not None:
            if options.CAuth.upper() not in ["MD5", "SHA"]:
                print "please check -x"
                optParser.print_help()
                return
            else:
                options.CAuth = options.CAuth.upper()
        if options.CPriv is not None:
            if options.CPriv.upper() not in ["AES", "DES"]:
                print "please check -d"
                optParser.print_help()
                return
            else:
                options.CPriv = options.CPriv.upper()
        if options.TAuth is not None:
            if options.TAuth.upper() not in ["MD5", "SHA"]:
                print "please check -X"
                optParser.print_help()
                return
            else:
                options.TAuth = options.TAuth.upper()
        if options.TPriv is not None:
            if options.TPriv.upper() not in ["AES", "DES"]:
                print "please check -D"
                optParser.print_help()
                return
            else:
                options.TPriv = options.TPriv.upper()
        if options.CSnmp is not None:
            if options.CSnmp.lower() not in ["v1", "v2", "v3"]:
                print "please check -v "
                optParser.print_help()
                return
            else:
                options.CSnmp = options.CSnmp.lower()
        if options.TSnmp is not None:
            if options.TSnmp.lower() not in ["v1", "v2", "v3"]:
                print "please check -V"
                optParser.print_help()
                return
            else:
                options.TSnmp = options.TSnmp.lower()
        if options.type is not None:
            if options.type.upper() not in ["RACK", "BLADE", "HIGHDENSITY"]:
                print "please check -t,only suppport :Rack Blade HighDensity"
            else:
                if options.type.upper() == "RACK":
                    options.type = "Rack"
                if options.type.upper() == "BLADE":
                    options.type = "Blade"
                if options.type.upper() == "HIGHDENSITY":
                    options.type = "HighDensity"
                    # batch set hostName cant be set
        if options.hostName is not None and args[0].upper() == NAME_FUNTION_BATCH:
            print "Info: when batch  hostName would auto be set as ip address "
            options.hostName = None
    ConfigHandler(parseParm(options, args)).mainHandler()


def parseParm(options, args):
    _snmp_map_list = {CFG_NODE_KEY_TSNMPVERSION: CFG_NODE_KEY_CSNMPVERSION,
                      CFG_NODE_KEY_TUSER: CFG_NODE_KEY_CUSER,
                      CFG_NODE_KEY_TPWD: CFG_NODE_KEY_CPWD,
                      CFG_NODE_KEY_TAUTH: CFG_NODE_KEY_CAUTH,
                      CFG_NODE_KEY_TPRIV: CFG_NODE_KEY_CPRIV,
                      CFG_NODE_KEY_TCNMTY: CFG_NODE_KEY_CCNMTY,
                      CFG_NODE_KEY_CPRIV_PWD: CFG_NODE_KEY_CPWD,
                      CFG_NODE_KEY_TPRIV_PWD: CFG_NODE_KEY_TPWD}
    parm_list = {
        "fun": args[0],
        OPTION_CMD_LIST[0]: options.ip,
        OPTION_CMD_LIST[1]: options.hostName,
        OPTION_CMD_LIST[2]: options.type,
        OPTION_CMD_LIST[3]: options.port,
        OPTION_CMD_LIST[4]: options.CSnmp,
        OPTION_CMD_LIST[5]: options.CUser,
        OPTION_CMD_LIST[6]: options.CPass,
        CFG_NODE_KEY_CPRIV_PWD: options.CPrivPass,
        OPTION_CMD_LIST[7]: options.CAuth,
        OPTION_CMD_LIST[8]: options.CPriv,
        OPTION_CMD_LIST[9]: options.Ccommunity,
        OPTION_CMD_LIST[10]: options.TSnmp,
        OPTION_CMD_LIST[11]: options.TUser,
        OPTION_CMD_LIST[12]: options.TPass,
        CFG_NODE_KEY_TPRIV_PWD: options.TPrivPass,
        OPTION_CMD_LIST[13]: options.TAuth,
        OPTION_CMD_LIST[14]: options.TPriv,
        OPTION_CMD_LIST[15]: options.Tcommunity,
    }
    # if SNMP config for Trap is none then use the collect snmp config
    for _tmp_item in _snmp_map_list.keys():
        if parm_list[_tmp_item] is None:
            parm_list[_tmp_item] = parm_list[_snmp_map_list[_tmp_item]]
    
    return parm_list


class commonFun:
    @classmethod
    def matchSigleIp(cls, ipAddstr):
        matcher = re.match(
            "((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)",
            ipAddstr)
        if matcher is not None:
            if matcher.group(0) == ipAddstr:
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def matchBatchIP(cls, ipAddstr):
        ipList = []
        matcher = re.match(
            "(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?\.)("
            "2[0-4]\d|25[0-5]|[01]?\d\d?\.)\*", ipAddstr)
        if matcher is not None:
            ipStr = matcher.group(1) + matcher.group(2) + matcher.group(3)
            for i in range(255):
                ipList.append(ipStr + str(i))
            return True, ipList
        else:
            matcher = re.match(
                "(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|["
                "01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25["
                "0-5]|[01]?\d\d?)-(2[0-4]\d|25[0-5]|[01]?\d\d?)",
                ipAddstr)
            if matcher is not None:
                ipStr = matcher.group(1) + matcher.group(2) + matcher.group(3)
                startStr = matcher.group(4)
                endStr = matcher.group(5)
                if int(endStr) < int(startStr):
                    for i in range(255):
                        if i < int(endStr):
                            continue
                        if i > int(startStr):
                            continue
                        ipList.append(ipStr + str(i))
                else:
                    for i in range(255):
                        if i < int(startStr):
                            continue
                        if i > int(endStr):
                            continue
                        ipList.append(ipStr + str(i))
                return True, ipList
            else:
                return False, ipList


class ConfigHandler:
    def __init__(self, argv):
        self.__parm = argv
        self.__configDiclist = []
        self.__trapPort = ""
        self.__localip = ""
        self.CofnigServer = False
        self.__OidDic = {}
        self.__OidDicV5 = {}
        self.__chechmkVersion = self.__find_ckmkVersion()
        self._nagiosHomeDir = self.__find_nagiosdir()
        self.__pareHostFile()
        self.__PareInitFile()
        self.__ParePluginFile()
        self._cmkuser = "prod"
        self._cmkgroup = "prod"
        self._nagiosuser = 'nagios'
        self._nagiosgroup = 'nagios'
        if self.__chechmkVersion == '1_4' or self.__chechmkVersion == '1_5':
            self._cmkuser, self._cmkgroup = self.getUsrInfo()
        else:
            self._nagiosuser, self._nagiosgroup = self.getNagiosUserinfo()

    def getNagiosUserinfo(self):
        try:
            list = commands.getoutput("ls -l /usr/local/nagios ")
            infolist = list.split('\n')[1].split()
            usr = infolist[2]
            group = infolist[3]
            return usr, group
        except Exception, err:
            print "get getNagiosUserinfo error Exception: ", str(err)
            return "nagios", "nagios"

    def getUsrInfo(self):
        usrFile = self._nagiosHomeDir + os.path.sep + "etc/XFUSION_server/usrFile.cfg"
        strlist = []
        usr = 'prod'
        group = 'prod'
        file = None
        try:
            file = open(usrFile, "r+")
            strlist = file.readlines()
        except Exception, e:
            print 'error : open usrFile.cfg error :  ' + str(e)
        finally:
            if file is not None:
                file.close()
        if strlist == [] or strlist is None:
            return usr, group
        for eachline in strlist:
            if re.findall(r'.*usr.*=.*', eachline):
                usr = eachline.split('=')[1]
            if re.findall(r'.*group.*=.*', eachline):
                group = eachline.split('=')[1]
        return usr.strip(), group.strip()

    def __ParePluginFile(self):
        _etcPath = self.__getCfgPath()
        filePath = _etcPath + os.path.sep + "XFUSION_plugin.cfg"
        filePathV5 = _etcPath + os.path.sep + "XFUSION_plugin_v5.cfg"
        self.__DoParePluginFile(filePath, self.__OidDic)
        self.__DoParePluginFile(filePathV5, self.__OidDicV5)

    def __DoParePluginFile(self, filePath, dic):
        parser = ConfigParser.ConfigParser()
        file = None
        try:
            file = open(filePath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                if not section.upper() == "GENERIC":
                    continue
                for (key, value) in parser.items(section):
                    dic[key] = value
        except Exception, err:
            print "__DoParePluginFile err. file path: %s" % filePath, str(err)
        finally:
            if file is not None:
                file.close()

    def __PareInitFile(self):
        _etcPath = self.__getCfgPath()
        filePath = _etcPath + os.path.sep + "initial.cfg"
        parser = ConfigParser.ConfigParser()
        file = None
        try:
            file = open(filePath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    if key == "local_address":
                        self.__localip = value
                    elif key == "listen_port":
                        self.__trapPort = value
                    else:
                        continue
        except Exception, err:
            print "__PareInitFile err", str(err)
        finally:
            if file is not None:
                file.close()

    def __pareHostFile(self):
        _etcPath = self.__getCfgPath()
        filePath = _etcPath + os.path.sep + "XFUSION_hosts.xml"
        if not os.path.exists(filePath):
            print filePath + "not exist",
            return False
        file = open(filePath, 'r')
        doc = minidom.parseString(file.read())
        for hostnode in doc.documentElement.getElementsByTagName(
                HOST_CFG_KEY_HOST):
            try:
                parmDic = {}
                for node in hostnode.childNodes:
                    if node.nodeName == HOST_CFG_KEY_DEVICE:
                        parmDic[CFG_NODE_KEY_HOST_NAME] = \
                            str(node.getElementsByTagName(
                                HOST_CFG_KEY_HOSTNAME)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[HOST_CFG_KEY_IP] = \
                            str(node.getElementsByTagName(HOST_CFG_KEY_IP)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[CFG_NODE_KEY_DEVTYPE] = \
                            str(node.getElementsByTagName(
                                HOST_CFG_KEY_DEVICETYPE)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[CFG_NODE_KEY_VENDORID] = \
                            str(node.getElementsByTagName(
                                HOST_CFG_KEY_VENDORID)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[CFG_NODE_KEY_PPORT] = \
                            str(node.getElementsByTagName(HOST_CFG_KEY_PORT)[0]
                                .childNodes[0].nodeValue.strip())
                    elif node.nodeName == HOST_CFG_KEY_ALARM:
                        parmDic[CFG_NODE_KEY_TUSER] = \
                            str(node.getElementsByTagName(HOST_CFG_KEY_USER)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[CFG_NODE_KEY_TPWD] = \
                            self.dencrypt(str(
                                node.getElementsByTagName(HOST_CFG_KEY_PASS)[0]
                                    .childNodes[0].nodeValue.strip()))
                        parmDic[CFG_NODE_KEY_TPRIV_PWD] = \
                            self.dencrypt(str(
                                node.getElementsByTagName(HOST_CFG_KEY_PRIVPASS)[0]
                                    .childNodes[0].nodeValue.strip()))
                        parmDic[CFG_NODE_KEY_TSNMPVERSION] = \
                            str(node.getElementsByTagName(
                                HOST_CFG_KEY_TRAPSNMPVERSION)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[CFG_NODE_KEY_TCNMTY] = \
                            self.dencrypt(str(node.getElementsByTagName(
                                HOST_CFG_KEY_TRAPCOMMUNITY)[0]
                                              .childNodes[
                                                  0].nodeValue.strip()))
                        if node.getElementsByTagName(
                                HOST_CFG_KEY_AUTHPROTOCOL).length != 0:
                            parmDic[CFG_NODE_KEY_TAUTH] = \
                                str(node.getElementsByTagName(
                                    HOST_CFG_KEY_AUTHPROTOCOL)[0]
                                    .childNodes[0].nodeValue.strip())
                        else:
                            parmDic[CFG_NODE_KEY_TAUTH] = "SHA"
                        if node.getElementsByTagName(
                                HOST_CFG_KEY_PRIVPROTOCOL).length != 0:
                            parmDic[CFG_NODE_KEY_TPRIV] = \
                                str(node.getElementsByTagName(
                                    HOST_CFG_KEY_PRIVPROTOCOL)[0]
                                    .childNodes[0].nodeValue.strip())
                        else:
                            parmDic[CFG_NODE_KEY_TPRIV] = "AES"
                    elif node.nodeName == HOST_CFG_KEY_COLLECT:
                        parmDic[CFG_NODE_KEY_CUSER] = \
                            str(node.getElementsByTagName(HOST_CFG_KEY_USER)[0]
                                .childNodes[0].nodeValue.strip())
                        parmDic[CFG_NODE_KEY_CPWD] = \
                            self.dencrypt(str(
                                node.getElementsByTagName(HOST_CFG_KEY_PASS)[0]
                                    .childNodes[0].nodeValue.strip()))
                        parmDic[CFG_NODE_KEY_CPRIV_PWD] = \
                            self.dencrypt(str(
                                node.getElementsByTagName(HOST_CFG_KEY_PRIVPASS)[0]
                                    .childNodes[0].nodeValue.strip()))
                        parmDic[CFG_NODE_KEY_CSNMPVERSION] = \
                            str(node.getElementsByTagName(
                                HOST_CFG_KEY_TRAPSNMPVERSION)[0].childNodes[0]
                                .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_CCNMTY] = \
                            self.dencrypt(str(node.getElementsByTagName(
                                HOST_CFG_KEY_TRAPCOMMUNITY)[0]
                                              .childNodes[
                                                  0].nodeValue.strip()))
                        if node.getElementsByTagName(
                                HOST_CFG_KEY_AUTHPROTOCOL).length != 0:
                            parmDic[CFG_NODE_KEY_CAUTH] = \
                                str(node.getElementsByTagName(
                                    HOST_CFG_KEY_AUTHPROTOCOL)[0].childNodes[0]
                                    .nodeValue.strip())
                        else:
                            parmDic[CFG_NODE_KEY_CAUTH] = "SHA"
                        if node.getElementsByTagName(
                                HOST_CFG_KEY_PRIVPROTOCOL).length != 0:
                            parmDic[CFG_NODE_KEY_CPRIV] = \
                                str(node.getElementsByTagName(
                                    HOST_CFG_KEY_PRIVPROTOCOL)[0]
                                    .childNodes[0].nodeValue.strip())
                        else:
                            parmDic[CFG_NODE_KEY_CPRIV] = "AES"
                    else:
                        continue
                tmpDic = {}
                keyStr = None
                if HOST_CFG_KEY_IP in parmDic:
                    keyStr = parmDic.pop(HOST_CFG_KEY_IP)
                tmpDic.update(parmDic)
                tmphostDic = {}
                if keyStr is not None:
                    tmphostDic[keyStr] = tmpDic
                    self.__configDiclist.append(tmphostDic)
            except Exception, err:
                print "__pareHostFile except err : %s" % (str(err))
        if file is not None:
            file.close()
        return True

    def mainHandler(self):
        _funDis = {
            NAME_FUNTION_ADD: self.funAdd,
            NAME_FUNTION_BATCH: self.funBatch,
            NAME_FUNTION_DEL: self.funDel,
            NAME_FUNTION_INQUIRY: self.funInquiry,
            NAME_FUNTION_VERSION: self.funVersion,
            NAME_FUNTION_RESETSERVER: self.funReSetServer,
            NAME_FUNTION_UPDATE: self.funUpdate,
        }
        try:
            _funDis[self.__parm["fun"].upper()]()
            self.creatConfigfile()
            
            if self.CofnigServer is True:
                self.funSetServer()
            self.addPlugincfgInNagios()
            self.restartNagios()
        except IPExcept:
            print " please check IP "
        except Exception, err:
            print " mainHandler Exception  error info:", str(err)
            # update config

    def funUpdate(self):
        # need to creat config file againt ,
        # maybethe old file cant usr in new version 
        self.creatConfigfile()
        self.addPlugincfgInNagios()
        self.restartNagios()

    # set server ip ,port ,snmp config for trap        
    def funSetServer(self):
        global trapversion
        print "start set Server Trap config"
        ret = None
        iPlist = []
        for list in self.__configDiclist:
            try:
                for ipaddress, hostdic in list.items():
                    oidDic = self.__OidDic
                    if hostdic[CFG_NODE_KEY_VENDORID] == "1":
                        oidDic = self.__OidDicV5
                    if hostdic[CFG_NODE_KEY_CUSER] is None:
                        print " set server error ipaddress:%s has no snmpUser " % (
                            ipaddress)
                        return ret, iPlist
                    if hostdic[CFG_NODE_KEY_CPWD] is None:
                        print " set server error ipaddress:%s has no pwd " % (
                            ipaddress)
                        return ret, iPlist

                    if 'SHA'.find(
                            str(hostdic[CFG_NODE_KEY_CAUTH].upper())) != -1:
                        authProtocol = usmHMACSHAAuthProtocol
                    else:
                        authProtocol = usmHMACMD5AuthProtocol
                    if 'AES'.find(
                            str(hostdic[CFG_NODE_KEY_CPRIV].upper())) != -1:
                        privProtocol = usmAesCfb128Protocol
                    else:
                        privProtocol = usmDESPrivProtocol
                    useData = cmdgen.UsmUserData(hostdic[CFG_NODE_KEY_CUSER],
                                                 hostdic[CFG_NODE_KEY_CPWD],
                                                 hostdic[CFG_NODE_KEY_CPRIV_PWD],
                                                 authProtocol,
                                                 privProtocol)

                    # get server type
                    type = self._getServerType(ipaddress, useData, hostdic)
                    if type is None:
                        print "server:%s get server type error " % ipaddress
                        print "server:%s can not set trap config ,please set it yourself " % ipaddress
                        iPlist.append(ipaddress)
                        continue
                    print "--------------------------------------------------"
                    print "server:%s the last trap ip will be set " % ipaddress
                    print "server:%s trap mode will be set to eventcode mode " % ipaddress

                    if "E9000" in str(type) or "E6000" in str(type):
                        localaddresssetted = IpAddress(self.__localip)
                        portsetted = OctetString(self.__trapPort)
                        enableoid = Integer(1)
                        # eventCodeMode
                        trapmode = Integer(0)

                        if 'V3' == hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                            print "server:%s trap SNMP user will be set " % ipaddress
                            trapuser = OctetString(hostdic[CFG_NODE_KEY_CUSER])
                            trapversion = OctetString("v3")
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress,
                                                               hostdic[
                                                                   CFG_NODE_KEY_PPORT])),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_IP_SMM_KEY],
                                     localaddresssetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_PORT_SMM_KEY],
                                     portsetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_ENABLE_SMM_KEY],
                                     enableoid),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPMODE_SMM_KEY],
                                     trapmode),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_VERSION_SMM_KEY],
                                     trapversion))
                        else:
                            print "server:%s trap comunity will be set " % ipaddress
                            if 'V2' == hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion = OctetString("v2c")
                            
                            if 'V1' == hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion = OctetString("v1")
                            trapComunity = OctetString(
                                hostdic[CFG_NODE_KEY_TCNMTY])
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress,
                                                               hostdic[
                                                                   CFG_NODE_KEY_PPORT])),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_IP_SMM_KEY],
                                     localaddresssetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_PORT_SMM_KEY],
                                     portsetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_ENABLE_SMM_KEY],
                                     enableoid),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_VERSION_SMM_KEY],
                                     trapversion),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_COMMUNITY_SMM_KEY],
                                     trapComunity),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPMODE_SMM_KEY],
                                     trapmode))
                    else:
                        # ibmc
                        localaddresssetted = OctetString(self.__localip)
                        portsetted = Integer(self.__trapPort)
                        enableoid = Integer(2)
                        enableAll = Integer(2)
                        disableBob = Integer(1)
                        # eventCodeMode
                        trapmode = Integer(1)
                        if 'V3' == hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                            print "server:%s trap SNMP user will be set " % ipaddress
                            trapuser = OctetString(hostdic[CFG_NODE_KEY_CUSER])
                            trapversion = Integer(3)
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress,
                                                               hostdic[
                                                                   CFG_NODE_KEY_PPORT])),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_IP_BMC_KEY],
                                     localaddresssetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_PORT_BMC_KEY],
                                     portsetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_ENABLE_BMC_KEY],
                                     enableoid),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPMODE_BMC_KEY],
                                     trapmode),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPVERSION_BMC_KEY],
                                     trapversion),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_USER_BMC_KEY],
                                     trapuser),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPENABLE_BMC_KEY],
                                     enableAll),
                                    (oidDic[
                                        SERVER_TRAP_SETTING_TRAP_BOB_ENABLE_BMC_KEY],
                                     disableBob))
                        else:
                            print "server:%s trap comunity will be set " % ipaddress
                            if 'V2' == hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion = Integer(2)
                            if 'V1' == hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion = Integer(1)
                            trapComunity = OctetString(
                                hostdic[CFG_NODE_KEY_TCNMTY])
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress,
                                                               hostdic[
                                                                   CFG_NODE_KEY_PPORT])),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_IP_BMC_KEY],
                                     localaddresssetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_PORT_BMC_KEY],
                                     portsetted),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_ENABLE_BMC_KEY],
                                     enableoid),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPMODE_BMC_KEY],
                                     trapmode),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPVERSION_BMC_KEY],
                                     trapversion),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_COMMUNITY_BMC_KEY],
                                     trapComunity),
                                    (oidDic[
                                         SERVER_TRAP_SETTING_TRAPENABLE_BMC_KEY],
                                     enableAll),
                                    (oidDic[
                                        SERVER_TRAP_SETTING_TRAP_BOB_ENABLE_BMC_KEY],
                                     disableBob))
                            if errorIndication is None \
                                    and errorIndex == 6 \
                                    and errorStatus == 132:
                                print '==========================================================='
                                print 'set COMMUNITY fail please check your ' \
                                      'COMMUNITY  config serverIP:%s' % \
                                      ipaddress
                                print '==========================================================='
                                iPlist.append(ipaddress)
                                continue
                    if errorIndication is None \
                            and errorIndex == 0 \
                            and errorStatus == 0:
                        print ' setTrapSendAddress Done. %s' % ipaddress
                        print "--------------------------------------------------- "
                        continue
                    else:
                        print "set server trap  port and IP error msg:%s " \
                              "error index %s errorStatus %s ip %s" % \
                              (str(errorIndication), str(errorIndex),
                               str(errorStatus), ipaddress)
                        iPlist.append(ipaddress)
                        continue
            except Exception, err:
                print 'set trap config exception ;Exceptionstr:' + str(err)
        ret = len(iPlist)
        return ret, iPlist

    def funReSetServer(self):
        if 'SHA' in self.__parm[CFG_NODE_KEY_CAUTH].upper():
            authProtocol = usmHMACSHAAuthProtocol
        else:
            authProtocol = usmHMACMD5AuthProtocol
        if 'AES' in self.__parm[CFG_NODE_KEY_CPRIV].upper():
            privProtocol = usmAesCfb128Protocol
        else:
            privProtocol = usmDESPrivProtocol
        pwd = self.__parm[CFG_NODE_KEY_CPWD]
        if pwd is None:
            print "need snmp pwd"
            exit()
        if self.__parm[CFG_NODE_KEY_CUSER] is None:
            print "need snmp user"
            exit()
        useData = cmdgen.UsmUserData(self.__parm[CFG_NODE_KEY_CUSER],
                                     pwd,
                                     self.__parm[CFG_NODE_KEY_CPRIV_PWD],
                                     authProtocol,
                                     privProtocol)
        serverlist = []
        if commonFun.matchSigleIp(self.__parm[CFG_NODE_KEY_IP]):
            serverlist.append(self.__parm[CFG_NODE_KEY_IP])
        else:
            _ret, _iPstrlist = commonFun.matchBatchIP(
                self.__parm[CFG_NODE_KEY_IP])
            if _ret is not True:
                print "restet Server error ip is illegal ip:%s" % self.__parm[
                    CFG_NODE_KEY_IP]
                exit()
            serverlist = _iPstrlist
        for eachServer in serverlist:
            try:
                temDic = {}
                temDic.update(self.__parm)
                vendorId = self.__getVendorId(eachServer, temDic)
                temDic[CFG_NODE_KEY_VENDORID] = vendorId
                self._clearTrapIP(eachServer, useData, temDic)
            except Exception, err:
                print "reset server error: %s" % err
        exit()

    def _clearTrapIP(self, ipAddr, useData, hostDic):
        try:
            type = None
            type = self._getServerType(ipAddr, useData, hostDic)
            oidDic = self.__OidDic
            if hostDic[CFG_NODE_KEY_VENDORID] == "1":
                oidDic = self.__OidDicV5
            if type is None:
                print "get server type error ,ip:", ipAddr
            if "E9000" in str(type) or "E6000" in str(type):
                localaddresssetted = OctetString("")
                ipoid = oidDic[SERVER_TRAP_SETTING_IP_SMM_KEY]
            else:
                localaddresssetted = OctetString("")
                ipoid = oidDic[SERVER_TRAP_SETTING_IP_BMC_KEY]
            errorIndication, errorStatus, errorIndex, varBinds = \
                cmdgen.CommandGenerator().setCmd(
                    useData,
                    cmdgen.UdpTransportTarget((ipAddr, hostDic[CFG_NODE_KEY_PPORT])),
                    (ipoid, localaddresssetted))
            if errorIndication is None \
                    and errorIndex == 0 \
                    and errorStatus == 0:
                print ' clear TrapIP Done. , %s' % ipAddr
                return True
            else:
                return False
        except Exception, err:
            print "clear TrapIP Exception ,err: %s ServerIp:%s" % (err, ipAddr)
            return False

    def funAdd(self):
        print "addconfig start"
        if commonFun.matchSigleIp(self.__parm[CFG_NODE_KEY_IP]):
            # chang parm list to match type witch  saving in __configDiclist
            temKey = self.__parm.pop(CFG_NODE_KEY_IP)
            temDic = {}
            _tmpConfigDis = {}
            temDic.update(self.__parm)
            vendorId = self.__getVendorId(temKey, temDic)
            temDic[CFG_NODE_KEY_VENDORID] = vendorId
            _tmpConfigDis = {temKey: temDic}
            self._singleIPHandler(_tmpConfigDis)
            self.CofnigServer = True
        else:
            raise IPExcept

    def _singleIPHandler(self, cofnigDic):
        _cntConfig = len(self.__configDiclist)
        temKey = cofnigDic.keys()[0]
        indextoMo = None
        if _cntConfig >= 1:
            # ip in config file modify it
            for i in range(_cntConfig):
                if temKey in self.__configDiclist[i].keys():
                    self.__configDiclist[i][temKey] = cofnigDic[temKey]
                    indextoMo = i
            # has not ip in configfile just add it
            if indextoMo is None:
                self.__configDiclist.append(cofnigDic)
                # has no items configfils  just add it
        else:
            self.__configDiclist.append(cofnigDic)

    def funBatch(self):
        print "batch config start"
        _ret, _iPstrlist = commonFun.matchBatchIP(self.__parm[CFG_NODE_KEY_IP])
        self.__parm.pop(CFG_NODE_KEY_IP)

        if _ret:
            for eachitem in _iPstrlist:
                temDic = {}
                temDic.update(self.__parm)
                vendorId = self.__getVendorId(eachitem, temDic)
                temDic[CFG_NODE_KEY_VENDORID] = vendorId
                if self._CheckServiceIsok(eachitem, temDic):
                    _tmpConfigDis = {}
                    _tmpConfigDis = {eachitem: temDic}
                    self._singleIPHandler(_tmpConfigDis)
                    self.CofnigServer = True
                else:
                    print "server ip %s can not connect please check " % eachitem
        else:
            raise IPExcept
            # check service is network and snmp is OK

    def __getVendorId(self, ip, dic):
        host = Host()
        host.setIpAddress(ip)
        host.setPort(dic[CFG_NODE_KEY_PPORT])
        host.setUserName(dic[CFG_NODE_KEY_CUSER])
        host.setPassword(dic[CFG_NODE_KEY_CPWD])
        host.setPrivPassword(dic[CFG_NODE_KEY_CPRIV_PWD])
        host.setAuthProtocol(dic[CFG_NODE_KEY_CAUTH])
        host.setEncryptionProtocol(dic[CFG_NODE_KEY_CPRIV])
        host.setCollectVersion(dic[CFG_NODE_KEY_CSNMPVERSION])
        host.setCollectCommunity(dic[CFG_NODE_KEY_CCNMTY])
        try:
            channel = Channel(host)
            oid = "1.3.6.1.2.1.1.2.0"
            result = channel.getCmd(oid)
            if result.getCode() != NAGIOS_ERROR_SUCCESS:
                raise Exception("get vendor id fail. ")
            vendorIdStr = result.getData()[oid]
            vendorId = None
            if vendorIdStr.find(".58132.") != -1:
                vendorId = "2"
            elif vendorIdStr.find(".2011.") != -1:
                vendorId = "1"
            else:
                raise Exception("vendor id is not supported. ")
            return vendorId
        except Exception, err:
            raise err

    def _getServerType(self, IpStr, usedata, hostDic):
        oidDic = self.__OidDic
        if hostDic[CFG_NODE_KEY_VENDORID] == "1":
            oidDic = self.__OidDicV5
        type = None
        try:
            for serverTypeoid in oidDic[SERVER_TYPE_OID_KEY].split(","):
                errorIndication, errorStatus, errorIndex, varBinds = \
                    cmdgen.CommandGenerator().getCmd(usedata,
                                                     cmdgen.UdpTransportTarget(
                                                         (IpStr, hostDic[CFG_NODE_KEY_PPORT]),
                                                         timeout=2, retries=2),
                                                     serverTypeoid)

                if errorIndication is None and errorIndex == 0 and errorStatus == 0:
                    if str(varBinds[0][1]) == "":
                        continue
                    type = varBinds[0][1]
                    break
        except Exception, err:
            print "get server type Exception errif:", err
        finally:
            return type

    def _CheckServiceIsok(self, IpStr, dic):
        if 'SHA' in self.__parm[CFG_NODE_KEY_CAUTH].upper():
            authProtocol = usmHMACSHAAuthProtocol
        else:
            authProtocol = usmHMACMD5AuthProtocol
        if 'AES' in self.__parm[CFG_NODE_KEY_CPRIV].upper():
            privProtocol = usmAesCfb128Protocol
        else:
            privProtocol = usmDESPrivProtocol
        pwd = self.__parm[CFG_NODE_KEY_CPWD]
        community = self.__parm[CFG_NODE_KEY_CCNMTY]
        if self.__parm[CFG_NODE_KEY_CSNMPVERSION].upper() == "V3":
            userDate = cmdgen.UsmUserData(self.__parm[CFG_NODE_KEY_CUSER],
                                          pwd,
                                          self.__parm[CFG_NODE_KEY_CPRIV_PWD],
                                          authProtocol,
                                          privProtocol)
        else:
            userDate = cmdgen.CommunityData(community)
        type = self._getServerType(IpStr, userDate, dic)
        if type is None:
            return False
        return True

    def funDel(self):
        print "del config start"
        try:
            _cntConfig = len(self.__configDiclist)
            # iplist witch should be del
            ipdellist = []
            # del sigle IP
            if commonFun.matchSigleIp(self.__parm[CFG_NODE_KEY_IP]):
                # chang parm list to match type witch  saving in __configDiclist
                temKey = self.__parm[CFG_NODE_KEY_IP]
                indextoDel = None
                if _cntConfig >= 1:
                    # find ip if in config file,if yes save it and its config in ipdellist
                    for i in range(_cntConfig):
                        if temKey in self.__configDiclist[i].keys():
                            ipdellist.append(self.__configDiclist[i])
                self._ClearTrapIpBylist(ipdellist)
                self._delIPfromConfig(ipdellist)
                return
                # del batch ip
            _ret, _iPstrlist = commonFun.matchBatchIP(
                self.__parm[CFG_NODE_KEY_IP])
            if _ret is True:
                for ip in _iPstrlist:
                    if _cntConfig >= 1:
                        # find ip if in config file,if yes save it and its config in ipdellist
                        for i in range(_cntConfig):
                            if ip in self.__configDiclist[i].keys():
                                ipdellist.append(self.__configDiclist[i])
                self._ClearTrapIpBylist(ipdellist)
                self._delIPfromConfig(ipdellist)
                return
        except Exception, err:
            print "funDel Exception Errstr:" + str(err)
            # ip is illegal raise  IPExcept
        raise IPExcept

    def _ClearTrapIpBylist(self, configList):
        try:
            for eachconfig in configList:
                ipAddr = eachconfig.keys()[0]
                confdic = eachconfig.values()[0]
                if 'SHA'.find(str(confdic[CFG_NODE_KEY_CAUTH].upper())) != -1:
                    authProtocol = usmHMACSHAAuthProtocol
                else:
                    authProtocol = usmHMACMD5AuthProtocol
                if 'AES'.find(str(confdic[CFG_NODE_KEY_CPRIV].upper())) != -1:
                    privProtocol = usmAesCfb128Protocol
                else:
                    privProtocol = usmDESPrivProtocol
                useData = cmdgen.UsmUserData(confdic[CFG_NODE_KEY_CUSER],
                                             confdic[CFG_NODE_KEY_CPWD],
                                             confdic[CFG_NODE_KEY_CPRIV_PWD],
                                             authProtocol,
                                             privProtocol)
                ret = self._clearTrapIP(ipAddr, useData, confdic)
                if ret is False:
                    print "clear server Trap IP fail ,please clear it " \
                          "yourself  server IP :%s " % ipAddr
        except Exception, err:
            print "_ClearTrapIBylist Exception Errstr:" + str(err)
    
    def _delIPfromConfig(self, configList):
        for ipconfig in configList:
            try:
                ipaddr = ipconfig.keys()[0]
                _cntConfig = len(self.__configDiclist)
                if _cntConfig < 1:
                    return
                for i in range(_cntConfig):
                    if ipaddr in self.__configDiclist[i].keys():
                        del self.__configDiclist[i]
                        break
            except Exception, err:
                print "_delIPfromConfig Exception Errstr:" + str(err)

    def funVersion(self):
        print VERSTION_STR
        exit(0)
    
    def funInquiry(self):
        print "==============iplist in configfile ===================="
        for eachitem in self.__configDiclist:
            for eachkey in eachitem:
                print eachkey
        exit(0)
        # creat all config file

    def creatConfigfile(self):
        print "start CreatConfigfile "
        self.__creatServerCfg()
        self.__creathostxml()
        # 生成XFUSION_server.cfg 文件

    def __gethostservicescontent(self, devicetype, hostname, hostalias,
                                 ipaddress):
        _etcPath = self.__getCfgPath()
        # create a blade tmp file for services configuration for current host
        if devicetype == 'Blade':
            commands.getoutput("cat " + _etcPath + os.path.sep +
                               "Blade.cfg > /tmp/XFUSIONtmp.cfg")
        # create a rack or HD tmp file for services configuration for current host
        if devicetype != 'Blade' and devicetype != '':
            commands.getoutput("cat " + _etcPath + os.path.sep +
                               "HDorRack.cfg > /tmp/XFUSIONtmp.cfg")
        # update hostname in tmp file
        if hostname:
            commands.getoutput(
                "sed -i 's/hostname/" + hostname + "/g' /tmp/XFUSIONtmp.cfg")
        # update hostalias in tmp file
        if hostalias:
            commands.getoutput(
                "sed -i 's/hostalias/" + hostalias + "/g' /tmp/XFUSIONtmp.cfg")
        # update ipaddress in tmp file
        if ipaddress:
            commands.getoutput(
                "sed -i 's/ipaddress/" + ipaddress + "/g' /tmp/XFUSIONtmp.cfg")
        # get tmp file content about services for host
        output = commands.getoutput("cat /tmp/XFUSIONtmp.cfg")
        commands.getoutput("rm -rf /tmp/XFUSIONtmp.cfg")
        return output

    def __getObjContent(self, ipaddress, hostdic, objName):
        _etcPath = self.__getCfgPath()
        if not hostdic[CFG_NODE_KEY_HOST_NAME] is None:
            hostname = hostdic[CFG_NODE_KEY_HOST_NAME]
        else:
            hostname = ipaddress

        cmdName = objName + "_" + hostname + "_cmd"
        if hostdic[CFG_NODE_KEY_CSNMPVERSION].upper() == 'V3':
            cmdLind = "python $USER5$/XFUSION_server/%s -H %s -v 3 -u %s -a " \
                      "%s -A %s -x %s -X %s -c %s -T %s -p %s -o %s $" % (
                          "getInfoWithEncrypt.py", ipaddress,
                          hostdic[CFG_NODE_KEY_CUSER],
                          hostdic[CFG_NODE_KEY_CAUTH],
                          self.encrypt(hostdic[CFG_NODE_KEY_CPWD]),
                          hostdic[CFG_NODE_KEY_CPRIV],
                          self.encrypt(hostdic[CFG_NODE_KEY_CPRIV_PWD]),
                          objName, hostdic[CFG_NODE_KEY_DEVTYPE],
                          hostdic[CFG_NODE_KEY_PPORT],
                          hostdic[CFG_NODE_KEY_VENDORID])
        else:
            if hostdic[CFG_NODE_KEY_CSNMPVERSION].upper() == 'V2':
                versionStr = '2c'
            else:
                versionStr = '1'
            cmdLind = "python $USER5$/XFUSION_server/%s -H %s -v %s -C %s -c " \
                      "%s -T %s -p %s -o %s $" % (
                          "getInfoWithEncrypt.py", ipaddress, versionStr,
                          self.encrypt(hostdic[CFG_NODE_KEY_CCNMTY]), objName,
                          hostdic[CFG_NODE_KEY_DEVTYPE],
                          hostdic[CFG_NODE_KEY_PPORT],
                          hostdic[CFG_NODE_KEY_VENDORID])
        
        commands.getoutput(
            "cat " + _etcPath + os.path.sep + "objModle.cfg > "
                                              "/tmp/XFUSIONtmp.cfg")
        if hostname:
            commands.getoutput(
                "sed -i 's/hostname/" + hostname + "/g' /tmp/XFUSIONtmp.cfg")
        if cmdName:
            commands.getoutput(
                "sed -i 's/commandName/" + cmdName + "/g' /tmp/XFUSIONtmp.cfg")
        if objName:
            commands.getoutput(
                "sed -i 's/serveiceName/" + objName + "/g' /tmp/XFUSIONtmp.cfg")
        # blade collect info use passive module
        if objName.lower() != 'raid':
            commands.getoutput(
                "sed -i 's/active_enable/0" + "/g' /tmp/XFUSIONtmp.cfg")
            commands.getoutput(
                "sed -i 's/passive_eanble/1" + "/g' /tmp/XFUSIONtmp.cfg")
        else:
            commands.getoutput(
                "sed -i 's/active_enable/1" + "/g' /tmp/XFUSIONtmp.cfg")
            commands.getoutput(
                "sed -i 's/passive_eanble/0" + "/g' /tmp/XFUSIONtmp.cfg")
        comstr = '''
        define command{
        command_name                %s
        command_line                %s
        }
        ''' % (cmdName, cmdLind)
        output = commands.getoutput("cat /tmp/XFUSIONtmp.cfg")
        output += comstr
        commands.getoutput("rm -rf /tmp/XFUSIONtmp.cfg")
        return output

    def __getlistenercontent(self, hostname):
        _etcPath = self.__getCfgPath()

        # create a listener tmp file for nagios plugin listener
        # configuration for local host
        commands.getoutput(
            "cat " + _etcPath + os.path.sep + "listener.cfg > /tmp/listenertmp.cfg")
        # update hostname in tmp file
        commands.getoutput(
            "sed -i 's/localhost/" + hostname + "/g' /tmp/listenertmp.cfg")
        # get content of listener configuration
        output = commands.getoutput("cat /tmp/listenertmp.cfg")
        commands.getoutput("rm -rf /tmp/listenertmp.cfg")
        return output

    def __creatServerCfg(self):
        _etcPath = self.__getCfgPath()
        commands.getoutput(
            "rm -rf " + _etcPath + os.path.sep + "XFUSION_server.cfg")
        servicefile = None
        servicefile = open(_etcPath + os.path.sep + "XFUSION_server.cfg", 'w')
        for hostdic in self.__configDiclist:
            for hostIpAddress in hostdic.keys():
                _hostParmdic = hostdic[hostIpAddress]
                if _hostParmdic[CFG_NODE_KEY_HOST_NAME] is None:
                    _hostName = hostIpAddress
                else:
                    _hostName = _hostParmdic[CFG_NODE_KEY_HOST_NAME]
                hostalias = _hostName
                if _hostParmdic[CFG_NODE_KEY_DEVTYPE] == 'Rack':
                    hostalias = 'RackDetailsStatus@' + _hostName
                elif _hostParmdic[CFG_NODE_KEY_DEVTYPE] == 'HighDensity':
                    hostalias = 'HighDensityDetailsStatus@' + _hostName
                elif _hostParmdic[CFG_NODE_KEY_DEVTYPE] == 'Blade':
                    hostalias = 'BladeDetailsStatus@' + _hostName
                cfgContent = self.__gethostservicescontent(
                    _hostParmdic[CFG_NODE_KEY_DEVTYPE],
                    _hostName, hostalias, hostIpAddress)
                
                if _hostParmdic[CFG_NODE_KEY_DEVTYPE].lower() == "blade":
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "system")
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "power")
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "fan")
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "shelf")
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "smm")
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "switch")
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "blade")
                else:
                    cfgContent += self.__getObjContent(hostIpAddress,
                                                       _hostParmdic, "raid")
                servicefile.writelines(cfgContent)

        servicefile.writelines(self.__getlistenercontent("127.0.0.1"))
        servicefile.close()
        if '1_4' in self.__chechmkVersion or '1_5' in self.__chechmkVersion:
            commands.getoutput(
                "sudo chown %s:%s " % (self._cmkuser, self._cmkgroup)
                + _etcPath + os.path.sep + "XFUSION_server.cfg")
        else:
            commands.getoutput(
                "sudo chown %s:%s " % (self._nagiosuser, self._nagiosgroup)
                + _etcPath + os.path.sep + "XFUSION_server.cfg")
        print "creatServerCfg ok"

    def __getCfgPath(self):
        _etcPath = self._nagiosHomeDir + os.path.sep + "etc" + os.path.sep + "XFUSION_server"
        return _etcPath

    def __find_nagiosdir(self):
        # return nagios directory
        cmd = "source /etc/profile;echo $NAGIOSHOME"
        procs = commands.getoutput(cmd)
        return procs

    def __find_ckmkVersion(self):
        # return nagios directory
        cmd = "source /etc/profile;echo $NAGIOS_CHECKMK_VERSION"
        procs = commands.getoutput(cmd)
        return procs

    def __getNagiosPath(self):
        return self._nagiosHomeDir

    # creat XFUSION_hosts.xml:
    def __creathostxml(self):
        _etcPath = self.__getCfgPath()
        commands.getoutput(
            "rm -rf " + _etcPath + os.path.sep + "XFUSION_hosts.xml")
        _hostfilePath = _etcPath + os.path.sep + "XFUSION_hosts.xml"
        try:
            impl = minidom.getDOMImplementation()
            dom = impl.createDocument(None, 'hosts', None)
            for hostdic in self.__configDiclist:
                for hostIpAddress in hostdic.keys():
                    _hostParmdic = hostdic[hostIpAddress]
                    root = dom.documentElement
                    xhost = dom.createElement('host')
                    root.appendChild(xhost)
                    xdevice = dom.createElement('device')
                    xhost.appendChild(xdevice)
                    xhostname = dom.createElement('hostname')
                    # if hostName =None , hostName = Ip addr
                    if _hostParmdic[CFG_NODE_KEY_HOST_NAME] == "None":
                        xhostnamet = dom.createTextNode(None)
                    else:
                        xhostnamet = dom.createTextNode(hostIpAddress)
                    xhostname.appendChild(xhostnamet)
                    xdevice.appendChild(xhostname)
                    xipaddress = dom.createElement('ipaddress')
                    xipaddresst = dom.createTextNode(hostIpAddress)
                    xipaddress.appendChild(xipaddresst)
                    xdevice.appendChild(xipaddress)
                    xdevicetype = dom.createElement('devicetype')
                    xdevicetypet = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_DEVTYPE])
                    xdevicetype.appendChild(xdevicetypet)
                    xdevice.appendChild(xdevicetype)
                    xvendorid = dom.createElement('vendorid')
                    xvendoridt = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_VENDORID])
                    xvendorid.appendChild(xvendoridt)
                    xdevice.appendChild(xvendorid)
                    xport = dom.createElement('port')
                    xportt = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_PPORT])
                    xport.appendChild(xportt)
                    xdevice.appendChild(xport)
                    # collect info: collectuser/password/authprotocol/privprotocol
                    xcollect = dom.createElement('collect')
                    xhost.appendChild(xcollect)
                    xsnmpversion = dom.createElement('snmpversion')
                    xsnmpversiont = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_CSNMPVERSION])
                    xsnmpversion.appendChild(xsnmpversiont)
                    xcollect.appendChild(xsnmpversion)
                    xuser = dom.createElement('user')
                    xusert = dom.createTextNode(
                        str(_hostParmdic[CFG_NODE_KEY_CUSER]))
                    xuser.appendChild(xusert)
                    xcollect.appendChild(xuser)
                    xpass = dom.createElement('pass')
                    xpasst = dom.createTextNode(
                        self.encrypt(str(_hostParmdic[CFG_NODE_KEY_CPWD])))
                    xpass.appendChild(xpasst)
                    xcollect.appendChild(xpass)
                    xprivpass = dom.createElement('privpass')
                    xprivpasst = dom.createTextNode(
                        self.encrypt(str(_hostParmdic[CFG_NODE_KEY_CPRIV_PWD])))
                    xprivpass.appendChild(xprivpasst)
                    xcollect.appendChild(xprivpass)
                    xauthprotocol = dom.createElement('authprotocol')
                    xauthprotocolt = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_CAUTH])
                    xauthprotocol.appendChild(xauthprotocolt)
                    xcollect.appendChild(xauthprotocol)
                    xprivprotocol = dom.createElement('privprotocol')
                    xprivprotocolt = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_CPRIV])
                    xprivprotocol.appendChild(xprivprotocolt)
                    xcollect.appendChild(xprivprotocol)
                    xcommunity = dom.createElement('community')
                    xcommunityt = dom.createTextNode(
                        self.encrypt(str(_hostParmdic[CFG_NODE_KEY_CCNMTY])))
                    xcommunity.appendChild(xcommunityt)
                    xcollect.appendChild(xcommunity)
                    # alarm info: trapuser/trapwd/trapauthprotocol/trapprivprotocol
                    xalarm = dom.createElement('alarm')
                    xhost.appendChild(xalarm)
                    xtrapsnmpversion = dom.createElement('snmpversion')
                    xtrapsnmpversiont = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_TSNMPVERSION])
                    xtrapsnmpversion.appendChild(xtrapsnmpversiont)
                    xalarm.appendChild(xtrapsnmpversion)
                    xtrapuser = dom.createElement('user')
                    xtrapusert = dom.createTextNode(
                        str(_hostParmdic[CFG_NODE_KEY_TUSER]))
                    xtrapuser.appendChild(xtrapusert)
                    xalarm.appendChild(xtrapuser)
                    xtrappass = dom.createElement('pass')
                    xtrappasst = dom.createTextNode(
                        self.encrypt(str(_hostParmdic[CFG_NODE_KEY_TPWD])))
                    xtrappass.appendChild(xtrappasst)
                    xalarm.appendChild(xtrappass)
                    xtrapprivpass = dom.createElement('privpass')
                    xtrapprivpasst = dom.createTextNode(
                        self.encrypt(str(_hostParmdic[CFG_NODE_KEY_TPRIV_PWD])))
                    xtrapprivpass.appendChild(xtrapprivpasst)
                    xalarm.appendChild(xtrapprivpass)
                    xtrapauthprotocol = dom.createElement('authprotocol')
                    xtrapauthprotocolt = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_TAUTH])
                    xtrapauthprotocol.appendChild(xtrapauthprotocolt)
                    xalarm.appendChild(xtrapauthprotocol)
                    xtrapprivprotocol = dom.createElement('privprotocol')
                    xtrapprivprotocolt = dom.createTextNode(
                        _hostParmdic[CFG_NODE_KEY_TPRIV])
                    xtrapprivprotocol.appendChild(xtrapprivprotocolt)
                    xalarm.appendChild(xtrapprivprotocol)
                    xtrapcommunity = dom.createElement('community')
                    xtrapcommunityt = dom.createTextNode(
                        self.encrypt(str(_hostParmdic[CFG_NODE_KEY_TCNMTY])))
                    xtrapcommunity.appendChild(xtrapcommunityt)
                    xalarm.appendChild(xtrapcommunity)
        except Exception, e:
            print "parm not right : %s" % e
            sys.exit(1)

        xmlfile = open(_hostfilePath, 'w')
        dom.writexml(xmlfile, addindent='    ', newl='\n', encoding='UTF-8')
        xmlfile.close()
        if '1_4' in self.__chechmkVersion or '1_5' in self.__chechmkVersion:
            commands.getoutput(
                "sudo chown %s:%s " % (self._cmkuser, self._cmkgroup) +
                _etcPath + os.path.sep + "XFUSION_hosts.xml")
        else:
            commands.getoutput(
                "sudo chown %s:%s " % (self._nagiosuser, self._nagiosgroup)
                + _etcPath + os.path.sep + "XFUSION_hosts.xml")
        print "creathostxml ok"

        # deccode an encrypt funs  -------------

    def dencrypt(self, pkey):
        return genKey.dencryptKey(pkey, self.getrootkey())

    def getrootkey(self):
        rootkey = genKey.dencryptKey(genKey.readKey(), genKey.genRootKeyStr())
        return rootkey

    def encrypt(self, pkey):
        encryptpwd = genKey.encryptKey(pkey, self.getrootkey())
        return encryptpwd
        # end deccode an encrypt funs  -------------

    def EditSourceFile(self):
        global file
        nagioshome = self.__getNagiosPath()
        if '1_4' in self.__chechmkVersion or '1_5' in self.__chechmkVersion:
            SourceFile = "/omd/sites/%s/etc/nagios/resource.cfg" % (
                self._cmkuser)

        else:
            SourceFile = nagioshome + os.path.sep + "etc" + os.path.sep + "resource.cfg"
        SourcInfo = "$USER5$=%s/libexec\n" % nagioshome
        try:
            file = open(SourceFile, "r+")
            strlist = file.readlines()
            if SourcInfo in strlist:
                return
            file.writelines(SourcInfo)
        except Exception, err:
            print "EditSourceFile exception info :" + str(err)
        finally:
            if file is not None:
                file.close()

    def addPlugincfgInNagios(self):
        nagioshome = self.__getNagiosPath()
        self.EditSourceFile()

        if '1_4' in self.__chechmkVersion or '1_5' in self.__chechmkVersion:
            NagioscfgFilePath = "/omd/sites/%s/etc/nagios/nagios.cfg" % (
                self._cmkuser)
            strforconfig = "precached_object_file=%s" % nagioshome + os.path.sep \
                           + "etc" + os.path.sep + "XFUSION_server" + os.path.sep + "XFUSION_server.cfg\n"
        else:
            NagioscfgFilePath = nagioshome + os.path.sep + "etc" + os.path.sep + "nagios.cfg"
            strforconfig = "cfg_file=%s" % nagioshome + os.path.sep + "etc" \
                           + os.path.sep + "XFUSION_server" + os.path.sep + "XFUSION_server.cfg\n"
        file = None
        try:
            file = open(NagioscfgFilePath, "r+")
            strlist = file.readlines()
            # had configed so exit
            if strforconfig in strlist:
                return
                # cofnig nagios.cfg
            file.writelines(strforconfig)
        except Exception, err:
            print "addPlugincfgInNagios exception info :" + str(err)
        finally:
            if file is not None:
                file.close()

    def restartNagios(self):
        print "start kill trapd.py "
        if '1_4' in self.__chechmkVersion or '1_5' in self.__chechmkVersion:
            ret = os.system("omd stop")
        else:
            ret = os.system("service nagios stop")
        if not ret == 0:
            print "stop Nagios fail "
        time.sleep(1)
        trapdpid = commands.getoutput(
            "ps -efww | grep trapd.py | grep -v grep | awk '{print $2}'")
        os.system("kill -9  %s" % trapdpid)
        time.sleep(2)
        try:
            if '1_4' in self.__chechmkVersion or '1_5' in self.__chechmkVersion:
                ret = os.system("omd restart")
            else:
                ret = os.system("service nagios restart")
            if not ret == 0:
                print "start Nagios fail "
                print "please restart nagios service youself "
        except Exception, err:
            print "start Nagios exception errif : %s" % str(err)
            print "please restart nagios service yourself "
        print "start Nagios servic done"


if __name__ == '__main__':
    main()
