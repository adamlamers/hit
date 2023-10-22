import click
import os

from hit.request import Request
from hit.utils import find_yaml_files

@click.command(help="Run a request file")
@click.argument('path')
@click.option("--recursive", "-r", type=bool, is_flag=True, default=False)
@click.option("--pretty", type=bool, is_flag=True, default=False, help="Attempt to format the response data")
@click.option("--print-response-headers", type=bool, is_flag=True, default=False, help="Print response headers")
@click.option("--print-response-body", type=bool, is_flag=True, default=False, help="Print response body")
@click.option("--environment", "-e", type=str, help="Choose an environment to load context from")
def run(path, recursive, pretty, print_response_headers, print_response_body, environment):

    found_files = []
    if recursive:
        if not os.path.isdir(path):
            print("path must be a directory when using recursive")
        found_files = find_yaml_files(path, recursive=True, exclude_config=True)
    elif not recursive and os.path.isdir(path):
        found_files = find_yaml_files(path, exclude_config=True)
    else:
        if os.path.isfile(path):
            found_files = [path]
        else:
            found_files = []

    click.echo(f"Found {len(found_files)} spec files")

    for file in found_files:
        if recursive:
            click.echo(f"Executing {os.path.relpath(file)}")

        request = Request(file, environment=environment)
        response = request.send()

        if response.status_code < 300:
            click.echo(click.style(request.dump_response(), fg='green'))
        else:
            click.echo(click.style(request.dump_response(), fg='red'))
