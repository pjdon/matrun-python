# -*- coding: utf-8 -*-
#
# Author: Paul Donchenko <pdonchen@uwaterloo.ca>
# License: GPLv3

# matrun.py must be in the same folder, a python module or in a "sources root"
from matrun import MatlabRunner

# path to MATLAB executable
# file's existence is only checked on command execution
matlab_exe_path = "C:/Program Files/MATLAB/R2016a/bin/matlab.exe"


# create a runner object linked to the executable
runner = MatlabRunner(matlab_exe_path)

# set the command line options
# see the MatlabRunner class definition for valid flags
# for more details: https://www.mathworks.com/help/matlab/ref/matlabwindows.html
# - the nodesktop/splash flags/options will cause MATLAB to launch in a
#   small command window and hide the loading splash screen
# - `automation` flag will achieve the same result but start minimized
#   silently below existing windows
# - `sd` flag will set a starting directory/folder for the process
# - `logfile` flag will write a record of the command window to a text file
runner.set_options(
    nodesktop=True,
    nosplash=True,
    logfile="subprocess_log.txt"
)

# list of single-line MATLAB commands to perform during execution
# - each list item is a single line statement
# - .M scripts can be called with just their name, assuming they are in the
#   working directory (see the `sd` flag)
# - variables can be set before calling the script to create environment
#   parameters
#   in this case, output_folder was changed from level_b (MATLAB script default)
#   to level_c
commands = [
    "output_folder='./data/level_c'",
    "subprocess",
]

# execute the commands using the options that were previously set for this
# runner
# `auto_exit=True` argument will append a statement at the end to exit when all
# commands are finished
# `batch=True` argument will use the `-batch` flag instead of the `-r` flag to
# run the commands, which has some extra features
# for more details: https://www.mathworks.com/help/matlab/ref/matlabwindows.html
runner.execute(commands, auto_exit=True)

