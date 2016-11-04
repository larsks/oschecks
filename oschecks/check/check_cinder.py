import cinderclient
import cinderclient.client
import cinderclient.exceptions
import time

import oschecks.openstack as openstack
import oschecks.common as common


class CinderCommand(openstack.OpenstackCommand):
    '''This is the base class for all the Cinder checks.'''

    def take_action(self, parsed_args):
        super(CinderCommand, self).take_action(parsed_args)

        try:
            self.cinder = cinderclient.client.Client(
                parsed_args.os_volume_api_version,
                session=self.auth.sess)
        except cinderclient.exceptions.ClientException as exc:
            raise common.ExitCritical(
                'Failed to create Cinder client: {}'.format(exc))

    def get_volume(self, name_or_id):
        try:
            volume = self.cinder.volumes.get(name_or_id)
        except cinderclient.exceptions.NotFound:
            volume = self.cinder.volumes.find(name=name_or_id)

        return volume

    def volume_exists(self, volume_name):
        try:
            self.get_volume(volume_name)
        except cinderclient.exceptions.NoUniqueMatch:
            return True
        except cinderclient.exceptions.NotFound:
            return False
        else:
            return True

    def volume_status(self, volume):
        try:
            volume.get()
            return volume.status
        except cinderclient.exceptions.NotFound:
            return 'deleted'

    def wait_for_status(self, volume, status, timeout=None):
        with common.Timer(timeout=timeout) as t:
            while self.volume_status(volume) != status:
                time.sleep(1)
                t.tick()

    def delete_volume(self, volume, timeout=None):
        volume.delete()
        self.wait_for_status(volume, 'deleted', timeout=timeout)


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


class CheckVolumeCreateDelete(CinderCommand):

    default_timeout_warning = 20
    default_timeout_critical = 40

    def get_parser(self, prog_name):
        p = super(CheckVolumeCreateDelete, self).get_parser(prog_name)

        g = p.add_argument_group('Volume API Options')
        g.add_argument('--os-volume-api-version', default='2')
        g.add_argument('--volume-name', '--name', default='monitoring-test')
        g.add_argument('--volume-type')
        g.add_argument('--availability-zone')
        g.add_argument('--volume-ready-timeout', type=int, default=10)
        g.add_argument('--volume-delete-timeout', type=int, default=10)
        g.add_argument('--delete-existing', action='store_true')
        g.add_argument('volume_size', nargs='?', default=1, type=float)

        return p

    def ensure_test_volume_exists(self, parsed_args, ctx):
        '''Ensure the test volume exists'''

        if not self.volume_exists(parsed_args.volume_name):
            raise common.ExitCritical(
                'Test volume {.volume_name} is missing '
                '(but should exist)'.format(parsed_args))

    def ensure_test_volume_is_absent(self, parsed_args, ctx):
        '''Ensure the test volume is absent'''

        if self.volume_exists(parsed_args.volume_name):
            raise common.ExitCritical(
                "Test volume {.volume_name} exists (but shouldn't)".format(
                    parsed_args))

    def delete_old_test_volume(self, parsed_args, ctx):
        '''Delete existing test volume if --delete-existing'''
        if parsed_args.delete_existing:
            self.delete_test_volume(parsed_args, ctx)

    def delete_test_volume(self, parsed_args, ctx):
        '''Delete test volume'''
        try:
            volume = self.get_volume(parsed_args.volume_name)
            volume.delete()
            self.wait_for_status(volume, 'deleted',
                                 timeout=parsed_args.volume_delete_timeout)
        except cinderclient.exceptions.NoUniqueMatch:
                raise common.ExitCritical(
                    'Multiple volumes named {.volume_name}, aborting'.format(
                        parsed_args))
        except cinderclient.exceptions.NotFound:
            pass

    def create_test_volume(self, parsed_args, ctx):
        '''Create test volume'''

        volume = self.cinder.volumes.create(
            name=parsed_args.volume_name,
            size=parsed_args.volume_size,
            volume_type=parsed_args.volume_type,
            availability_zone=parsed_args.availability_zone)

        ctx.volume_created = True

        self.wait_for_status(volume, 'available',
                             timeout=parsed_args.volume_ready_timeout)

    def take_action(self, parsed_args):
        '''Check if the named Cinder volume exists.'''
        super(CheckVolumeCreateDelete, self).take_action(parsed_args)

        test_plan = (
            self.delete_old_test_volume,
            self.ensure_test_volume_is_absent,
            self.create_test_volume,
            self.ensure_test_volume_exists,
            self.delete_test_volume,
            self.ensure_test_volume_is_absent,
        )

        with common.Timer() as t:
            try:
                ctx = lambda: None
                ctx.volume_created = False
                for step in test_plan:
                    self.log.info('running step: {}'.format(
                        step.__doc__))
                    step(parsed_args, ctx)
            except cinderclient.exceptions.ClientException as exc:
                raise common.ExitCritical(
                    '{} failed: {}'.format(step.__doc__, exc))
            except common.TimeoutError:
                raise common.ExitCritical(
                    '{} timed out'.format(step.__doc__))
            finally:
                try:
                    if ctx.volume_created:
                        self.delete_test_volume(parsed_args, ctx)
                except cinderclient.exceptions.ClientException as exc:
                    raise common.ExitCritical(
                        'Failed to delete test volume: {}'.format(exc))

        msg = 'Successfully created and deleted volume {.volume_name}'.format(
            parsed_args)

        return (common.RET_OKAY, msg, t)
