import sys
import logging

from . import __version__
from rpmreq import shell


def rpmreq(*cargs):
    """
    rpmreq CLI interface

    Execute rpmreq action with specified arguments and return
    shell friendly exit code.

    This is the default high level way to interact with rpmreq.

        py> rpmreq('foo', 'bar')

    is equivalent to

        $> rpmreq foo bar
    """
    return shell.run(cargs=cargs, version=__version__)


def main():
    """
    rpmreq console_scripts entry point
    """
    # setup logging to terminal
    logging.basicConfig(level=logging.DEBUG,
                        # format="%(message)s",
                        stream=sys.stdout)
    cargs = sys.argv[1:]
    sys.exit(rpmreq(*cargs))


if __name__ == '__main__':
    main()
