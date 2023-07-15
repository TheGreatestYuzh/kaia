import pathlib
from pathlib import Path
import dotenv
import os
import sys

class _Loc:
    def __init__(self):
        self.root_folder = Path(__file__).parent.parent.parent
        if isinstance(self.root_folder, pathlib.WindowsPath):
            self.is_windows = True
        else:
            self.is_windows = False
        self.temp_folder = self.root_folder/'temp'
        self.test_folder = self.temp_folder/'tests'
        self.externals_folder = self.root_folder/'externals'
        self.data_folder = self.root_folder/'data'
        os.makedirs(self.temp_folder, exist_ok=True)
        os.makedirs(self.externals_folder, exist_ok=True)
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.test_folder, exist_ok=True)
        env_file = self.root_folder/'environment.env'
        dotenv.load_dotenv(env_file)

        self.conda_folder = Path(sys.executable).parent.parent.parent
        self.env_folder = Path(sys.executable).parent

        if self.is_windows:
            self.call_conda = f"call {self.conda_folder/'condabin/conda.bat'}"
        else:
            self.call_conda = self.conda_folder/'conda'

    def get_python_by_env(self, env):
        if self.is_windows:
            return self.conda_folder / 'envs' / env / 'python.exe'
        else:
            return self.conda_folder/env/'bin/python'

Loc = _Loc()