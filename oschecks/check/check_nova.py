import click
import novaclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.group('nova')
def cli():
    '''Health checks for Openstack Nova'''

    pass

@cli.command()
@click.option('--os-compute-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@openstack.apply_openstack_options
@common.apply_common_options
def check_api(os_compute_api_version=None,
                   timeout_warning=None,
                   timeout_critical=None,
                   limit=None,
                   **kwargs):
    '''Check if Nova API is responding.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=helper.sess)

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
@openstack.apply_openstack_options
@common.apply_common_options
@click.argument('flavor', default='m1.small')
def check_flavor_exists(os_compute_api_version=None,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        flavor=None,
                        **kwargs):
    '''Check if the named flavor exists.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=helper.sess)

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
@openstack.apply_openstack_options
@common.apply_common_options
@click.argument('server')
def check_server_exists(os_compute_api_version=None,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        server=None,
                        **kwargs):
    '''Check if the named server exists.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=helper.sess)

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
