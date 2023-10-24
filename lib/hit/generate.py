# generate curl, python, whatever
import click
from hit.request import Request

def prepared_request_to_code(requests_obj):
    prepared_request = requests_obj.prepare()
    code = ""

    # Add the request method and URL
    code += "import requests\n\n"
    code += f"url = '{prepared_request.url}'\n"
    code += f"method = '{prepared_request.method}'\n"

    # Add request headers
    headers = prepared_request.headers
    if headers:
        code += "headers = {\n"
        for key, value in headers.items():
            code += f"    '{key}': '{value}',\n"
        code += "}\n"

    # Add request data (if any)
    data = prepared_request.body
    if not isinstance(data, str):
        data = data.decode("UTF-8")

    if data:
        data = data.encode('unicode_escape').decode('UTF-8')
        code += f"data = '{data}'\n"

    # Generate the complete request
    code += f"\nresponse = requests.{prepared_request.method.lower()}(url"
    if headers:
        code += ", headers=headers"
    if data:
        code += ", data=data"
    code += ")\n"

    return code

def requests_to_go(requests_obj):
    prepared = requests_obj.prepare()
    method = prepared.method
    url = prepared.url
    headers = prepared.headers
    data = prepared.body

    data = prepared.body
    if data and not isinstance(data, str):
        data = data.decode("UTF-8")
        data = data.encode('unicode_escape').decode('UTF-8')

    go_code = 'package main\n\n'
    go_code += 'import (\n'
    go_code += '    "fmt"\n'
    go_code += '    "net/http"\n'
    go_code += '    "io/ioutil"\n'
    go_code += ')\n\n'
    go_code += 'func main() {\n'
    go_code += f'    url := "{url}"\n'
    go_code += f'    method := "{method}"\n'
    go_code += f'    payload := []byte("{data}")\n'

    if headers:
        go_code += '    headers := map[string]string{\n'
        for key, value in headers.items():
            go_code += f'        "{key}": "{value}",\n'
        go_code += '    }\n'

    go_code += '    req, _ := http.NewRequest(method, url, bytes.NewBuffer(payload))\n'

    if headers:
        go_code += '    for key, value := range headers {\n'
        go_code += '        req.Header.Set(key, value)\n'
        go_code += '    }\n'

    go_code += '    client := &http.Client{}\n'
    go_code += '    resp, err := client.Do(req)\n'
    go_code += '    if err != nil {\n'
    go_code += '        panic(err)\n'
    go_code += '    }\n'

    go_code += '    defer resp.Body.Close()\n'
    go_code += '    body, _ := ioutil.ReadAll(resp.Body)\n'
    go_code += '    fmt.Println(string(body))\n'
    go_code += '}\n'

    return go_code

def requests_to_fetch(requests_obj):
    prepared = requests_obj.prepare()
    # Start building the fetch code
    fetch_code = "fetch('" + prepared.url + "', {\n"

    # Add method
    fetch_code += f"  method: '{prepared.method}',\n"

    # Add headers
    headers = prepared.headers
    if headers:
        fetch_code += "  headers: {\n"
        for key, value in headers.items():
            fetch_code += f"    '{key}': '{value}',\n"
        fetch_code += "  },\n"

    # Add data (if any)
    data = prepared.body
    if not isinstance(data, str):
        data = data.decode("UTF-8")
    if data:
        data = data.encode('unicode_escape').decode('UTF-8')
        fetch_code += f"  body: \'{data}\'\n"

    # Add options like credentials, mode, etc.
    fetch_code += "  // Add more options here if needed\n"
    fetch_code += "})\n"
    fetch_code += ".then(response => {\n"
    fetch_code += "  if (!response.ok) {\n"
    fetch_code += "    throw new Error('Network response was not ok');\n"
    fetch_code += "  }\n"
    fetch_code += "  return response.text();\n"
    fetch_code += "})\n"
    fetch_code += ".then(data => {\n"
    fetch_code += "  // Handle the response data here\n"
    fetch_code += "  console.log(data);\n"
    fetch_code += "})\n"
    fetch_code += ".catch(error => {\n"
    fetch_code += "  // Handle errors here\n"
    fetch_code += "  console.error(error);\n"
    fetch_code += "});"

    return fetch_code

@click.command()
@click.argument('path')
@click.option("--type", "-t", "_type", type=click.Choice(["curl", "fetch", "go", "requests"], case_sensitive=False), default="curl")
@click.option("--environment", "-e", type=str, help="Choose an environment to load context from")
def generate(path, _type, environment):
    r = Request(path, environment=environment)
    if _type == "curl":
        click.echo(r.to_curl())
    elif _type == "fetch":
        click.echo(requests_to_fetch(r))
    elif _type == "go":
        click.echo(requests_to_go(r))
    elif _type == "requests":
        click.echo(prepared_request_to_code(r))
    else:
        click.echo("unknown type")
