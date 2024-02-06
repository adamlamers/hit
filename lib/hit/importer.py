import click
import jsonref

@click.command(name="import", help="import an api spec")
@click.argument('path')
@click.option("--type", "-t", "type_", type=click.Choice(["openapi"], case_sensitive=False), required=True)
def importer(path, type_):

    if type_ == "openapi":
        with open(path, "r") as f:
            doc = jsonref.load(f)

        for path, methods in doc.get("paths", {}).items():
            for method, method_def in methods.items():
                print(path, method)
                request_body = method_def.get("requestBody", {}).get("content")
                for media_type in request_body:
                    request_content = request_body.get(media_type).get("schema")
                    # print(request_body)
                    generate_request_obj(request_content["properties"])

def generate_request_obj(request_content):
    print(request_content)
