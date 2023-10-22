import click
import jsonref

@click.command(name="import", help="import an api spec")
@click.argument('path')
@click.option("--type", "-t", "type_", type=click.Choice(["openapi"], case_sensitive=False), required=True)
def importer(path, type_):

    if type_ == "openapi":
        with open(path, "r") as f:
            doc = jsonref.load(f)

        extracted_methods = {}
        for urlpath, methods in doc.get("paths").items():
            for method, method_def in methods.items():
                extracted_methods[urlpath] = {}
                extracted_methods[urlpath]["operationId"] = method_def.get("operationId")
                extracted_methods[urlpath][method] = method_def.get("requestBody")
        print(jsonref.dumps(extracted_methods, indent=4))
