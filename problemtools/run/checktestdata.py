"""This module handles execution of scripts in the Checktestdata input
verification language (https://github.com/DOMjudge/checktestdata)
"""

import os
import json
from .executable import Executable
from .errors import ProgramError
from .tools import get_tool_path

class Checktestdata(Executable):
    """Wrapper class for running Checktestdata scripts.
    """
    _CTD_PATH = get_tool_path('checktestdata')

    def __init__(self, path):
        """Create a Checktestdata wrapper.

        Args:
            path (str): path to .ctd source file
        """
        if Checktestdata._CTD_PATH is None:
            raise ProgramError(
                'Could not locate the Checktestdata program to run %s' % path)

        # if contraints file exists
        constraintFile = os.path.dirname(path) + "/../problem_statement/constraints.json"
        if os.path.exists(constraintFile):
            constraints = json.loads(open(constraintFile).read())
            
            # prepend file with constraints
            tmpFile = '/tmp/ctd.tmp'
            with open(tmpFile, "w") as outf:
                outf.write(self.constraintString(constraints))
                with open(path, "r") as inf:
                    content = inf.read()
                outf.write(content)
            path = tmpFile

        super(Checktestdata, self).__init__(Checktestdata._CTD_PATH,
                                            args=[path])


    def __str__(self):
        """String representation"""
        return '%s' % (self.args[0])

    def constraintString(self, dictionary):
        """Converts a dictionary with key-value pairs into a string
            that can be prepended to the actual program and sets some constaints
        """
        r = ""
        for k, v in dictionary.iteritems():
            r += "SET(%s = %s)\n" % (str(k), str(v))
        return r

    _compile_result = None
    def compile(self):
        """Syntax-check the Checktestdata script

        Returns:
            False if the Checktestdata script has syntax errors and
            True otherwise
        """
        if self._compile_result is None:
            (status, _) = super(Checktestdata, self).run()
            self._compile_result = (os.WIFEXITED(status) and
                                    os.WEXITSTATUS(status) in [0, 1])
        return self._compile_result


    def run(self, infile='/dev/null', outfile='/dev/null',
            errfile='/dev/null', args=None, timelim=1000):
        """Run the Checktestdata script to validate an input file.

        Args:
            infile (str): name of input file to validate
            outfile (str): file name to save stdout of Checktestdata in
            errfile (str): file name to save stderr of Checktestdata in
            args (list of str): additional command-line arguments to
                pass to Checktestdata
            timelim (int): time limit for the Checktestdata process in
                seconds

        Returns:
            tuple (status, runtime):
                status (int): exit status of the validator.
                    WEXITSTATUS(status) will be 42 if and only if
                    Checktestdata accepted the input file.
                runtime (float): runtime of the Checktestdata process
                    in seconds
        """
        (status, runtime) = super(Checktestdata, self).run(infile=infile,
                                                           outfile=outfile,
                                                           errfile=errfile,
                                                           args=args,
                                                           timelim=timelim)
        # This is ugly, switches the accept exit status and our accept
        # exit status 42.
        if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
            return (42<<8, runtime)
        if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 42:
            return (0, runtime)
        return (status, runtime)
