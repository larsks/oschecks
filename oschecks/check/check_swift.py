import click
import swiftclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.group('swift')
def cli():
    '''Health checks for Openstack Swift'''
    pass

@cli.command()
@openstack.apply_openstack_options
@common.apply_common_options
def check_api(timeout_warning=None,
              timeout_critical=None,
              limit=None,
              **kwargs):
    '''Check that the Swift API is responding.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        client = swiftclient.client.Connection(session=helper.sess)

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
@openstack.apply_openstack_options
@common.apply_common_options
@click.argument('container')
def check_container_exists(timeout_warning=None,
                           timeout_critical=None,
                           limit=None,
                           container=None,
                           **kwargs):
    '''Check if the named container exists.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        client = swiftclient.client.Connection(session=helper.sess)

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
@openstack.apply_openstack_options
@common.apply_common_options
@click.argument('container')
@click.argument('obj')
def check_object_exists(timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        container=None,
                        obj=None,
                        **kwargs):
    '''Check if the named object exists in the named container exists.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        client = swiftclient.client.Connection(session=helper.sess)

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
