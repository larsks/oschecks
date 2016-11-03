## Getting started

Clone the repository:

    $ git clone https://github.com/larsks/oschecks.git

Set up and activate a virtualenv:

    $ virtualenv .venv
    $ . .venv/bin/activate

Install:

    $ pip install -e .

Enjoy:

    $ oschecks --help
    usage: oschecks [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

    oschecks health checks

    optional arguments:
      --version            show program's version number and exit
      -v, --verbose        Increase verbosity of output. Can be repeated.
      -q, --quiet          Suppress output except warnings and errors.
      --log-file LOG_FILE  Specify a file to log output. Disabled by default.
      -h, --help           Show help message and exit.
      --debug              Show tracebacks on errors.

    Commands:
      cinder api
      cinder volume exists
      complete       print bash completion command
      glance api
      glance image exists
      help           print detailed help for another command
      keystone api
      keystone service alive
      keystone service exists
      nova api
      nova flavor exists
      nova server exists
      swift api
      swift container exists
      swift object exists

## The checks

### Nova

- `oschecks nova api`
- `oschecks nova server exists <server_name_or_id>`
- `oschecks nova flavor exists <flavor_name_or_id>`

### Glance

- `oschecks glance api`
- `oschecks glance image exists <image_name_or_id>`

### Cinder

- `oschecks cinder api`
- `oschecks cinder volume exists <volume_name_or_id>`

### Keystone

- `oschecks keystone api`
- `oschecks keystone service exists <service_type> [<service_name>]`
- `oschecks keystone service alive <service_type> [<service_name>]`

### Swift

- `oschecks swift api`
- `oschecks swift container exists <container_name>`
- `oschecks swift object exists <container_name> <object_name>`

## See also

- [Health checks for systemd units][oschecks_systemd]

[oschecks_systemd]: https://github.com/larsks/oschecks_systemd
