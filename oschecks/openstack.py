#!/usr/bin/python

import keystoneauth1
import os_client_config as os_client_config

import oschecks.common as common

openstack_option_names = [
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

openstack_option_defaults = {
    'default_domain_name': 'default',
}


class Openstack(object):
    '''Loads authentication configuration using os_client_config and creates
    a keystoneauth1 session for authenticating to other services.'''

    def __init__(self, parsed_args):
        try:
            cfg = (
                os_client_config.config
                .OpenStackConfig()
                .get_one_cloud(argparse=parsed_args))
            sess = cfg.get_session()
        except (
                keystoneauth1.exceptions.ClientException,
                os_client_config.exceptions.OpenStackConfigException
        ) as exc:
            raise common.ExitCritical(
                'Failed to authenticate: {}'.format(exc))

        self.cfg = cfg
        self.sess = sess


class OpenstackAuthCommand(common.CheckCommand):
    '''A command that provides all the standard Keystone
    authentication options.'''

    def get_parser(self, prog_name):
        p = super(OpenstackAuthCommand, self).get_parser(prog_name)
        g = p.add_argument_group('Openstack Authentication Options')

        for opt in openstack_option_names:
            g.add_argument('--os-{}'.format(opt.replace('_', '-')),
                           dest=opt,
                           default=openstack_option_defaults.get(opt))

        g.add_argument('--cloud')

        return p

    def take_action(self, parsed_args):
        self.auth = Openstack(parsed_args)


class OpenstackCommand(OpenstackAuthCommand,
                       common.TimeoutCommand,
                       common.LimitCommand):
    '''This is the base class used by most of the OpenStack API
    checks.  It includes the Openstack authentication options, the
    timing options (-w/--warning and -c/--critical), and the limit
    options (-l/--limit).'''

    pass
