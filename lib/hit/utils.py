import os

def find_yaml_files(path, recursive=False, exclude_config=False):
    if not os.path.isdir(path):
        raise ValueError("Path must be a directory")

    found_files = []
    if recursive:
        for root, dirs, files in os.walk(path):
            for file in files:
                if exclude_config and file.endswith(".config.yaml"):
                    continue

                if file.endswith(".yaml"):
                    found_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(path):
            if file.endswith(".yaml"):
                found_files.append(os.path.join(path, file))

    return found_files

def find_parent_configs(path):
    configs = []
    p = os.path.abspath(path)
    while p != '/':
        files = os.listdir(p)
        for file in files:
            if file and file.endswith(".config.yaml"):
                configs.append(os.path.join(p, file))
        p = os.path.dirname(p)

    return reversed(configs)
