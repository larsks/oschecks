import sys
import click
import time

RET_OKAY = 0
RET_WARN = 1
RET_CRIT = 2
RET_WTF = 3

common_options = [
    click.option('--warning', '-w', 'timeout_warning',
                 type=int, default=5,
                 help='Warning timeout for API calls'),
    click.option('--critical', '-c', 'timeout_critical',
                 type=int, default=10,
                 help='Critical timeout for API calls'),
    click.option('--limit', '-l', type=int, default=1,
                 help='Maximum number of objects to list')
]


def apply_common_options(func):
    for opt in common_options:
        func = opt(func)

    return func


class Timer(object):
    def __init__(self):
        self.interval = 0

    def __enter__(self):
        self.time_start = time.time()
        return self

    def __exit__(self, *args):
        self.time_end = time.time()
        self.interval = self.time_end - self.time_start


class ExitException(click.ClickException):
    def __init__(self, msg, duration=None):
        if duration is not None:
            msg = '{} ({:0.4f} seconds)'.format(msg, duration)

        super(ExitException, self).__init__(msg)

    def show(self, output=None):
        if output is None:
            output = sys.stderr

        output.write(self.format_message())
        output.write('\n')


class ExitOkay(ExitException):
    exit_code = RET_OKAY

    def __init__(self, msg, duration=None):
        super(ExitOkay, self).__init__('OKAY: {}'.format(msg),
                                       duration=duration)


class ExitWarning(ExitException):
    exit_code = RET_WARN

    def __init__(self, msg, duration=None):
        super(ExitWarning, self).__init__('WARNING: {}'.format(msg),
                                          duration=duration)


class ExitCritical(ExitException):
    exit_code = RET_CRIT

    def __init__(self, msg, duration=None):
        super(ExitCritical, self).__init__('CRITICAL: {}'.format(msg),
                                           duration=duration)


class ExitWTF(ExitException):
    exit_code = RET_WTF

    def __init__(self, msg, duration=None):
        super(ExitCritical, self).__init__('UNKNOWN: {}'.format(msg),
                                           duration=duration)
