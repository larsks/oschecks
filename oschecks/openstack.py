#!/usr/bin/python

import click
import logging
import os
import keystoneauth1.loading
import keystoneauth1.session

from novaclient import client

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
    'identity_api_version'
]

openstack_auth_option_defaults = {
    'default_domain_name': 'default',
}

openstack_options = [
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
    def __init__(self, identity_api_version=None, **kwargs):
        if identity_api_version is not None:
            raise NotImplementedError('Support for explicitly setting the '
                                      'identity API version is currently '
                                      'unimplemented.')

        kwargs = {k: v for k, v in kwargs.items()
                  if k in openstack_auth_option_names}

        params = self.params_from_env()
        params.update(kwargs)
        self.params = params

        loader = keystoneauth1.loading.get_plugin_loader('password')
        auth = loader.load_from_options(**params)
        sess = keystoneauth1.session.Session(auth=auth)

        self.auth = auth
        self.sess = sess

    def params_from_env(self):
        params = {name: os.environ.get('OS_{}'.format(name.upper()))
                  for name in openstack_auth_option_names
                  if 'OS_{}'.format(name.upper()) in os.environ}

        return params


if __name__ == '__main__':
    o = OpenStack()
