from __future__ import absolute_import

RET_OKAY = 0
RET_WARN = 1
RET_CRIT = 2
RET_WTF = 3


class Exitcode(Exception):
    exitcode = RET_WTF


class ExitCritical(Exitcode):
    exitcode = RET_CRIT


class ExitWarning(Exitcode):
    exitcode = RET_WARN


class ExitOkay(Exitcode):
    exitcode = RET_OKAY
