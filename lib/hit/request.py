import os
import json

import requests
from hit._yaml import yaml, Loader
from hit.config import (
    HitConfig,
    RequestConfig,
    ExpectConfig,
)

class Request(requests.Request):

    def __init__(self, file=None, options=None, environment=None):
        super().__init__(self)

        self.context = dict(os.environ)
        self.options = options or HitConfig()
        self.response = None
        self.request_config = RequestConfig()
        self.environment = environment
        self.expect_config = ExpectConfig()
        if file is not None:
            self.file = os.path.abspath(file)
            self.load(self.file)

    def update_context(self, context_dict):
        self.context.update(context_dict)

    def load(self, file):
        self.file = os.path.abspath(file)

        with open(self.file, "r") as f:
            config = yaml.load(f, Loader=Loader)

            self.options.load_dict(
                config.get("config", {}),
                context=self.context,
                file_dir=os.path.dirname(self.file),
            )
            self.update_context(self.options.variables)

            if self.options.auth:
                self.options.prepare_auth()

            if self.environment:
                print(f"Environment {self.environment}")
                print(self.options.environments)
                env_contexts = self.options.environments.get(self.environment, {})
                print(env_contexts)
                self.update_context(env_contexts)

            self.request_config.load_dict(
                config.get("request", {}),
                context=self.context,
                file_dir=os.path.dirname(self.file),
            )

            self.expect_config.load_dict(
                config.get("expect", {})
            )

            self.method = self._format_with_context(self.request_config.method)
            self.url = self._format_with_context(self.request_config.url)
            self.params = self._format_with_context(self.request_config.query_params)
            self.headers = self._format_with_context(self.request_config.headers)
            self.cookies = self._format_with_context(self.request_config.cookies)
            self.data = self.request_config.body

    def _format_with_context(self, format_obj):
        if isinstance(format_obj, str):
            return format_obj.format(**self.context)

        if isinstance(format_obj, list):
            formatted_obj = []
            for item in format_obj:
                if isinstance(item, str):
                   formatted_obj.append(item.format(**self.context))
            return formatted_obj

        if isinstance(format_obj, dict):
            formatted_obj = {}
            for k, v in format_obj.items():
                if isinstance(v, str):
                    formatted_obj[k] = v.format(**self.context)
                else:
                    formatted_obj[k] = self._format_with_context(v)
            return formatted_obj

    def send(self, session=None):
        if not session:
            session = requests.Session()

        if self.options.auth_obj:
            self.auth = self.options.auth_obj

        self.response = session.send(self.prepare())
        self.expect_config.check(self.response)
        return self.response

    def dump_response(self):
        prepared = self.prepare()
        repr_str = f"[{os.path.relpath(self.file)}] {prepared.method} {prepared.url} {self.response.status_code}"

        if self.options.print_request_headers or self.options.verbose:
            repr_str += "\n\nRequest headers:\n"
            for header, value in prepared.headers.items():
                repr_str += f"[{os.path.relpath(self.file)}] {header}: {value}\n"
            repr_str += "\n"

        if self.options.print_request_body or self.options.verbose:
            if prepared.body:
                repr_str += "\nRequest body:\n"
                if isinstance(prepared.body, str):
                    repr_str += prepared.body
                else:
                    repr_str += f"<{len(prepared.body)} bytes>"

        if self.options.print_response_headers or self.options.verbose:
            repr_str += "\n\nResponse headers:\n"
            for header, value in self.response.headers.items():
                repr_str += f"[{os.path.relpath(self.file)}] {header}: {value}\n"

        if self.options.print_response_body or self.options.verbose:
            content_type = self.response.headers.get("Content-Type")
            repr_str += "\nResponse body:\n"
            if content_type:
                repr_str += _get_print_handler(content_type.lower())(self.response.content.decode("UTF-8"))
            else:
                repr_str += _get_print_handler(None)(self.response.content)

        return repr_str

    def __str__(self):
        if self.response:
            return f"<hit.request.Request [{self.response.status_code}]>"
        else:
            return "<hit.request.Request [not sent]>"

    def __repr__(self):
        return self.__str__()


def _get_print_handler(content_type):

    handlers = {
        "application/json": _json_handler,
        None: _plaintext_handler,
    }

    return handlers.get(content_type, lambda _: _)


def _json_handler(data):

    clean_data = data
    if isinstance(clean_data, bytes):
        clean_data = data.decode("UTF-8")

    clean_data = json.loads(clean_data)

    return json.dumps(clean_data, indent=4)


def _plaintext_handler(data):
    return data.decode("UTF-8")
