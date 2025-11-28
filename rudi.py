#!/usr/bin/env python3

import sys
import yaml
import subprocess

CHGRP = '/bin/chgrp '
CHMOD = '/bin/chmod '
CHOWN = '/bin/chown '
DPKG = '/usr/bin/apt-get'
DEFAULT_CONF = 'rudi.yaml'
DPKG_INSTALL = f'{DPKG} install -y '
DPKG_REINSTALL = f'{DPKG_INSTALL} --reinstall'
DPKG_AUTOPURGE = f'{DPKG} remove --auto-remove --purge -y '
MKDIR_P_M = '/bin/mkdir -p -m '
SERVICE = '/usr/sbin/service '
START = ' start'
STOP = ' stop'


def do_file(file):
    """Deploy a file with specified attributes.

    file: A dictionary with keys:
        base: The base directory for the file.
        content: The content to write into the file.
        group: The group ownership for the file.
        mode: The file permissions mode.
        name: The name of the file.
        owner: The owner of the file.

    Returns:
        None because we are only interested in side effects.

    Raises:
        SystemExit: If any subprocess call fails or file operations fail.
    """
    base = file['base']
    content = file['content']
    group = file['group']
    mode = file['mode']
    name = file['name']
    owner = file['owner']
    fn = base + name
    print(f'Deploying {fn}...')
    try:
        subprocess.run(f'{MKDIR_P_M}{mode} {base}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error creating directory {base}: {e}')
        sys.exit(e.returncode)
    with open(fn, 'w', encoding='utf-8') as to_file:
        try:
            to_file.write(content)
        except Exception as w_exc:
            print(f'Error writing file {fn}: {w_exc}')
            sys.exit(-2) # TODO: Maybe improve this block (from 'with', 5 lines above).
    try:
        subprocess.run(f'{CHOWN}{owner} {fn}', shell=True, check=True)
        subprocess.run(f'{CHGRP}{group} {fn}', shell=True, check=True)
        subprocess.run(f'{CHMOD}{mode} {fn}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error setting ownership or permissions for {fn}')
        sys.exit(e.returncode)
    print(f'File {fn} deployed successfully.')

def converge(data):
    def do_service(service):

        def do_package(package):
            """
            Handle package installation/reinstallation and associated files.
            
            :param package: The name of the package to install/reinstall.
            :return: None
            """
            print(f'Reinstalling {package} ...')
            try:
                subprocess.run(f'{DPKG_INSTALL}{package}', shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f'Error reinstalling package {package}: {e}')
                sys.exit(e.returncode)
            print(f'Package {package} installed successfully.')
            if 'Packages' in data and \
                    package in data['Packages'] and \
                    'files' in data['Packages'][package]:
                for f in data['Packages'][package]['files']:
                    if f in data['Files']:
                        do_file(data['Files'][f])
                    else:
                        print(f"\n\nWARNING: File '{f}' required by package"
                              f" '{package}' was not found amongst Files:.\n\n")
        print(f"Cycling service '{service}'.")
        try:
            subprocess.run(f'{SERVICE}{service}{STOP}', shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error stopping service '{service}': {e}")
            sys.exit(e.returncode)
        for p in data['Services'][service]['packages']:
            do_package(p)
        try:
            subprocess.run(f'{SERVICE}{service}{START}', shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error starting service '{service}': {e}")
            sys.exit(e.returncode)
        print(f"Service '{service}' is up & running now.")
    if 'Services' in data:
        for s in data['Services']:
            do_service(s)
    if 'Evictions' in data:
        print('Removing final packages...')
        try:
            subprocess.run(f"{DPKG_AUTOPURGE}{' '.join(data['Evictions'])}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error removing packages: {e}')
            sys.exit(e.returncode)
        print('Packages removed successfully.')


if '__main__' == __name__:
    input_file = DEFAULT_CONF
    if 2 == len(sys.argv):
        input_file = sys.argv[1]
    elif 2 < len(sys.argv):
        print('\nUsage:\n\n' + sys.argv[0] +
              ' [ configuration_file ]  # ' + DEFAULT_CONF +
              ' if configuration_file is omitted.\n\n', sys.stderr)
        sys.exit(-1)
    with open(input_file, 'r', encoding='utf-8') as stream:
        try:
            yaml_data = yaml.safe_load(stream)
        except yaml.YAMLError as r_exc:
            print(r_exc)
            sys.exit(-2)
    converge(yaml_data)
