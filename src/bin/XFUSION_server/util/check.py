# encoding:utf-8

import os
import sys

from base.logger import Logger
from constant.constant import NUMBER_ZERO, NUMBER_ONE, NUMBER_TWO, NUMBER_THREE

sys.path.append("..")


# 参数校验类
class Check:
    _logger = Logger.getInstance()

    @classmethod
    def checkPluginModeParam(cls, params):
        if NUMBER_ZERO == len(params):
            return True
        return False

    @classmethod
    def checkTotalModeParam(cls, params):
        if NUMBER_ZERO == len(params):
            return True
        if NUMBER_ONE == len(params) or NUMBER_TWO == len(params):
            if '-r' == params[0]:
                return cls.checkTargetParam(params[1:])
            else:
                cls._logger.error(
                    "check target param: param is not '-r'. ")
                return False
        cls._logger.error(
            "main error: param length is incorrect. ")
        return False

    @classmethod
    def checkFileModeParam(cls, params):
        if NUMBER_ZERO == len(params):
            cls._logger.error(
                "check file mode: necessary parameters are missing, param=-f. ")
            return False
        if os.path.isfile(params[0]) and \
                os.path.splitext(params[0])[1] == ".xml":
            if NUMBER_ONE == len(params):
                return True
            if NUMBER_TWO == len(params) or NUMBER_THREE == len(params):
                if '-r' == params[1]:
                    return cls.checkTargetParam(params[2:])
                else:
                    cls._logger.error(
                         "check target param: param is not '-r'. ")
                    return False
            cls._logger.error(
                "main error: param length is incorrect. ")
            return False
        else:
            cls._logger.error(
                "check file mode: param is invalid, param=-f. ")
            return False

    # 结果文件存放参数校验
    @classmethod
    def checkTargetParam(cls, params):
        if NUMBER_ONE == len(params):
            if not os.path.isdir(params[0]):
                cls._logger.error(
                    "check target param: the target path is invalid, param=-r. ")
                return False
            else:
                return True
        if NUMBER_ZERO == len(params):
            cls._logger.error(
                "check target param: the necessary parameter is missing, param=-r. ")
            return False
        return True
