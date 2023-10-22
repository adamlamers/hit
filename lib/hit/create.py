import os

import click
import json

from collections import OrderedDict
from hit.logger import logger
from hit._yaml import yaml


@click.command(help="Create a new template file")
@click.argument('path')
@click.option("--method", "-m", type=click.Choice(["GET", "POST"], case_sensitive=False), default="GET")
@click.option("--example-type", type=click.Choice(["json"], case_sensitive=False), default="json")
def create(path, method, example_type):
    directory = os.path.dirname(path)
    file_name = os.path.basename(path)

    logger.info(f"Create a new file {path} for {method} http request")

    if directory:
        os.makedirs(directory, exist_ok=True)

    if not file_name:
        logger.error("A file name is required!")
        return 1

    resolved_path = path
    if not resolved_path.endswith(".yaml"):
        resolved_path = resolved_path + ".yaml"

    with open(resolved_path, "w") as new_file:

        new_request = OrderedDict() 
        new_request["method"] = method
        new_request["url"] = "http://example.com"
        new_request["query_params"] = [
            { "referrer": "hit" },
        ]
        new_request["headers"] = [
            {"Accept": "*/*"},
            {"Accept-Encoding": "gzip, deflate"},
            {"Content-Type": "application/json"},
            {"User-Agent": "hit/0.0.1"},
        ]
        new_request["body"] = _get_example_payload(example_type)

        new_config_file = OrderedDict(
            hit_config=OrderedDict(
                auth=None,
                print_response_headers=False,
                print_response_body=False,
            ),
            request=new_request
        )
        
        yaml.dump(new_config_file, new_file, indent=2)

def _get_example_payload(which):

    example_payload = {
        "a": "bunch",
        "of": ["example", "data"]
    }

    examples = dict(
        json=_example_json
    )

    return examples.get(which)(example_payload)

def _example_json(example_payload):
    return json.dumps(example_payload, indent=4) + "\n"
