import click
import swiftclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.group('swift')
@openstack.apply_openstack_options
@click.pass_context
def cli(ctx, **kwargs):
    '''Health checks for Openstack Swift'''
    ctx.obj.auth = openstack.OpenStack(**kwargs)

@cli.command()
@common.apply_common_options
@click.pass_context
def check_api(ctx,
              timeout_warning=None,
              timeout_critical=None,
              limit=None):
    '''Check that the Swift API is responding.'''

    try:
        client = swiftclient.client.Connection(session=ctx.obj.auth.sess)

        with common.Timer() as t:
            containers = client.get_account(limit=limit)

    except swiftclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to list containers: {}'.format(exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found {} containers'.format(len(containers))

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)

@cli.command()
@common.apply_common_options
@click.argument('container')
@click.pass_context
def check_container_exists(ctx,
                           timeout_warning=None,
                           timeout_critical=None,
                           limit=None,
                           container=None):
    '''Check if the named container exists.'''

    try:
        client = swiftclient.client.Connection(session=ctx.obj.auth.sess)

        with common.Timer() as t:
            res = client.get_container(container)
    except swiftclient.exceptions.ClientException as exc:
        if exc.http_status == 404:
            msg = 'Container {} does not exist'.format(container)
        else:
            msg = 'Failed to get container {}: {}'.format(container, exc),

        raise common.ExitCritical(msg, duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))

    msg = 'Found container {}'.format(container)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)


@cli.command()
@common.apply_common_options
@click.argument('container')
@click.argument('obj')
@click.pass_context
def check_object_exists(ctx,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        container=None,
                        obj=None):
    '''Check if the named object exists in the named container exists.'''

    try:
        client = swiftclient.client.Connection(session=ctx.obj.auth.sess)

        with common.Timer() as t:
            res = client.get_object(container, obj)
    except swiftclient.exceptions.ClientException as exc:
        if exc.http_status == 404:
            msg = 'Object {} in container {} does not exist'.format(
                obj, container)
        else:
            msg = 'Failed to get object {} in container {}: {}'.format(
                obj, container, exc),

        raise common.ExitCritical(msg, duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))

    msg = 'Found object {} in container {} with {} bytes'.format(
        obj, container, res[0]['content-length'])

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
