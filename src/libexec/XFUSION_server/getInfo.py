#!/usr/bin/python
from optparse import OptionParser
import os
import re
import subprocess

# ----------status----------------------------------------
STATUS_UNKNOWN = 3
STATUS_CRITICAL = 2
STATUS_WARNING = 1
STATUS_OK = 0
MSG_HEASTATUS = ["OK", "WARNING", "CRITICAL", "UNKNOWN"]

# --------------OID---------------------------------------
OID_LIST_SYSTEM = [{"status": "on", "method": "get",
                    "oid": "1.3.6.1.4.1.58132.2.235.1.1.1.1.0",
                    "replace": "1:0,2:1,3:1,4:2"},
                   {"status": "off", "method": "bulk", "name": "alarmstatus",
                    "oid": "1.3.6.1.4.1.58132.2.235.1.1.1.50.1.4",
                    "replace": "1:0,2:1,3:1,4:2"},
                   {"status": "off", "method": "bulk",
                    "name": "alarmsdecription",
                    "oid": "1.3.6.1.4.1.58132.2.235.1.1.1.50.1.5"},
                   {"status": "off", "method": "get", "name": "deviceName",
                    "oid": "1.3.6.1.4.1.58132.2.235.1.1.1.6.0"},
                   {"status": "off", "method": "get", "name": "deviceSerialNo",
                    "oid": "1.3.6.1.4.1.58132.2.235.1.1.1.7.0"},
                   {"status": "off", "method": "get",
                    "name": "systemPowerState",
                    "oid": "1.3.6.1.4.1.58132.2.235.1.1.1.12.0", "replace":
                        "1:gracefulPowerOff,2:powerOn,3:coldReset,4:gracefulReboot,5:forciblyPowerOff"}]
OID_LIST_CPU = [{"status": "on", "method": "get",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.15.1.0",
                 "replace": "1:0,2:1,3:1,4:2,5:3,6:3"},
                {"status": "off", "method": "bulk", "name": "presence",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.15.50.1.6",
                 "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"},
                {"status": "off", "method": "bulk", "name": "devicename",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.15.50.1.10"},
                {"status": "off", "method": "bulk", "name": "state",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.15.50.1.6",
                 "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"}]
OID_LIST_FAN = [{"status": "on", "method": "get",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.8.3.0",
                 "replace": "1:0,2:1,3:1,4:2,5:3,6:3"},
                {"status": "off", "method": "bulk", "name": "presence",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.8.50.1.3",
                 "replace": "1:absence,2:presence,3:unknown"},
                {"status": "off", "method": "bulk", "name": "devicename",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.8.50.1.7"},
                {"status": "off", "method": "bulk", "name": "state",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.8.50.1.4",
                 "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"}]
OID_LIST_POWER = [{"status": "on", "method": "get",
                   "oid": "1.3.6.1.4.1.58132.2.235.1.1.6.1.0",
                   "replace": "1:0,2:1,3:1,4:2,5:3,6:3"},
                  {"status": "off", "method": "bulk", "name": "presence",
                   "oid": "1.3.6.1.4.1.58132.2.235.1.1.6.50.1.9",
                   "replace": "1:absence,2:presence,3:unknown"},
                  {"status": "off", "method": "bulk", "name": "devicename",
                   "oid": "1.3.6.1.4.1.58132.2.235.1.1.6.50.1.13"},
                  {"status": "off", "method": "bulk", "name": "state",
                   "oid": "1.3.6.1.4.1.58132.2.235.1.1.6.50.1.7",
                   "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"}]
OID_LIST_DISK = [{"status": "on", "method": "get",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.18.1.0",
                  "replace": "1:0,2:1,3:1,4:2,5:3,6:3"},
                 {"status": "off", "method": "bulk", "name": "presence",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.18.50.1.2",
                  "replace": "1:absence,2:presence,3:unknown"},
                 {"status": "off", "method": "bulk", "name": "devicename",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.18.50.1.6"},
                 {"status": "off", "method": "bulk", "name": "state",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.18.50.1.3",
                  "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"}]
OID_LIST_MEN = [{"status": "on", "method": "get",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.16.1.0",
                 "replace": "1:0,2:1,3:1,4:2,5:3,6:3"},
                {"status": "off", "method": "bulk", "name": "presence",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.16.50.1.6",
                 "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"},
                {"status": "off", "method": "bulk", "name": "devicename",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.16.50.1.10"},
                {"status": "off", "method": "bulk", "name": "state",
                 "oid": "1.3.6.1.4.1.58132.2.235.1.1.16.50.1.6",
                 "replace": "1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"}]
OID_LIST_RAID = [{"status": "on", "method": "bulk",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.36.50.1.7"},
                 {"status": "off", "method": "bulk", "name": "present",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.36.50.1.16"},
                 {"status": "off", "method": "bulk", "name": "state",
                  "oid": "1.3.6.1.4.1.58132.2.235.1.1.36.50.1.18"},
                 ]

OID_DIC = {"power": OID_LIST_POWER,
           "cpu": OID_LIST_CPU,
           "memory": OID_LIST_MEN,
           "fan": OID_LIST_FAN,
           "hardDisk": OID_LIST_DISK,
           "system": OID_LIST_SYSTEM}


def commandParse():
    parser = OptionParser()
    parser.add_option("-c", "--component", dest="component",
                      help="component for check  as (power,cpu,memory,fan,system,hardDisk)",
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
                      help="SNMP security level (only with SNMP v3) ("
                           "noAuthNoPriv|authNoPriv|authPriv)",
                      default="authPriv")
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="Timeout in seconds for SNMP", default="3")
    parser.add_option("-r", "--retry", dest="retry",
                      help="retry for  SNMP", default="2")
    (opts, args) = parser.parse_args()
    compenlist = ["power", "cpu", "memory", "fan", "system", "hardDisk",
                  "raid"]

    if opts.host is None:
        print "please input Hostname or IP "
        exit(STATUS_UNKNOWN)
    if opts.version == '3' and opts.user is None:
        print "please input SNMP username  "
        exit(STATUS_UNKNOWN)
    if opts.ppwd is None:
        opts.ppwd = opts.apwd
    if opts.component not in compenlist:
        print "-c only support as : power,cpu,memory,fan,system,hardDisk,raid"
        exit(STATUS_UNKNOWN)
    return opts


class InfoHandler:
    def __init__(self, parmlist):
        self._Parm = parmlist

    def getRaidStatus(self):
        _status = STATUS_UNKNOWN
        _info = ''
        _ret = "1"
        _output = ""
        _ret, _output = self.snmpWalk(OID_LIST_RAID[0]["oid"])
        _tempListStatus = []
        if _ret == "0":
            tmplist = _output.split("\n")
            for itemTmp in tmplist:
                matcher = re.match(".*=.*:(.*)", itemTmp)
                if matcher is None:
                    _tempListStatus.append(STATUS_UNKNOWN)
                    continue
                if matcher.group(1).strip() == "65535":
                    _tempListStatus.append(STATUS_UNKNOWN)
                elif matcher.group(1).strip() == "0":
                    _tempListStatus.append(STATUS_OK)
                else:
                    _tempListStatus.append(STATUS_WARNING)
        _tempListBBUpresent = []
        _tempListBBUstatus = []
        _ret, _output = self.snmpWalk(OID_LIST_RAID[1]["oid"])

        if _ret == "0":
            tmplist = _output.split("\n")
            for itemTmp in tmplist:
                matcher = re.match(".*=.*:(.*)", itemTmp)
                if matcher is not None:
                    _tempListBBUpresent.append(matcher.group(1).strip())
        _ret, _output = self.snmpWalk(OID_LIST_RAID[2]["oid"])

        if _ret == "0":
            tmplist = _output.split("\n")
            for itemTmp in tmplist:
                matcher = re.match(".*=.*:(.*)", itemTmp)
                if matcher is None:
                    continue
                if matcher.group(1).strip() == '0':
                    _tempListBBUstatus.append(STATUS_OK)
                else:
                    _tempListBBUstatus.append(STATUS_WARNING)
        if not _tempListStatus:
            _info = "can not  get Raid status ,network error or has no Raid "
            return _status, _info

        if STATUS_WARNING in _tempListStatus:
            _status = STATUS_WARNING
        elif STATUS_OK in _tempListStatus:
            _status = STATUS_OK
        else:
            _status = STATUS_UNKNOWN
        if _tempListBBUpresent == [] or _tempListBBUstatus == []:
            _info = "can not get BBU status ,network error or has no Raid "
            return _status, _info
        else:
            for i in range(len(_tempListBBUpresent)):
                # prensented BBU  should display healthstate
                if _tempListBBUpresent[i] == '2':
                    _info += 'BBU' + str(i) + ' status:' \
                             + MSG_HEASTATUS[_tempListBBUstatus[i]] + "; "
        return _status, _info

    def getStatu(self):
        _status = STATUS_UNKNOWN
        _infoStr = ''
        if self._Parm.component.lower() == "raid":
            _status, _infoStr = self.getRaidStatus()
        else:
            if self._Parm.component is not None:
                _status = self.getStatuOid(self._Parm.component)
                _infoStr = self.getMessageOid(self._Parm.component)
            else:
                print "error getStatuOid input None "
        print "%s HealthStatus: %s " % (str(self._Parm.component), MSG_HEASTATUS[_status])
        print "=============================== info ============================="
        print _infoStr

        return _status

    def snmpGet(self, oid):
        if self._Parm.vendorid == "1":
            oid = oid.replace(".58132.", ".2011.")
        if self._Parm.version == '3':
            _comStr = "snmpget -u %s -t %s -r %s -v %s -l %s -a %s -A %s -x " \
                      "%s -X %s %s:%s %s" \
                      % (self._Parm.user, self._Parm.timeout, self._Parm.retry,
                         self._Parm.version, self._Parm.seclevel,
                         self._Parm.aprotocol, self._Parm.apwd,
                         self._Parm.pprotocol, self._Parm.ppwd,
                         self._Parm.host, self._Parm.port, oid)
        else:
            _comStr = "snmpget -t %s -r %s -v %s -c %s  %s:%s %s" \
                      % (self._Parm.timeout, self._Parm.retry,
                         self._Parm.version, self._Parm.community,
                         self._Parm.host, self._Parm.port, oid)
        
        ret, output = self.runCommand(_comStr)
        return ret, output

    def snmpWalk(self, oid):
        if self._Parm.vendorid == "1":
            oid = oid.replace(".58132.", ".2011.")
        _ret = "1"
        _output = ""
        if self._Parm.version == '3':
            _comStr = "snmpwalk -u %s -t %s -r %s -v %s -l %s -a %s -A %s " \
                      "-x %s -X %s %s:%s %s" \
                      % (self._Parm.user, self._Parm.timeout, self._Parm.retry,
                         self._Parm.version, self._Parm.seclevel,
                         self._Parm.aprotocol, self._Parm.apwd,
                         self._Parm.pprotocol, self._Parm.ppwd,
                         self._Parm.host, self._Parm.port, oid)
        else:
            _comStr = "snmpwalk -t %s -r %s -v %s -c %s  %s:%s %s" \
                      % (self._Parm.timeout, self._Parm.retry,
                         self._Parm.version, self._Parm.community,
                         self._Parm.host, self._Parm.port, oid)

        _ret, _output = self.runCommand(_comStr)
        return _ret, _output

    def _repalce(self, strSrc, repleaseStr):
        _ret = STATUS_UNKNOWN
        strlist = repleaseStr.strip().split(",")
        for strRe in strlist:
            if strSrc == strRe.split(":")[0]:
                _ret = strRe.split(":")[1]
        return _ret

    def getStatuOid(self, component):
        _statu = STATUS_UNKNOWN
        _ret = "1"
        _output = ""
        oidlist = OID_DIC[component]
        for oidDis in oidlist:
            if oidDis["status"] != "on" or \
                    oidDis["method"] != "get":
                continue
            _ret, _ouput = self.snmpGet(oidDis["oid"])
            if _ret != "0":
                print "snmpget  end with error "
                continue
            if "replace" in oidDis.keys():
                matcher = re.match(".*=.*:(.*)", _ouput)
                if matcher is not None:
                    _tmpStatu = matcher.group(1).strip()
                    _statu = int(self._repalce(_tmpStatu, oidDis["replace"]))
        return _statu

    def getMessageOid(self, component):
        _infoStr = ""
        _ret = "1"
        _output = ""
        oidlist = OID_DIC[component]
        presentStatuList = []
        nameList = []
        StatusList = []
        AlarmStatus = []
        AlarmDecrition = []
        for oidDis in oidlist:
            if oidDis["status"] != "off":
                continue

            if oidDis["method"] == "get":
                _ret, _ouput = self.snmpGet(oidDis["oid"])
                if _ret != "0":
                    print "snmpget  end with error "
                    continue
                matcher = re.match(".*=.*:(.*)", _ouput)
                if matcher is None:
                    continue
                if "replace" in oidDis.keys():
                    _infoStr = _infoStr + oidDis["name"] \
                               + self._repalce(matcher.group(1).strip(),
                                               oidDis["replace"])
                else:
                    _infoStr = _infoStr + oidDis["name"] + " " \
                               + matcher.group(1) + " "

            elif oidDis["method"] == "bulk":
                _ret, _ouput = self.snmpWalk(oidDis["oid"])
                if _ret != "0":
                    print "snmpwalk end with error ", oidDis["name"]
                    continue
                tmpList = _ouput.split("\n")

                if oidDis["name"] == "presence":
                    for itemTmp in tmpList:
                        matcher = re.match(".*=.*:(.*)", itemTmp)
                        if matcher is not None:
                            presentStatuList.append(
                                self._repalce(matcher.group(1).strip(),
                                              oidDis["replace"]))
                elif oidDis["name"] == "devicename":
                    for itemTmp in tmpList:
                        matcher = re.match(".*=.*:(.*)", itemTmp)
                        if matcher is not None:
                            nameList.append(matcher.group(1).strip())
                elif oidDis["name"] == "state":
                    for itemTmp in tmpList:
                        matcher = re.match(".*=.*:(.*)", itemTmp)
                        if matcher is not None:
                            StatusList.append(
                                self._repalce(matcher.group(1).strip(),
                                              oidDis["replace"]))
                elif oidDis["name"] == "alarmstatus":
                    for itemTmp in tmpList:
                        matcher = re.match(".*=.*:(.*)", itemTmp)
                        if matcher is not None:
                            AlarmStatus.append(
                                self._repalce(matcher.group(1).strip(),
                                              oidDis["replace"]))
                elif oidDis["name"] == "alarmsdecription":
                    for itemTmp in tmpList:
                        matcher = re.match(".*=.*:.*\"(.*)\"", itemTmp)
                        if matcher is not None:
                            AlarmDecrition.append(matcher.group(1))
                else:
                    print "oidDis[ name], config error :", oidDis["name"]

            else:
                print "oidDis[ method] config error :", oidDis["method"]
        _alldevice = len(presentStatuList)
        if _alldevice >= 1:
            presentCnt = 0
            for i in range(_alldevice):
                if not "absence" == presentStatuList[i]:
                    presentCnt = presentCnt + 1
                    _infoStr = _infoStr + str(presentCnt) + ":" + nameList[
                        presentCnt - 1] + " " + "status: " + StatusList[i] + "\n"
            presentMsg = " presentStatus:" + str(presentCnt) + "/" + \
                         str(_alldevice) + "\n"
            _infoStr = presentMsg + _infoStr
        _allAlarm = len(AlarmStatus)
        if _allAlarm >= 1:
            _infoStr = _infoStr + \
                       "\n \n============== alarms =================\n"
            cnt = 0
            for i in range(_allAlarm):
                cnt = cnt + 1
                _infoStr = _infoStr + str(cnt) + "," + AlarmDecrition[
                    i] + "status:" + MSG_HEASTATUS[int(AlarmStatus[i])] + "\n"
        return _infoStr

    def runCommand(self, command):
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, )
        stdout, stderr = proc.communicate('through stdin to stdout')
        if not proc.returncode == 0:
            print "Error %s: %s\n " % (proc.returncode, stderr.strip())
            if proc.returncode == 127:  # File not found, lets print path
                path = os.getenv("PATH")
                print "cmdout:", stdout
                print "Check if your path is correct %s" % path

        return str(proc.returncode), stdout


if __name__ == '__main__':
    try:
        commandDic = commandParse()
        infoHandler = InfoHandler(commandDic)
        state = infoHandler.getStatu()
        exit(state)
    except Exception, e:
        print "Unhandled exception while running script: %s" % e
        exit(STATUS_UNKNOWN)
