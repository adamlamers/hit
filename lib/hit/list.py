import os

import click
from hit.utils import find_yaml_files

@click.command(name="list", help="List available files to execute")
def list_requests():
    
    valid_files = find_yaml_files(os.getcwd(), recursive=True, exclude_config=True)
    for file in sorted(valid_files):
        click.echo(os.path.relpath(file))
