import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

@with_plugins(iter_entry_points('oschecks.check'))
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {'hello': 'word'}

