# -*- coding: utf-8 -*-
#
# Author: Paul Donchenko <pdonchen@uwaterloo.ca>
# License: GPLv3

"""
Helps to run MATLAB statements and scripts through the MATLAB executable
command line on Windows.
"""

# Currently configured for windows, but would require minor changes to adapt
# for Linux and MacOS
# https://www.mathworks.com/help/matlab/ref/matlablinux.html
# https://www.mathworks.com/help/matlab/ref/matlabmacos.html

# For a more powerful tool see the "MATLAB Engine API for Python"
# https://www.mathworks.com/help/matlab/matlab_external/get-started-with-matlab-engine-for-python.html


import subprocess
from os.path import isfile
from typing import Union, List
from collections import Iterable

# default command line options/flags that are appended to the executable
# for details see https://www.mathworks.com/help/matlab/ref/matlabwindows.html
option_defaults = dict(
    # launches command windows instead of full desktop GUI
    nodesktop=False,

    # Disable the display of figure windows in MATLAB.
    noFigureWindows=False,

    # Do not display the splash screen during startup.
    nosplash=False,

    # Set the MATLAB folder to folder, specified as a string.
    sd=False,

    # Set the MATLAB folder to the value specified by the Initial working
    # folder option in the General Preferences panel.
    useStartupFolderPref=False,

    # Copy Command Window output, including error log reports, in to filename,
    # specified as a string.
    logfile=False,

    # Enable use of the Java® debugger. The Java debugger uses the default
    # portnumber value 4444 to communicate with MATLAB
    jbd=False,

    # Limit MATLAB to a single computational thread.
    singleCompThread=False,

    # Disable use of javaclasspath.txt and javalibrarypath.txt files.
    nouserjavapath=False,

    # Force MATLAB to start with software OpenGL libraries.
    softwareopengl=False,

    # Disable auto-selection of OpenGL software.
    nosoftwareopengl=False,

    # Start MATLAB as a Component Object Model (COM) Automation server. MATLAB
    # does not display the splash screen and minimizes the window. Use for a
    # single call to MATLAB.
    automation=False,

    # Register MATLAB as a COM Automation server in the Windows registry.
    regserver=False,

    # Remove MATLAB COM server entries from the registry.
    unregserver=False,

    # Use in a script to process the results from MATLAB. Calling MATLAB with
    # this option blocks the script from continuing until the results are
    # generated
    wait=False,
)

# wraps MATLAB statement with a try-catch block to silence exceptions
try_catch_wrapper = \
    "try, {}, catch err, fprintf('%s %s', err.identifier, err.message), end"
# appends to MATLAB block an exit statement to automatically close the
# window after running
exit_wrapper = "{}, exit"


class MatlabRunner:
    """
    Runs statements using a given MATLAB executable path with specified options.
    """

    def __init__(self, exe_path: str, **options: Union[bool, str, int, float]):
        """
        :param exe_path: path to `matlab.exe` executable
        :param options: command line flags with values (string or number)
            see https://www.mathworks.com/help/matlab/ref/matlabwindows.html
        """
        self._exe_path = exe_path
        self._options = {}
        self.set_options(**options)

    @staticmethod
    def _build_options_parameter(
            k: str, v: Union[int, str, bool]
    ) -> Union[str, None]:
        """
        Builds a command-line ready string flag from an option key-value pair
        """
        if k not in option_defaults:
            raise ValueError(
                f"Key {k} is not a valid matlab.exe flag."
                f"Valid flags are {tuple(option_defaults.keys())}"
            )

        if v is True:
            return f"-{k}"
        elif v is False:
            return None
        elif isinstance(v, str):
            return f'-{k} "{v}"'
        elif isinstance(v, (int, float)):
            return f'-{k} {v}'
        else:
            raise ValueError(f"Value for Key {k} is not a number or a string")

    def _build_options_string(self) -> str:
        """
        Builds the flags components of the command line string using the stored
        options dictionary
        """
        return " ".join(
            param for param in
            [
                self._build_options_parameter(k, v)
                for k, v in self._options.items()
            ]
            if param is not None
        )

    def _build_command_header(self) -> str:
        """
        Builds the command line header containing the executable path and the
        flags
        """
        return f"""{self._exe_path} {self._build_options_string()}"""

    def set_exe_path(self, exe_path: str):
        """
        Set the `matlab.exe` executable path for this runner
        """
        self._exe_path = exe_path

    def set_options(self, **options: Union[bool, str, int, float]) -> None:
        """
        Set the command line flags for this runner.
        For details see
            https://www.mathworks.com/help/matlab/ref/matlabwindows.html
        """
        invalid_options = set(options.keys()) - set(option_defaults.keys())
        if invalid_options:
            raise ValueError(f'Invalid options: {list(invalid_options)}')
        else:
            self._options = {
                **option_defaults,
                **self._options,
                **(options or {})
            }

    def _assert_exe_exists(self):
        if not isfile(self._exe_path):
            raise FileExistsError(
                f"MATLAB executable at {self._exe_path} does not exist"
            )

    def execute(
            self,
            statement: Union[str, List[str]],
            batch=False,
            try_catch=False,
            auto_exit=False,
            **subprocess_kwargs
    ) -> None:
        """
        Execute `statement` using the stored MATLAB executable and command line
        flags.

        :param statement: The MATLAB statement string to run.
            A list of statement strings will be joined into a single line
            using the ", " string.

            Example 1 - run a script (myscript.m) that exists the working
            directory:
                "myscript"

            Example 2 - single statement:
                "disp('Hello World')"

            Example 3 - multiple statements:
                ["myvar=123", "myscript"]

        :param batch: Use the -batch run flag instead of -r
        :param try_catch: Wrap `statement` in a try-catch block
        :param auto_exit: Append an exit command to the end of `statement`
        :param subprocess_kwargs: Keyword arguments passed to subprocess.call
        """
        self._assert_exe_exists()

        header = self._build_command_header()

        if batch:
            run_option = '-batch'
        else:
            run_option = '-r'

        if isinstance(statement, Iterable) and not isinstance(statement, str):
            statement = ", ".join(statement)

        if try_catch:
            statement = try_catch_wrapper.format(statement)

        if auto_exit:
            statement = exit_wrapper.format(statement)

        command = f'{header} {run_option} "{statement}"'

        subprocess.call(command, **subprocess_kwargs)
