import time
import click
import requests

from oschecks import common

@click.command()
@click.option('--method', '-m', default='GET',
              type=click.Choice(['GET', 'POST', 'PUT', 'DELETE', 'HEAD']))
@click.option('--status-okay', '-s', default='200')
@click.option('--status-warn', '-W')
@click.option('--status-critical', '--status-crit', '-C')
@click.option('--timeout', '-t', default=10)
@click.option('--ssl-verify/--no-ssl-verify', default=True)
@click.option('--ssl-ca')
@click.argument('url')
def check_http(url=None, method=None,
               status_okay=None,
               status_warn=None,
               status_crit=None,
               timeout=None,
               ssl_verify=None,
               ssl_ca=None):

    status_okay = status_okay.split(',') if status_okay else []
    status_warn = status_warn.split(',') if status_warn else []
    status_crit = status_crit.split(',') if status_crit else []
    methodfunc = getattr(requests, method.lower())

    if ssl_ca:
        ssl_verify = ssl_ca

    req_start = time.time()
    try:
        res = methodfunc(url, timeout=timeout,
                         verify=ssl_verify)
    except requests.exceptions.SSLError:
        raise common.ExitCritical('Certificate verification failed')
    except requests.exceptions.ConnectTimeout:
        raise common.ExitCritical('Timeout')
    req_end = time.time()
    delta = req_end - req_start

    msg = '[{}] {} ({:0.4f} seconds)'.format(res.status_code, res.reason, delta)

    if str(res.status_code) in status_crit:
        raise common.ExitCritical(msg)
    elif str(res.status_code) in status_warn:
        raise common.ExitWarning(msg)
    elif str(res.status_code) in status_okay:
        raise common.ExitOkay(msg)
    else:
        raise common.ExitCritical(msg)
