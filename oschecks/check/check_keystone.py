import click
import keystoneauth1
import keystoneclient
import requests

import oschecks.openstack as openstack
import oschecks.common as common


@click.group('keystone')
@openstack.apply_openstack_options
@click.pass_context
def cli(ctx, **kwargs):
    '''Health checks for Openstack Keystone'''
    ctx.obj.auth = openstack.OpenStack(**kwargs)


@cli.command()
@click.option('--os-identity-api-version', default='2',
              envvar='OS_IDENTITY_API_VERSION')
@common.apply_common_options
@click.pass_context
def check_api(ctx,
              os_identity_api_version=None,
              timeout_warning=None,
              timeout_critical=None,
              limit=None):
    '''Check if the Keystone API is responding.'''

    try:
        with common.Timer() as t:
            keystone = keystoneclient.client.Client(
                os_identity_api_version,
                session=ctx.obj.auth.sess)

            # this just stops flake8 from complaining
            keystone
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))

    msg = 'Keystone is active'

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)


@cli.command()
@click.option('--os-identity-api-version', default='2',
              envvar='OS_IDENTITY_API_VERSION')
@common.apply_common_options
@click.option('--service-name')
@click.argument('service_type', default='identity')
@click.pass_context
def check_service_exists(ctx,
                         os_identity_api_version=None,
                         timeout_warning=None,
                         timeout_critical=None,
                         limit=None,
                         service_type=None,
                         service_name=None):
    '''Check if a service of the given type exists in the service
    catalog.'''

    try:
        with common.Timer() as t:
            endpoint_url = ctx.obj.auth.sess.get_endpoint(
                service_type=service_type,
                service_name=service_name)
    except keystoneauth1.exceptions.EndpointNotFound:
        raise common.ExitCritical(
            'Service {} does not exist'.format(service_type),
            duration=t.interval)

    msg = 'Service {} exists at {}'.format(service_type, endpoint_url)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)


@cli.command()
@click.option('--os-identity-api-version', default='2',
              envvar='OS_IDENTITY_API_VERSION')
@common.apply_common_options
@click.option('--status-okay', default='200')
@click.option('--status-warning')
@click.option('--status-critical')
@click.option('--service-name')
@click.argument('service_type', default='identity')
@click.pass_context
def check_service_alive(ctx,
                        os_identity_api_version=None,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        service_type=None,
                        service_name=None,
                        status_okay=None,
                        status_warning=None,
                        status_critical=None,
                        **kwargs):
    '''Check if a service of the given type exists in the service
    catalog and if it reponds to HTTP requests.'''

    status_okay = ([int(x) for x in status_okay.split(',')]
                   if status_okay else [])
    status_warning = ([int(x) for x in status_warning.split(',')]
                      if status_warning else [])
    status_critical = ([int(x) for x in status_critical.split(',')]
                       if status_critical else [])

    try:
        endpoint_url = ctx.obj.auth.sess.get_endpoint(
            service_type=service_type,
            service_name=service_name)
        with common.Timer() as t:
            res = requests.get(endpoint_url)
    except requests.exceptions.ConnectionError:
        raise common.ExitCritical(
            'Cannot connect to service {} at {}'.format(
                service_type, endpoint_url))
    except keystoneauth1.exceptions.EndpointNotFound:
        raise common.ExitCritical(
            'Service {} does not exist'.format(service_type),
            duration=t.interval)

    msg = 'Received status {} from service {} at {}'.format(
        res.status_code, service_type, endpoint_url)

    if res.status_code in status_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    elif res.status_code not in status_okay:
        raise common.ExitCritical(msg, duration=t.interval)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
