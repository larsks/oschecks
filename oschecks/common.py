from __future__ import print_function

import cliff.command
import logging
import time

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


class CheckCommand (cliff.command.Command):
    def format_result(self, retcode, msg):
        label = {
            RET_OKAY: 'OKAY',
            RET_WARN: 'WARNING',
            RET_CRIT: 'CRITICAL',
        }.get(retcode, 'UNKNOWN')

        print('{}: {}'.format(label, msg))
        return retcode

    def run(self, parsed_args):
        try:
            exitcode, msg = self.take_action(parsed_args)
            return self.format_result(exitcode, msg)
        except Exitcode as exc:
            return self.format_result(exc.exitcode, str(exc))


class LimitCommand (CheckCommand):
    def get_parser(self, prog_name):
        p = super(LimitCommand, self).get_parser(prog_name)
        g = p.add_argument_group('Limit Options')
        g.add_argument('--limit', '-l', type=int, default=1)

        return p


class TimeoutCommand (CheckCommand):
    def get_parser(self, prog_name):
        p = super(TimeoutCommand, self).get_parser(prog_name)
        g = p.add_argument_group('Timeout Options')

        g.add_argument('--warning', '-w', dest='timeout_warning',
                       type=int, default=5)
        g.add_argument('--critical', '-c', dest='timeout_critical',
                       type=int, default=10)

        return p

    def run(self, parsed_args):
        try:
            exitcode, msg, t = self.take_action(parsed_args)
        except Exitcode as exc:
            return self.format_result(exc.exitcode, str(exc))

        if t is None:
            return self.format_result(exitcode, msg)

        msg = '{} ({:0.4f} seconds)'.format(msg, t.interval)

        if exitcode != RET_OKAY:
            return self.format_result(exitcode, msg)

        if (parsed_args.timeout_critical and
                t.interval >= parsed_args.timeout_critical):
            return self.format_result(RET_CRIT, msg)
        elif (parsed_args.timeout_warning and
                t.interval >= parsed_args.timeout_warning):
            return self.format_result(RET_WARN, msg)
        else:
            return self.format_result(RET_OKAY, msg)


class TimeoutError(Exception):
    pass


class Timer(object):

    log = logging.getLogger(__name__)

    def __init__(self, timeout=None):
        self.interval = 0
        self.timeout = timeout

    def __enter__(self):
        self.time_start = time.time()
        return self

    def __exit__(self, *args):
        self.time_end = time.time()
        self.interval = self.time_end - self.time_start

    def tick(self):
        if self.timeout:
            time_now = time.time()
            delta = time_now - self.time_start
            if delta > self.timeout:
                raise TimeoutError(delta)
