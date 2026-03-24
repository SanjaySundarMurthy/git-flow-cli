"""Schema validator for git-flow-cli config files."""
import yaml

from ..parser import validate_config


def validate_file(path: str) -> tuple[bool, list[str]]:
    """Validate a YAML config file. Returns (valid, errors)."""
    try:
        with open(path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return False, [f"File not found: {path}"]
    except PermissionError:
        return False, [f"Permission denied: {path}"]

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]

    if not data:
        return False, ["Config file is empty"]

    errors = validate_config(data)
    return len(errors) == 0, errors
