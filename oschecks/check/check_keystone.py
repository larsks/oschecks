import keystoneauth1
import keystoneclient
import requests

import oschecks.openstack as openstack
import oschecks.common as common


class KeystoneCommand(openstack.OpenstackCommand):
    def take_action(self, parsed_args):
        super(KeystoneCommand, self).take_action(parsed_args)

        try:
            self.keystone = keystoneclient.client.Client(
                parsed_args.os_identity_api_version,
                session=self.auth.sess)
        except keystoneauth1.exceptions.ClientException as exc:
            raise common.ExitCritical(
                   'Failed to authenticate: {}'.format(exc))

    def get_endpoint(self, service_type, service_name=None):
        endpoint_url = self.auth.sess.get_endpoint(
            service_type=service_type,
            service_name=service_name)

        return endpoint_url


class CheckAPI(KeystoneCommand):
    def get_parser(self, prog_name):
        p = super(CheckAPI, self).get_parser(prog_name)

        g = p.add_argument_group('Identity API Options')
        g.add_argument('--os-identity-api-version')

        return p

    def take_action(self, parsed_args):
        '''Check if the Keystone API is responding.'''
        super(CheckAPI, self).take_action(parsed_args)

        # This check is mostly a no-op because if we are able to get a
        # keystone client in KeystoneCommand, we already know Keystone
        # is running.
        msg = 'Keystone is active'
        return (common.RET_OKAY, msg, None)


class CheckServiceExists(KeystoneCommand):
    def get_parser(self, prog_name):
        p = super(CheckServiceExists, self).get_parser(prog_name)

        g = p.add_argument_group('Identity API Options')
        g.add_argument('--os-identity-api-version')
        g.add_argument('service_type', nargs='?', default='identity')
        g.add_argument('service_name', nargs='?')

        return p

    def take_action(self, parsed_args):
        '''Check if a service of the given type exists in the service
        catalog.'''

        super(CheckServiceExists, self).take_action(parsed_args)

        try:
            with common.Timer() as t:
                endpoint_url = self.get_endpoint(
                    service_type=parsed_args.service_type,
                    service_name=parsed_args.service_name)
        except keystoneauth1.exceptions.EndpointNotFound:
            return (common.RET_CRIT,
                    'Service {} does not exist'.format(
                        parsed_args.service_type),
                    t)

        msg = 'Service {} exists at {}'.format(
            parsed_args.service_type, endpoint_url)

        return (common.RET_OKAY, msg, t)


class CheckServiceAlive(KeystoneCommand):
    def get_parser(self, prog_name):
        p = super(CheckServiceAlive, self).get_parser(prog_name)

        g = p.add_argument_group('Identity API Options')
        g.add_argument('--os-identity-api-version')
        g.add_argument('service_type', nargs='?', default='identity')
        g.add_argument('service_name', nargs='?')

        g = p.add_argument_group('HTTP Request Options')
        g.add_argument('--status-okay',
                       action='append',
                       default=[200],
                       type=int)
        g.add_argument('--status-warning',
                       action='append',
                       default=[])
        g.add_argument('--status-critical',
                       action='append',
                       default=[])

        return p

    def take_action(self, parsed_args):
        '''Check if a service of the given type exists in the service
        catalog and if it reponds to HTTP requests.'''

        super(CheckServiceAlive, self).take_action(parsed_args)

        try:
            endpoint_url = self.get_endpoint(
                service_type=parsed_args.service_type,
                service_name=parsed_args.service_name)

            with common.Timer() as t:
                res = requests.get(endpoint_url)
        except keystoneauth1.exceptions.EndpointNotFound:
            return (common.RET_CRIT,
                    'Service {} does not exist'.format(
                        parsed_args.service_type),
                    t)
        except requests.exceptions.ConnectionError:
            raise common.ExitCritical(
                'Cannot connect to service {} at {}'.format(
                    parsed_args.service_type, endpoint_url))

        msg = 'Received status {} from service {} at {}'.format(
            res.status_code, parsed_args.service_type, endpoint_url)

        exitcode = common.RET_OKAY

        if res.status_code in parsed_args.status_warning:
            exitcode = common.RET_WARN
        elif res.status_code not in parsed_args.status_okay:
            exitcode = common.RET_CRIT

        return (exitcode, msg, t)
