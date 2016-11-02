import click
import cinderclient
import cinderclient.exceptions
import cinderclient.client
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.command()
@click.option('--os-volume-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@openstack.apply_openstack_options
@common.apply_common_options
def check_cinder_api(os_volume_api_version=None,
                   timeout_warning=None,
                   timeout_critical=None,
                   **kwargs):

    try:
        helper = openstack.OpenStack(**kwargs)
        cinder = cinderclient.client.Client(os_volume_api_version,
                                            session=helper.sess)

        with common.Timer() as t:
            volumes = cinder.volumes.list()

    except cinderclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to list volumes: {}'.format(exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found {} volumes'.format(len(volumes))

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
