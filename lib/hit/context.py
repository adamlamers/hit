import os

class HitContext:

    def __init__(
        self,
        file_path,
        values=None,
        include_environment_variables=True,
        walk_parent_directories=True,
    ):
        self.file_path = file_path
        self.include_environment_variables = include_environment_variables
        self.walk_parent_directories = walk_parent_directories
        self.values = values or {}

        if self.include_environment_variables:
            self.values.update(dict(os.environ))

        if not os.path.isfile(file_path):
            raise ValueError("file_path must be a file")

    def render_values(self):
        pass
