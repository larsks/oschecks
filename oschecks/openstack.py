#!/usr/bin/python

import click
import logging
import os
import keystoneauth1
import os_client_config as os_client_config

import oschecks.common as common

LOG = logging.getLogger(__name__)

openstack_auth_option_names = [
    'auth_url',
    'domain_id',
    'domain_name',
    'default_domain_id',
    'default_domain_name',
    'password',
    'project_domain_id',
    'project_domain_name',
    'project_id',
    'project_name',
    'tenant_id',
    'tenant_name',
    'user_domain_id',
    'user_domain_name',
    'username',
]

openstack_auth_option_defaults = {
    'default_domain_name': 'default',
}

openstack_options = [
    click.option('--cloud',
                 help='Named cloud from os_client_config clouds.yaml')
] + [
    click.option('--os-{}'.format(name.replace('_', '-')),
                 name,
                 default=openstack_auth_option_defaults.get(name),
                 envvar='OS_{}'.format(name.upper()))
    for name in openstack_auth_option_names
]

def apply_openstack_options(func):
    for opt in openstack_options:
        func = opt(func)

    return func


class ClientNotAvailable(Exception):
    pass


class OpenStack(object):
    '''Loads authentication configuration using os_client_config and creates
    a keystoneauth1 session for authenticating to other services.'''

    def __init__(self, cloud=None, **kwargs):
        params = {k: v for k, v in kwargs.items()
                  if k in openstack_auth_option_names}

        try:
            cfg = os_client_config.config.OpenStackConfig().get_one_cloud(cloud=cloud, **params)
            sess = cfg.get_session()
        except (
                keystoneauth1.exceptions.ClientException,
                os_client_config.exceptions.OpenStackConfigException
        ) as exc:
            raise common.ExitCritical(
                'Failed to authenticate: {}'.format(exc))

        self.cfg = cfg
        self.sess = sess


if __name__ == '__main__':
    o = OpenStack()
