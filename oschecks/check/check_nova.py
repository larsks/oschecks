import click
import novaclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.group('nova')
@openstack.apply_openstack_options
@click.pass_context
def cli(ctx, **kwargs):
    '''Health checks for Openstack Nova'''
    ctx.obj.auth = openstack.OpenStack(**kwargs)

@cli.command()
@click.option('--os-compute-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@common.apply_common_options
@click.pass_context
def check_api(ctx,
              os_compute_api_version=None,
              timeout_warning=None,
              timeout_critical=None,
              limit=None):
    '''Check if Nova API is responding.'''

    try:
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=ctx.obj.auth.sess)

        with common.Timer() as t:
            servers = nova.servers.list(limit=limit)

    except novaclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to list servers: {}'.format(exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found {} servers'.format(len(servers))

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)

@cli.command()
@click.option('--os-compute-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@common.apply_common_options
@click.argument('flavor', default='m1.small')
@click.pass_context
def check_flavor_exists(ctx,
                        os_compute_api_version=None,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        flavor=None):
    '''Check if the named flavor exists.'''

    try:
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=ctx.obj.auth.sess)

        try:
            with common.Timer() as t:
                res = nova.flavors.get(flavor)
        except novaclient.exceptions.NotFound:
            with common.Timer() as t:
                res = nova.flavors.find(name=flavor)

    except novaclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to get flavor {}: {}'.format(flavor, exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found flavor {} with id {}'.format(res.name, res.id)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)

@cli.command()
@click.option('--os-compute-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@common.apply_common_options
@click.argument('server')
@click.pass_context
def check_server_exists(ctx,
                        os_compute_api_version=None,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        server=None):
    '''Check if the named server exists.'''

    try:
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=ctx.obj.auth.sess)

        try:
            with common.Timer() as t:
                res = nova.servers.get(server)
        except novaclient.exceptions.NotFound:
            with common.Timer() as t:
                res = nova.servers.find(name=server)

    except novaclient.exceptions.NoUniqueMatch:
        raise common.ExitWarning(
            'Too many matches for server {}'.format(server),
            duration=t.interval)
    except novaclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to get server {}: {}'.format(server, exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found server {} with id {}'.format(res.name, res.id)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
