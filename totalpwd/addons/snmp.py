#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    SNMP 扫描器
"""

from pysnmp.hlapi import *
from ..scanner import Scanner
from ..settings import opts


class SNMPScanner(Scanner):
    """
        SNMP 扫描器
    """

    def __init__(self, pwd, target, username, password):
        super(SNMPScanner, self).__init__(pwd, target, username, password)
        self.port = self.port or 161

    def _check(self):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.password),
            UdpTransportTarget((str(self.host), self.port)),
            ContextData(),
            ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        evidence = ""
        if errorIndication:
            self.logger.debug(errorIndication)
        elif errorStatus:
            self.logger.debug(
                "%s at %s"
                % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                )
            )
        else:
            for varBind in varBinds:
                evidence += " = ".join([x.prettyPrint() for x in varBind])

        return evidence


def mkscanner(pwd, target, username, password):
    return SNMPScanner(pwd, target, username, password)
