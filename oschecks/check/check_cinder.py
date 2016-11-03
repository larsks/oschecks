import cinderclient
import cinderclient.client
import cinderclient.exceptions
import logging
import time

from contextlib import contextmanager

import oschecks.openstack as openstack
import oschecks.common as common


class CinderCommand(openstack.OpenstackCommand):
    def take_action(self, parsed_args):
        '''Check if the Cinder API is responding.'''
        super(CinderCommand, self).take_action(parsed_args)

        try:
            self.cinder = cinderclient.client.Client(
                parsed_args.os_volume_api_version,
                session=self.auth.sess)
        except cinderclient.exceptions.ClientException as exc:
            raise common.ExitCritical(
                'Unable to create Cinder client: {}'.format(exc))

    def volume_exists(self, volume_name):
        try:
            try:
                # Try getting the volume by id
                self.cinder.volumes.get(
                    volume_name)
            except cinderclient.exceptions.NotFound:
                # Maybe it was a name after all
                volumes = self.cinder.volumes.findall(
                    name=volume_name)

                return bool(volumes)
        except:
            print 'exception'
            return False
        else:
            return True


class CheckAPI(CinderCommand):
    def get_parser(self, prog_name):
        p = super(CheckAPI, self).get_parser(prog_name)

        g = p.add_argument_group('Volume API Options')
        g.add_argument('--os-volume-api-version', default='2')

        return p

    def take_action(self, parsed_args):
        '''Check if the Cinder API is responding.'''
        super(CheckAPI, self).take_action(parsed_args)

        try:
            with common.Timer() as t:
                volumes = self.cinder.volumes.list(
                    limit=parsed_args.limit)
        except cinderclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list volumes: {}'.format(exc),
                    t)

        msg = 'Found {} volumes'.format(len(volumes))

        return (common.RET_OKAY, msg, t)


class CheckVolumeExists(CinderCommand):
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
            try:
                with common.Timer() as t:
                    volume = self.cinder.volumes.get(
                        parsed_args.volume_name)
            except cinderclient.exceptions.NotFound:
                with common.Timer() as t:
                    volume = self.cinder.volumes.find(
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


class temporaryVolume(object):
    '''This is a context manager that is used by the create/delete
    volume check to ensure that the test volume is deleted.'''

    log = logging.getLogger(__name__)

    def __init__(self, cinder,
                 volume_size, volume_name,
                 volume_type=None,
                 availability_zone=None,
                 timeout=None):

        self.cinder = cinder
        self.volume_size = volume_size
        self.volume_name = volume_name
        self.volume_type = volume_type
        self.availability_zone = availability_zone

    def __enter__(self):
        self.volume = self.cinder.volumes.create(
            name=self.volume_name,
            size=self.volume_size,
            volume_type=self.volume_type,
            availability_zone=self.availability_zone)
        self.log.info('created volume {0.name} '
                      '(id {0.id}) with size {0.size}'.format(self.volume))

    def __exit__(self, *args):
        self.volume.delete()
        self.log.info('deleted volume {0.name} '
                      '(id {0.id}) with size {0.id}'.format(self.volume))

    @property
    def status(self):
        self.volume.get()
        return self.volume.status

    def wait_ready(self, timeout=None):
        with common.Timer(timeout=timeout) as t:
            while self.status != 'available':
                time.sleep(1)
                t.tick()


class CheckVolumeCreateDelete(CinderCommand):

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        p = super(CheckVolumeCreateDelete, self).get_parser(prog_name)

        g = p.add_argument_group('Volume API Options')
        g.add_argument('--os-volume-api-version', default='2')
        g.add_argument('--volume-name', '--name', default='monitoring-test')
        g.add_argument('--volume-type')
        g.add_argument('--availability-zone')
        g.add_argument('--volume-ready-timeout', type=int, default=10)
        g.add_argument('volume_size', nargs='?', default=1, type=float)

        return p

    def take_action(self, parsed_args):
        '''Check if the named Cinder volume exists.'''
        super(CheckVolumeCreateDelete, self).take_action(parsed_args)

        if self.volume_exists(parsed_args.volume_name):
            return (common.RET_CRIT,
                    'A volume named "{}" already exists'.format(
                        parsed_args.volume_name),
                    None)

        volume = temporaryVolume(
            self.cinder,
            parsed_args.volume_size,
            parsed_args.volume_name,
            volume_type=parsed_args.volume_type,
            availability_zone=parsed_args.availability_zone)

        try:
            with common.Timer() as t, volume:
                volume.wait_ready(timeout=parsed_args.volume_ready_timeout)
        except common.TimeoutError as exc:
            return (common.RET_CRIT,
                    'Timeout waiting for volume {} to become ready'.format(
                        parsed_args.volume_name),
                    t)
        except cinderclient.exceptions.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to create/delete {}: {}'.format(
                        parsed_args.volume_name, exc),
                    t)

        msg = 'Successfully created and deleted volume {}'.format(
            parsed_args.volume_name)

        return (common.RET_OKAY, msg, t)
