import os

from hit._yaml import yaml, Loader
from requests.auth import HTTPBasicAuth, AuthBase
from hit.utils import find_parent_configs

class Specification:

    def __init__(self):
        self.config = None
        self.request = None
        self.expect = None
        self._raw_data = None
        self._file_abspath = None
        self._file_dir = None

    def load_file(self, file):
        self._file_abspath = os.path.abspath(file)
        self._file_dir = os.path.dirname(self._file_abspath)
        with open(self._file_abspath, "r") as sourcefile:
            self._raw_data = yaml.load(sourcefile, Loader=Loader)

        self.config = HitConfig()
        self.config.load_dict(
            self._raw_data.get("config", self._raw_data.get("hit_config", {})),
            context=dict(os.environ),
            file_dir=self._file_dir,
        )

        self.request = RequestConfig()
        self.request.load_dict(
            self._raw_data.get("request", {}), 
            file_dir=self._file_dir,
        )

        self.expect = ExpectConfig()
        self.expect.load_dict(
            self._raw_data.get("expect", {})
        )


class HitConfig:

    def __init__(self, **kwargs):
        self.file_dir = None
        self.auth = None
        self.auth_obj = None
        self.print_response_body = False
        self.print_response_headers = False
        self.print_request_body = False
        self.print_request_headers = False
        self.pretty_output = False
        self.verbose = False
        self.variables = {}
        self.environments = {}
        self.parents = []

    def load_yaml(self, yaml_str_or_fp, context=None):
        config = yaml.load(yaml_str_or_fp, Loader=Loader)
        self.load_dict(config, context)

    def load_file(self, file, context=None):
        self.file_dir = os.path.dirname(os.path.abspath(file))
        with open(file, "r") as f:
            self.load_yaml(f, context)

    def load_parents(self):
        if self.file_dir is None:
            return

        parent_configs = find_parent_configs(self.file_dir)
        self.parents = parent_configs
        parent_context = {}
        parent_environments = {}
        for config in parent_configs:
            c = HitConfig()
            c.load_file(config, parent_context)
            parent_context.update(c.variables)
            parent_environments.update(c.environments)

        self.variables.update(parent_context)
        self.environments.update(parent_environments)

    def load_dict(self, d, context, file_dir=None):
        self.file_dir = file_dir
        self.load_parents()

        dict_ = d
        if not dict_:
            return

        if "hit_config" in dict_:
            dict_ = dict_["hit_config"]

        if "config" in dict_:
            dict_ = dict_["config"]

        for key, value in dict_.items():
            setattr(self, key, value)

    def prepare_auth(self, variables={}):
        if self.auth:
            print(f"Authorizing with {self.auth}")

        if self.auth == "basic":
            self.auth_obj = HTTPBasicAuth(self.username, self.password)

        if self.auth == "custom":
            if not self.file_dir:
                print("file_dir must be set for custom auth")
                return

            script_globals = variables

            if not self.auth_script:
                print("auth_script must be defined for custom auth")
                return

            with open(os.path.join(self.file_dir, self.auth_script), "r") as f:
                exec(f.read(), script_globals)
                auth_class = script_globals.get("Auth")
                if issubclass(auth_class, AuthBase):
                    self.auth_obj = auth_class()


class RequestConfig:

    def __init__(self, **kwargs):
        self.method = None
        self.url = None
        self.query_params = None
        self.body = None
        self.body_src = None
        self.headers = None
        self.cookies = None
        self.form = None

    def load_dict(self, d, context={}, file_dir=None):
        self.context = context
        for key, value in d.items():
            setattr(self, key, value)

        self.query_params = self._resolve_query_params()
        self.headers = self._resolve_headers()
        self.cookies = self._resolve_cookies()

        # if body_src is defined but body is not, load the file with that path
        if not self.body and self.body_src:
            if not file_dir:
                raise ValueError("can't load body_src without file_path")

            abs_path = os.path.join(file_dir, self.body_src)
            with open(abs_path, "rb") as f:
                self.body = f.read()

    def _resolve_cookies(self):
        if self.cookies is None:
            return {}

        cookies = {}
        if isinstance(self.cookies, list):
            for cookie in self.cookies:
                for k, v in cookie.items():
                    cookies.update({
                        k.format(**self.context): v.format(**self.context)
                    })
        else:
            for k, v in cookie.items():
                cookies.update({
                    k.format(**self.context): v.format(**self.context)
                })

        return cookies

    def _resolve_headers(self):
        if self.headers is None:
            return {}

        headers = {}
        if isinstance(self.headers, list):
            for header in self.headers:
                for k,v in header.items():
                    headers.update({
                        k.format(**self.context): v.format(**self.context)
                    })
        else:
            for k,v in header.items():
                headers.update({
                    k.format(**self.context): v.format(**self.context)
                })

        return headers

    def _resolve_query_params(self):
        params = {}
        if isinstance(self.query_params, str):
            params = self.query_params

        if isinstance(self.query_params, list):
            for param in self.query_params:
                params.update(param)

        if isinstance(self.query_params, dict):
            for k, v in self.query_params.items():
                params.update({
                    k.format(**self.context): v.format(**self.context)
                })

        return params

class ExpectConfig:

    def __init__(self, **kwargs):
        self.status_code = None
        self.body = None
        self.headers = None

    def load_dict(self, d):
        for key, value in d.items():
            setattr(self, key, value)

    def check(self, response):
        if self.status_code:
            if self.status_code == response.status_code:
                print("Status code OK")
            else:
                print("Status code FAILED")

        if self.headers:
            errors = []
            for header, expected_value in self.headers.items():
                actual_value = response.headers.get(header)
                if actual_value != expected_value:
                    errors.append(f"Header {header} value {actual_value} does not equal expected value {expected_value}")
            for error in errors:
                print(error)
