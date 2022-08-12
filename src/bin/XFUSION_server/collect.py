# encoding:utf-8

import os
import sys
from threading import Timer

from base.logger import Logger
from config import VERSTION_STR
from constant.constant import COLLECT_MODE_CMD_PLUGIN, \
    COLLECT_MODE_CMD_TOTAL, COLLECT_MODE_CMD_FILE
from model.plugin import LoggerConfig
from service.collectservice import CollectService
from util.check import Check
from util.common import Common


def loggerConfig(node, loggerData):
    elements = Common.getChild(node)
    if elements is None:
        return False
    for element in elements:
        if "param" != element.tag:
            return False
        if "level" == element.attrib.get("name"):
            loggerData.setLoggerLevel(element.text)
        elif "size" == element.attrib.get("name"):
            loggerData.setLoggerSize(element.text)
        elif "index" == element.attrib.get("name"):
            loggerData.setLoggerIndex(element.text)

    loggerData.setLoggerPath(Common.getExePath() + os.path.sep + "log")

    return True


def pluginConfig(loggerData):
    if not os.path.exists(Common.getPluginConfigPath()):
        return False

    root = Common.getRoot(Common.getPluginConfigPath())
    if root is None:
        return False

    for node in Common.getChild(root):
        if "config" != node.tag:
            return False

        if "log" == node.attrib.get('name'):
            loggerConfig(node, loggerData)

    return True


def initPlugin():
    # parse plugin config
    loggerData = LoggerConfig()
    if not pluginConfig(loggerData):
        return False

    Logger.getInstance().init(loggerData)
    return True


def main(argv=None):
    if not initPlugin():
        return -1
    Logger.getInstance().error('========= %s =======' % VERSTION_STR)
    if len(argv) < 2:
        Logger.getInstance().error(
            "main error: param length should not be zero.")
        return -1

    try:
        if "-p" == argv[1]:
            if not Check.checkPluginModeParam(argv[2:]):
                Logger.getInstance().error(
                    "main error: param is invalid, param=%s." % sys.argv[1:])
                return -1

            service = CollectService(COLLECT_MODE_CMD_PLUGIN, None)

        elif "-a" == argv[1]:
            if not Check.checkTotalModeParam(argv[2:]):
                Logger.getInstance().error(
                    "main error: param is invalid, param=%s." % sys.argv[1])
                return -1

            service = CollectService(COLLECT_MODE_CMD_TOTAL, argv[2:])

        elif "-f" == argv[1]:
            if not Check.checkFileModeParam(argv[2:]):
                Logger.getInstance().error(
                    "main error: param is invalid, param=%s." % sys.argv[1])
                return -1

            service = CollectService(COLLECT_MODE_CMD_FILE, argv[2:])
        else:
            Logger.getInstance().error(
                "main error: option param is invalid optoion : [%s]" % (
                    argv[1]))
            return -1

        return service.start()

    except Exception as e:
        Logger.getInstance().exception(
            "main exception: collect device info exception: [%s]" % e)
        return -1


if __name__ == "__main__":

    time_int_eval = 300
    while True:
        t = Timer(time_int_eval, sys.exit(main(sys.argv)))
        t.start()
        time.sleep(300)
