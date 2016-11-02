import click
import glanceclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

@click.command()
@click.option('--os-image-api-version', default='2',
              envvar='OS_IMAGE_API_VERSION')
@openstack.apply_openstack_options
@common.apply_common_options
def check_glance_api(os_image_api_version=None,
                   timeout_warning=None,
                   timeout_critical=None,
                   **kwargs):
    try:
        helper = openstack.OpenStack(**kwargs)
        glance = glanceclient.client.Client(os_image_api_version,
                                            session=helper.sess)

        with common.Timer() as t:
            images = list(glance.images.list())

    except glanceclient.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to list images: {}'.format(exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found {} images'.format(len(images))

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
