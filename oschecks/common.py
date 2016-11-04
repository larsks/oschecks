from __future__ import print_function

import cliff.command
import logging
import time

from oschecks.exitcodes import (  # NOQA
    Exitcode, ExitCritical, ExitWarning, ExitOkay,
    RET_OKAY, RET_WARN, RET_CRIT
)


class CheckCommand (cliff.command.Command):

    def __init__(self, *args, **kwargs):
        super(CheckCommand, self).__init__(*args, **kwargs)

        self.log = logging.getLogger(
            '{0.__class__.__module__}.{0.__class__.__name__}'.format(self))

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

        # If we have no interval information, just exit normally.
        if t is None:
            return self.format_result(exitcode, msg)

        msg = '{} ({:0.4f} seconds)'.format(msg, t.interval)

        # If there was a problem, don't override the status
        # based on the timeouts.
        if exitcode != RET_OKAY:
            return self.format_result(exitcode, msg)

        # Modify the return status based on how long
        # the operation took to complete.
        if (parsed_args.timeout_critical and
                t.interval >= parsed_args.timeout_critical):
            return self.format_result(RET_CRIT, msg)
        elif (parsed_args.timeout_warning and
                t.interval >= parsed_args.timeout_warning):
            return self.format_result(RET_WARN, msg)
        else:
            return self.format_result(RET_OKAY, msg)


class TimeoutError(Exception):
    '''Raised by a Timer object if it ticks past a configued timeout.'''
    pass


class Timer(object):
    '''A context manager for measuring the duration of an operation.  Use
    it like this:

        with Timer() as t:
          ...do something...

        print ('The operation took {:02f} seconds.'.format(t.interval))

    If you provide a timeout value and periodically call the `tick` method,
    a Timer object will raise a TimeoutError exception when the timeout
    is exceeded.'''

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
