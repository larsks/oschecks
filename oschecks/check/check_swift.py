import swiftclient
import oschecks.openstack as openstack
import oschecks.common as common


class CheckAPI(openstack.OpenstackCommand):
    def take_action(self, parsed_args):
        '''Check if the Glance API is responding.'''
        super(CheckAPI, self).take_action(parsed_args)

        try:
            swift = swiftclient.client.Connection(session=self.auth.sess)

            with common.Timer() as t:
                # XXX: It looks like swiftclient ignores the limit
                # parameter.
                containers = swift.get_account(
                    limit=parsed_args.limit)
        except swiftclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list containers: {}'.format(exc),
                    t)

        msg = 'Found {} containers'.format(len(containers))

        return (common.RET_OKAY, msg, t)


class CheckContainerExists(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckContainerExists, self).get_parser(prog_name)

        g = p.add_argument_group('Object Storage API Options')
        g.add_argument('container_name')

        return p

    def take_action(self, parsed_args):
        '''Check if the Glance API is responding.'''
        super(CheckContainerExists, self).take_action(parsed_args)

        try:
            swift = swiftclient.client.Connection(session=self.auth.sess)

            with common.Timer() as t:
                with common.Timer() as t:
                    container = swift.get_container(
                        parsed_args.container_name)
        except swiftclient.exceptions.ClientException as exc:
            if exc.http_status == 404:
                msg = 'Container {} does not exist'.format(
                    parsed_args.container_name)
            else:
                msg = 'Failed to retrieve container {}: {}'.format(
                    parsed_args.container_name, exc),

            return (common.RET_CRIT, msg, t)

        msg = 'Found container {} with {} objects'.format(
            parsed_args.container_name,
            container[0]['x-container-object-count'])

        return (common.RET_OKAY, msg, t)


class CheckObjectExists(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckObjectExists, self).get_parser(prog_name)

        g = p.add_argument_group('Object Storage API Options')
        g.add_argument('container_name')
        g.add_argument('object_name')

        return p

    def take_action(self, parsed_args):
        '''Check if the Glance API is responding.'''
        super(CheckObjectExists, self).take_action(parsed_args)

        try:
            swift = swiftclient.client.Connection(session=self.auth.sess)

            with common.Timer() as t:
                with common.Timer() as t:
                    container = swift.get_object(
                        parsed_args.container_name,
                        parsed_args.object_name)
        except swiftclient.exceptions.ClientException as exc:
            if exc.http_status == 404:
                msg = 'Object {} in container {} does not exist'.format(
                    parsed_args.object_name,
                    parsed_args.container_name)
            else:
                msg = 'Failed to retrieve object {} fromContainer container {}: {}'.format(
                    parsed_args.object_name,
                    parsed_args.container_name,
                    exc),

            return (common.RET_CRIT, msg, t)

        msg = 'Found object {} in container {} with {} bytes'.format(
            parsed_args.object_name,
            parsed_args.container_name,
            container[0]['content-length'])

        return (common.RET_OKAY, msg, t)
