import yaml
from typing import Dict, Any
import os
from pathlib import Path

class Config():
    """
    A configuration reader class for loading and accessing YAML configuration files.
    This class provides functionality to load YAML files, validate their structure,
    and access configuration values using dictionary-like syntax with support for
    nested key access.
    Attributes:
        _data_dict (Dict[Any, Any]): Internal dictionary storing the loaded YAML configuration data.
    """

    def __init__(self, filepath: str):
        self._data_dict = self._load_file(filepath)

    def _load_file(self, filepath: str) -> Dict:
        """
        Load the configuration file and return the dictionary from the YAML file.
        
        
        :param self: Config Object
        :param filepath: Filepath to the yaml file.
        :return: Dictionary containing the YAML file contents.
        :rtype: Dict[Any, Any]
        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
            ValueError: If the YAML file is invalid or does not contain a dictionary at the root level.
        """
        if not os.path.isfile(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'r') as file:
                data = yaml.safe_load(file)
                if not isinstance(data, dict):
                    raise ValueError("YAML content is not a dictionary.")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")

    def get_data(self) -> Dict:
        return self._data_dict

    def __getitem__(self, *keys) -> Any:
        """
        Retrieves a value from a nested dictionary using a list of keys.
        Returns None if any key in the path is missing.
        """
        d = self._data_dict
        for key in keys:
            if isinstance(d, dict) and key in d:
                d = d[key]
            else:
                print('(ConfigReader) Missing key: {0}'.format(key)) # type: ignore
                return None
        return d

    def __str__(self) -> str:
        return self._format_recursively(self._data_dict)

    def _format_recursively(self, dictionary, level=0):
        """
        Helper Function for printing out the yaml file.
        """   
        indent = "\t" * level
        lines = []
        for key, value in dictionary.items():
            if isinstance(value, dict):
                lines.append(f"{indent}{key}:")
                lines.append(self._format_recursively(value, level + 1))
            else:
                lines.append(f"{indent}{key}: {value}")
        return "\n".join(lines)

CONFIG_SETUP = Config(str(Path('configs')/'Setup.yaml'))