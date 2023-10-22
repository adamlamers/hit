import click
from hit.create import create
from hit.list import list_requests
from hit.run import run
from hit.importer import importer
from hit.generate import generate


@click.group()
def cli():
    pass


cli.add_command(create)
cli.add_command(list_requests)
cli.add_command(run)
cli.add_command(importer)
cli.add_command(generate)
