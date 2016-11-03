import novaclient.client
import oschecks.openstack as openstack
import oschecks.common as common


class CheckAPI(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckAPI, self).get_parser(prog_name)

        g = p.add_argument_group('Compute API Options')
        g.add_argument('--os-compute-api-version', default=2)

        return p

    def take_action(self, parsed_args):
        '''Check if Nova API is responding.'''
        super(CheckAPI, self).take_action(parsed_args)

        try:
            nova = novaclient.client.Client(
                parsed_args.os_compute_api_version,
                session=self.auth.sess)

            with common.Timer() as t:
                servers = nova.servers.list(limit=parsed_args.limit)
        except novaclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list servers: {}'.format(exc),
                    t)

        msg = 'Found {} servers'.format(len(servers))

        return (common.RET_OKAY, msg, t)


class CheckFlavorExists(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckFlavorExists, self).get_parser(prog_name)

        g = p.add_argument_group('Compute API Options')
        g.add_argument('--os-compute-api-version', default=2)
        g.add_argument('flavor_name', nargs='?', default='m1.small')

        return p

    def take_action(self, parsed_args):
        '''Check if the named flavor exists.'''
        super(CheckFlavorExists, self).take_action(parsed_args)

        try:
            nova = novaclient.client.Client(
                parsed_args.os_compute_api_version,
                session=self.auth.sess)

            try:
                with common.Timer() as t:
                    flavor = nova.flavors.get(parsed_args.flavor_name)
            except novaclient.exceptions.NotFound:
                with common.Timer() as t:
                    flavor = nova.flavors.find(name=parsed_args.flavor_name)
        except novaclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list servers: {}'.format(exc),
                    t)

        msg = 'Found flavor {} with id {}'.format(
            flavor.name, flavor.id)

        return (common.RET_OKAY, msg, t)


class CheckServerExists(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckServerExists, self).get_parser(prog_name)

        g = p.add_argument_group('Compute API Options')
        g.add_argument('--os-compute-api-version', default=2)
        g.add_argument('server_name')

        return p

    def take_action(self, parsed_args):
        '''Check if the named server exists.'''
        super(CheckServerExists, self).take_action(parsed_args)

        try:
            nova = novaclient.client.Client(
                parsed_args.os_compute_api_version,
                session=self.auth.sess)

            try:
                with common.Timer() as t:
                    server = nova.servers.get(parsed_args.server_name)
            except novaclient.exceptions.NotFound:
                with common.Timer() as t:
                    server = nova.servers.find(name=parsed_args.server_name)
        except novaclient.exceptions.NoUniqueMatch:
            return (common.RET_WARN,
                    'Too many matches for server {}'.format(
                        parsed_args.server_name),
                    t)
        except novaclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to locate server {}: {}'.format(
                        parsed_args.server_name, exc),
                    t)

        msg = 'Found server {} with id {}'.format(
            server.name, server.id)

        return (common.RET_OKAY, msg, t)
