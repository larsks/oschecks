import click
import glanceclient
import keystoneauth1
import time

import oschecks.openstack as openstack
import oschecks.common as common

class NoUniqueMatch(Exception):
    pass

@click.group('glance')
def cli():
    '''Health checks for Openstack Glance'''

    pass

@cli.command()
@click.option('--os-image-api-version', default='2',
              envvar='OS_IMAGE_API_VERSION')
@openstack.apply_openstack_options
@common.apply_common_options
def check_api(os_image_api_version=None,
                     timeout_warning=None,
                     timeout_critical=None,
                     limit=None,
                     **kwargs):
    '''Check if the Glance API is responding.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        glance = glanceclient.client.Client(os_image_api_version,
                                            session=helper.sess)

        with common.Timer() as t:
            images = list(glance.images.list(limit=limit))

    except glanceclient.exc.ClientException as exc:
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

@cli.command()
@click.option('--os-image-api-version', default='2',
              envvar='OS_IMAGE_API_VERSION')
@openstack.apply_openstack_options
@common.apply_common_options
@click.argument('image')
def check_image_exists(os_image_api_version=None,
                       timeout_warning=None,
                       timeout_critical=None,
                       limit=None,
                       image=None,
                       **kwargs):
    '''Check if the named image exists.'''

    try:
        helper = openstack.OpenStack(**kwargs)
        glance = glanceclient.client.Client(os_image_api_version,
                                            session=helper.sess)

        try:
            with common.Timer() as t:
                res = glance.images.get(image)
        except glanceclient.exc.NotFound:
            with common.Timer() as t:
                res = [x for x in glance.images.list()
                       if x.name == image]

                if len(res) > 1:
                    raise NoUniqueMatch()

                res = res[0]
    except NoUniqueMatch:
        raise common.ExitWarning(
            'Too many matches for image {}'.format(image),
            duration=t.interval)
    except glanceclient.exc.ClientException as exc:
        raise common.ExitCritical(
            'Failed to get images {}: {}'.format(image, exc),
            duration=t.interval)
    except keystoneauth1.exceptions.ClientException as exc:
        raise common.ExitCritical(
            'Failed to authenticate: {}'.format(exc))


    msg = 'Found images {} with id {}'.format(res.name, res.id)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
