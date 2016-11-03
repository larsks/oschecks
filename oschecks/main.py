import click
import logging
from click_plugins import with_plugins
from pkg_resources import iter_entry_points


@with_plugins(iter_entry_points('oschecks.check'))
@click.group()
@click.option('--verbose', '-v', 'loglevel', flag_value='INFO')
@click.option('--debug', '-d', 'loglevel', flag_value='DEBUG')
@click.pass_context
def cli(ctx, loglevel=None):
    # This gives us a place to assign arbitrary attributes.
    ctx.obj = lambda: None

    if loglevel is not None:
        logging.root.setLevel(loglevel)
