# encoding:utf-8

import os

from processservice import ProcessService
from parsehostxml import ParseHostXml
from parsedevicexml import ParseDeviceXml

from base.logger import Logger
from base.channel import Channel
from util.common import Common
from model.device import Device
from model.result import CollectResult, ComponentResult
from constant import constant


class DeviceModelExcept(Exception):
    """
    " 获取设备型号失败异常
    " handle: 处理获取设备型号异常信息类,
    """
    pass


class DeviceConfigExcept(Exception):
    """
    " 获取设备配置文件失败异常
    " handle: 处理获取设备配置文件异常信息类,
    """
    pass


class CommonConfigPathExcept(Exception):
    """
    " 获取配置文件失败异常
    " handle: 处理获取配置文件异常信息类,
    """
    pass


class CollectService:
    _logger = Logger.getInstance()
    _configs = []

    def __init__(self, mode, data):
        self._mode = mode
        self._targetPath = Common.getBinPath() + os.path.sep + "result"
        self._hostPath = Common.getHostConfigPath()
        if constant.COLLECT_MODE_CMD_TOTAL == mode and constant.NUMBER_TWO == len(
                data):
            self._targetPath = data[1]
        elif constant.COLLECT_MODE_CMD_FILE == mode and constant.NUMBER_ONE == len(
                data):
            self._hostPath = data[0] if data[0][len(data[0]) - 1:] != os.path.sep else data[0][0:len(data[0]) - 1]
        elif constant.COLLECT_MODE_CMD_FILE == mode and constant.NUMBER_THREE == len(
                data):
            self._hostPath = data[0]
            self._targetPath = data[2] if data[2][len(data[2]) - 1:] != os.path.sep else data[2][0:len(data[2]) - 1]

        if not ParseDeviceXml.parseDeviceXml(Common.getDeviceConfigPath(),
                                             self._configs):
            self._logger.error("service : parse device xml file failed")

    @staticmethod
    def getCommonConfigPath(config):
        for file in config.getFile():
            if "common" == file.getType():
                return Common.getDeviceModelPath() + os.path.sep + file.getName()
        raise CommonConfigPathExcept

    # 获取host设备的型号
    @staticmethod
    def getDeiveModel(channel, oid):
        result = channel.getCmd(oid)
        if result.getCode() != constant.NAGIOS_ERROR_SUCCESS:
            raise DeviceModelExcept
        return result.getData()[oid]

    @staticmethod
    def getConfigPath(config, deviceModel):
        for file in config.getFile():
            if deviceModel == file.getType() or deviceModel in file.getReplace():
                return Common.getDeviceModelPath() + os.path.sep + file.getName()
        return CollectService.getCommonConfigPath(config)

    def start(self):
        hosts = []
        if not ParseHostXml.parseHostXml(self._hostPath, hosts):
            self._logger.error("service : parse host xml file failed.")
            return -1

        for host in hosts:
            channel = Channel(host)
            collectResult = CollectResult()
            collectResult.setHostName(host.getHostName())
            collectResult.setIpAddress(host.getIpAddress())
            deviceInfo = Device()
            errCode = self.__getDeviceInfo(channel, host, deviceInfo)
            if errCode != constant.NAGIOS_ERROR_SUCCESS:
                self._logger.error("service : get device info failed. host name:%s" % host.getHostName())
                if self._mode == constant.COLLECT_MODE_CMD_PLUGIN:
                    service_map = {service: errCode for service in host.getCollectBasic()}
                else:
                    service_map = {service: errCode for service in host.getCollectExtension()}
                collectResult.setService(service_map)
            
            else:
                collectResult.setService(
                    self.collect(channel, host, deviceInfo))
            ProcessService.start(self._mode, self._targetPath, collectResult)
        return 0

    def collect(self, channel, host, deviceInfo):
        if self._mode == constant.COLLECT_MODE_CMD_PLUGIN:
            collectComponents = host.getCollectBasic()
        else:
            collectComponents = host.getCollectExtension()

        serviceResult = {}
        for collectComponent in collectComponents:
            if collectComponent not in deviceInfo.getComponents():
                self._logger.error("service: collect device info failed. "
                                   "device config not has %s component in %s host."
                                   % (collectComponent, host.getHostName()))
                serviceResult[collectComponent] = \
                    constant.NAGIOS_ERROR_DEVICE_CONFIG_NOTINCLUDE

            else:
                componentResults = []
                for deviceComponent in deviceInfo.getComponents()[collectComponent]:
                    componentResult = ComponentResult()
                    componentResult.setComponent(deviceComponent)
                    componentResult.setResult(
                        self.__collectNode(channel, deviceComponent))
                    componentResults.append(componentResult)
                
                serviceResult[collectComponent] = componentResults

        return serviceResult

    # 采集node节点中的OID信息
    def __collectNode(self, channel, deviceComponent):
        
        nodeOids = [deviceNode.getOid() for deviceNode in deviceComponent.getNode()]

        if "get" == deviceComponent.getMethod():
            return channel.getCmd(*tuple(nodeOids))
        elif "bulk" == deviceComponent.getMethod():
            return channel.bulkCmd(0, 1, *tuple(nodeOids))
        else:
            self._logger.error("service: collect device info failed， the %s "
                               "method of request is invalid."
                               % (deviceComponent.getMethod()))
            return constant.ChannelResult(constant.NAIGOS_ERROR_INVALID_METHOD)

    # 获取host设备采集信息
    def __getDeviceInfo(self, channel, host, device):
        try:
            config = self.__getDeviceConfig(host)
            deviceModel = CollectService.getDeiveModel(channel, config.getOid())
            deviceConfigPath = CollectService.getConfigPath(config, deviceModel)
            errCode = ParseDeviceXml.parseDeviceConfig(self._mode, deviceConfigPath, device)
            if errCode != constant.NAGIOS_ERROR_SUCCESS:
                self._logger.error("service: parse device config failed. "
                                   "host name:%s, device model:%s."
                                   % (host.getHostName(), deviceModel))
                return errCode
            return constant.NAGIOS_ERROR_SUCCESS
        except DeviceConfigExcept:
            self._logger.error(
                "service: get device config failed. device type:%s." % (
                    host.getDeviceType()))
            return constant.NAGIOS_ERROR_DEVICE_XML_INVALID
        except DeviceModelExcept:
            self._logger.error("service: get device model failed. "
                               "host name:%s, device type oid:%s."
                               % (host.getHostName(), config.getOid()))
            return constant.NAGIOS_ERROR_DEVICE_XML_INVALID
        except CommonConfigPathExcept:
            self._logger.error("service: parse device config failed. "
                               "host name:%s, device model:%s."
                               % (host.getHostName(), deviceModel))
            return constant.NAGIOS_ERROR_DEVICE_CONFIG_NOTEXIST

    # 获取host设备的型号OID
    def __getDeviceConfig(self, host):
        for config in self._configs:
            if host.getDeviceType() == config.getDeviceType() \
                    and host.getVendorId() == config.getVendorId():
                return config
        raise DeviceConfigExcept
