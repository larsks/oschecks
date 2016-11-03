import glanceclient
import oschecks.openstack as openstack
import oschecks.common as common


class NonUniqueMatch(Exception):
    pass


class CheckAPI(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckAPI, self).get_parser(prog_name)

        g = p.add_argument_group('Image API Options')
        g.add_argument('--os-image-api-version', default='2')

        return p

    def take_action(self, parsed_args):
        '''Check if the Glance API is responding.'''
        super(CheckAPI, self).take_action(parsed_args)

        try:
            glance = glanceclient.client.Client(
                parsed_args.os_image_api_version,
                session=self.auth.sess)

            with common.Timer() as t:
                images = list(glance.images.list(
                    limit=parsed_args.limit))

        except glanceclient.exc.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list images: {}'.format(exc),
                    t)

        msg = 'Found {} images'.format(len(images))

        return (common.RET_OKAY, msg, t)


class CheckImageExists(openstack.OpenstackCommand):
    def get_parser(self, prog_name):
        p = super(CheckImageExists, self).get_parser(prog_name)

        g = p.add_argument_group('Image API Options')
        g.add_argument('--os-image-api-version', default='2')
        g.add_argument('image_name')

        return p

    def take_action(self, parsed_args):
        '''Check if the named image exists.'''
        super(CheckImageExists, self).take_action(parsed_args)

        try:
            glance = glanceclient.client.Client(
                parsed_args.os_image_api_version,
                session=self.auth.sess)

            try:
                with common.Timer() as t:
                    image = glance.images.get(
                        parsed_args.image_name)
            except glanceclient.exc.NotFound:
                with common.Timer() as t:
                    images = [image for image in glance.images.list()
                              if image.name == parsed_args.image_name]

                    if not images:
                        raise glanceclient.exc.NotFound(
                            parsed_args.image_name)

                    if len(images) > 1:
                        raise NonUniqueMatch()

                    image = images[0]
        except NonUniqueMatch:
            return (common.RET_WARN,
                    'Too many matches for image name {}'.format(
                        parsed_args.image_name),
                    t)
        except glanceclient.exc.NotFound as exc:
            return (common.RET_CRIT,
                    'Image named {} does not exist.'.format(
                        parsed_args.image_name),
                    t)
        except glanceclient.exc.ClientException as exc:
            return (common.RET_CRIT,
                    'Failed to list images: {}'.format(exc),
                    t)

        msg = 'Found image {} with id {}'.format(
            image.name, image.id)

        return (common.RET_OKAY, msg, t)
