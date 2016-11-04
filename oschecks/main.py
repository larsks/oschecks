import cliff.app
import cliff.commandmanager
import oschecks
import sys
import logging
import argparse


class App(cliff.app.App):
    '''An application that provides health checks for Openstack and other
    services.'''

    # override some cliff defaults
    CONSOLE_MESSAGE_FORMAT = '%(name)s %(message)s'
    DEFAULT_VERBOSE_LEVEL = 0

    def __init__(self):
        super(App, self).__init__(
            description='oschecks health checks',
            version=oschecks.__version__,
            command_manager=(
                cliff.commandmanager.CommandManager('oschecks.check')
            ),
            deferred_help=True,
        )

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        p = super(App, self).build_option_parser(
            description, version, argparse_kwargs=argparse_kwargs)

        p.add_argument('--debug-requests',
                       action='store_true',
                       help=argparse.SUPPRESS)

        return p

    def configure_logging(self, *args, **kwargs):
        super(App, self).configure_logging(*args, **kwargs)

        # inhibit log messages from the requests subsystem
        # unless --debug-requests was on the command line
        if not self.options.debug_requests:
            log = logging.getLogger('requests')
            log.setLevel('WARNING')


def cli():
    app = App()
    return app.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(cli())
