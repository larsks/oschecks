import cinderclient
import cinderclient.exceptions
import cinderclient.client

import oschecks.openstack as openstack
import oschecks.common as common


class CheckAPI(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckAPI, self).get_parser(prog_name)

        g = p.add_argument_group('Volume API Options')
        g.add_argument('--os-volume-api-version', default='2')

        return p

    def take_action(self, parsed_args):
        '''Check if the Cinder API is responding.'''
        super(CheckAPI, self).take_action(parsed_args)

        try:
            cinder = cinderclient.client.Client(
                parsed_args.os_volume_api_version,
                session=self.auth.sess)

            with common.Timer() as t:
                volumes = cinder.volumes.list(
                    limit=parsed_args.limit)
        except cinderclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list volumes: {}'.format(exc),
                    t)

        msg = 'Found {} volumes'.format(len(volumes))

        return (common.RET_OKAY, msg, t)


class CheckVolumeExists(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckVolumeExists, self).get_parser(prog_name)

        g = p.add_argument_group('Volume API Options')
        g.add_argument('--os-volume-api-version', default='2')
        g.add_argument('volume_name')

        return p

    def take_action(self, parsed_args):
        '''Check if the named Cinder volume exists.'''
        super(CheckVolumeExists, self).take_action(parsed_args)

        try:
            cinder = cinderclient.client.Client(
                parsed_args.os_volume_api_version,
                session=self.auth.sess)

            try:
                with common.Timer() as t:
                    volume = cinder.volumes.get(
                        parsed_args.volume_name)
            except cinderclient.exceptions.NotFound:
                with common.Timer() as t:
                    volume = cinder.volumes.find(
                        name=parsed_args.volume_name)
        except cinderclient.exceptions.NoUniqueMatch:
            return (common.RET_WARN,
                    'Too many matches for name {}'.format(
                        parsed_args.volume_name),
                    t)
        except cinderclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list volumes: {}'.format(exc),
                    t)

        msg = 'Found volume {} with id {}'.format(
            volume.name, volume.id)

        return (common.RET_OKAY, msg, t)
