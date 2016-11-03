import click
import cinderclient
import cinderclient.exceptions
import cinderclient.client

import oschecks.openstack as openstack
import oschecks.common as common


@click.group('cinder')
@openstack.apply_openstack_options
@click.pass_context
def cli(ctx, **kwargs):
    '''Health checks for Openstack Cinder'''
    ctx.obj.auth = openstack.OpenStack(**kwargs)


@cli.command()
@click.option('--os-volume-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@common.apply_common_options
@click.pass_context
def check_api(ctx,
              os_volume_api_version=None,
              timeout_warning=None,
              timeout_critical=None,
              limit=None):
    '''Check that the Cinder API is responding.'''

    try:
        cinder = cinderclient.client.Client(os_volume_api_version,
                                            session=ctx.obj.auth.sess)

        with common.Timer() as t:
            volumes = cinder.volumes.list(limit=limit)

    except cinderclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to list volumes: {}'.format(exc),
            duration=t.interval)

    msg = 'Found {} volumes'.format(len(volumes))

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)


@cli.command()
@click.option('--os-volume-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@common.apply_common_options
@click.argument('volume')
@click.pass_context
def check_volume_exists(ctx,
                        os_volume_api_version=None,
                        timeout_warning=None,
                        timeout_critical=None,
                        limit=None,
                        volume=None):
    '''Check if the named volume exists.'''

    try:
        cinder = cinderclient.client.Client(os_volume_api_version,
                                            session=ctx.obj.auth.sess)

        try:
            with common.Timer() as t:
                res = cinder.volumes.get(volume)
        except cinderclient.exceptions.NotFound:
            with common.Timer() as t:
                res = cinder.volumes.find(name=volume)
    except cinderclient.exceptions.NoUniqueMatch:
        raise common.ExitWarning(
            'Too many matches for volume {}'.format(volume),
            duration=t.interval)
    except cinderclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to get volume {}: {}'.format(volume, exc),
            duration=t.interval)

    msg = 'Found volume {} with id {}'.format(
        res.name, res.id)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
