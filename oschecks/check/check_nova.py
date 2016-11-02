import click
import novaclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.command()
@click.option('--os-compute-api-version', default='2',
              envvar='OS_COMPUTE_API_VERSION')
@openstack.apply_openstack_options
@common.apply_common_options
def check_nova_api(os_compute_api_version=None,
                   timeout_warning=None,
                   timeout_critical=None,
                   **kwargs):

    try:
        helper = openstack.OpenStack(**kwargs)
        nova = novaclient.client.Client(os_compute_api_version,
                                        session=helper.sess)

        with common.Timer() as t:
            servers = nova.servers.list()

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
