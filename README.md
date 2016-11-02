## Getting started

Clone the repository:

    $ git clone https://github.com/larsks/oschecks.git

Set up and activate a virtualenv:

    $ virtualenv .venv
    $ . .venv/bin/activate

Install:

    $ pip install -e .

Enjoy:

    Usage: oschecks [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --verbose
      -d, --debug
      --help         Show this message and exit.

    Commands:
      cinder    Health checks for Openstack Cinder
      glance    Health checks for Openstack Glance
      keystone  Health checks for Openstack Keystone
      nova      Health checks for Openstack Nova
      swift     Health checks for Openstack Swift

## The checks

### Nova

- `oschecks nova check_api`
- `oschecks nova check_server_exists`
- `oschecks nova check_flavor_exists`

### Glance

- `oschecks glance check_api`
- `oschecks glance check_image_exists`

### Cinder

- `oschecks cinder check_api`
- `oschecks cinder check_volume_exists`

### Keystone

- `oschecks keystone check_api`
- `oschecks keystone check_service_exists`
- `oschecks keystone check_service_alive`

### Swift

- `oschecks swift check_api`
- `oschecks swift check_container_exists`
- `oschecks swift check_object_exists`

## See also

- [Health checks for systemd units][oschecks_systemd]

[oschecks_systemd]: https://github.com/larsks/oschecks_systemd
