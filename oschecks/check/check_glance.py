import click
import glanceclient

import oschecks.openstack as openstack
import oschecks.common as common


class NoUniqueMatch(Exception):
    pass


@click.group('glance')
@openstack.apply_openstack_options
@click.pass_context
def cli(ctx, **kwargs):
    '''Health checks for Openstack Glance'''
    ctx.obj.auth = openstack.OpenStack(**kwargs)


@cli.command()
@click.option('--os-image-api-version', default='2',
              envvar='OS_IMAGE_API_VERSION')
@common.apply_common_options
@click.pass_context
def check_api(ctx,
              os_image_api_version=None,
              timeout_warning=None,
              timeout_critical=None,
              limit=None):
    '''Check if the Glance API is responding.'''

    try:
        glance = glanceclient.client.Client(os_image_api_version,
                                            session=ctx.obj.auth.sess)

        with common.Timer() as t:
            images = list(glance.images.list(limit=limit))

    except glanceclient.exc.ClientException as exc:
        raise common.ExitCritical(
            'Failed to list images: {}'.format(exc),
            duration=t.interval)

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
@common.apply_common_options
@click.argument('image')
@click.pass_context
def check_image_exists(ctx,
                       os_image_api_version=None,
                       timeout_warning=None,
                       timeout_critical=None,
                       limit=None,
                       image=None):
    '''Check if the named image exists.'''

    try:
        glance = glanceclient.client.Client(os_image_api_version,
                                            session=ctx.obj.auth.sess)

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

    msg = 'Found images {} with id {}'.format(res.name, res.id)

    if timeout_critical is not None and t.interval >= timeout_critical:
        raise common.ExitCritical(msg, duration=t.interval)
    elif timeout_warning is not None and t.interval >= timeout_warning:
        raise common.ExitWarning(msg, duration=t.interval)
    else:
        raise common.ExitOkay(msg, duration=t.interval)
