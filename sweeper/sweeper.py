import os

import yaml

from typing import List, Any
from itertools import product

from .utils import get_time_stamp, create_latest_symlink


class Run:
    """
    A single run of experiment.
    """
    def __init__(
        self,
        cmd: str,
        output_path: str | None = None,
        key: Any = None,
    ):
        """
        Args:
            cmd: The python command to execute.
            output_path: The path to dump the output.
            key: The key to sort the runs.
        """
        self.cmd = cmd
        self.output_path = output_path
        self.key = key if key is not None else cmd


class Script:
    """
    A script to run a list of runs.
    """
    def __init__(self, prologue: str, epilogue: str, lst_runs: List[Run]):
        self.prologue = prologue
        self.epilogue = epilogue
        self.lst_runs = lst_runs

    def to_str(self):
        return (
            self.prologue +
            "\n\n" +
            "\n\n".join(
                [
                    "echo {cmd}\n{cmd}".format(cmd=run.cmd) for run in self.lst_runs
                ]
            ) +
            "\n\n" +
            self.epilogue +
            "\n"
        )

    def write(self, path):
        with open(path, "w") as f:
            f.write(self.to_str())


class ConfigFileParser:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as fp:
            self.config = yaml.safe_load(fp)

    def dump(self, path: str):
        """
        Dump the entire configuration.

        Args:
            path: The path to dump configuration.
        """
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    @property
    def prologue(self):
        return self.config['prologue'] if "prologue" in self.config else ""

    @property
    def epilogue(self):
        return self.config['epilogue'] if "epilogue" in self.config else ""

    @property
    def root(self):
        return self.config['root'] if "root" in self.config else None

    @property
    def lst_args_dicts(self):
        """
        Construct the list of argument dictionaries by cartesian product.
        """
        def dfs(node, prefix=""):
            """
            Returns:
                A list of dictionaries.
            """
            if isinstance(node, int) or isinstance(node, float) or isinstance(node, str):
                return [{prefix: node}]

            elif isinstance(node, list):
                return [entry for child in node for entry in dfs(child, prefix)]

            elif isinstance(node, dict):
                cartesian_product = product(*[dfs(value, prefix + "." + key if prefix != "" else key) for key, value in node.items()])
                return [{key: value for d in l for key, value in d.items()} for l in cartesian_product]

        return dfs(self.config, "")


class ScriptGenerator:
    def __init__(
        self,
        root: str,
        config_path: str,
        num_scripts: int = 0,
    ):
        """
        Args:
            root: The root folder to dump everything.
            config_path: The path to the configuration file.
            prologue: The prologue to add to each script.
            epilogue: The epilogue to add to each script.
            num_scripts: The number of scripts to generate. If <= 0, it will generate one script for each run.
        """
        self.root = root
        self.parser = ConfigFileParser(config_path)
        self.num_scripts = num_scripts

        self.time_stamp = get_time_stamp()

    @property
    def root_folder(self):
        """The root folder to dump everything."""
        return os.path.join(self.root, self.time_stamp)

    @property
    def scripts_folder(self):
        """The folder to dump all scripts."""
        return os.path.join(self.root_folder, "scripts")

    @property
    def outputs_folder(self):
        """The folder to dump all runs."""
        return os.path.join(self.root_folder, "outputs")

    def write(self, make_symlink: bool = True):
        lst_runs = self.make_lst_runs(self.parser.lst_args_dicts)
        lst_runs.sort(key=lambda run: run.key)

        lst_scripts = self.make_scripts(lst_runs)

        os.mkdir(self.root_folder)
        self.parser.dump(os.path.join(self.root_folder, "config.yaml"))

        os.mkdir(self.scripts_folder)
        for i, script in enumerate(lst_scripts):
            script.write(os.path.join(self.scripts_folder,  "{:d}.sh".format(i)))

        os.mkdir(self.outputs_folder)
        for run in lst_runs:
            if run.output_path is not None:
                os.makedirs(os.path.join(self.outputs_folder, run.output_path))

        # TODO: Handle the symlink robustly, e.g., when the latest folder is deleted.
        if make_symlink:
            create_latest_symlink(self.root_folder)

    def make_lst_runs(self, lst_args_dicts: List[dict]) -> List[Run]:
        """
        Args:
            lst_args_dicts: A list of argument dictionaries.

        Returns:
            A list of Run objects.
        """
        raise NotImplementedError

    def make_scripts(self, lst_runs: List[Run]) -> List[Script]:
        num_scripts = self.num_scripts if self.num_scripts > 0 else len(lst_runs)

        return [
            Script(
                self.prologue,
                self.epilogue,
                [run for j, run in enumerate(lst_runs) if j % num_scripts == i],
            ) for i in range(num_scripts)
        ]
