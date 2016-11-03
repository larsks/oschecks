import cliff.app
import cliff.commandmanager
import logging
import oschecks
import sys


class App(cliff.app.App):
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
            description, version,
            argparse_kwargs=argparse_kwargs)

        # cliff defaults to logging at INFO and above, which leads to
        # unnecessary clutter.  This is the equivalent of setting
        # --quiet by default.
        p.set_defaults(verbose_level=0)

        return p


def cli():
    app = App()
    return app.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(cli())
