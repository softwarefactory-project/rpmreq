# rpmreq

`rpmreq` is a RPM requirements parser and explorer tool.

`rpmreq` is a part of
[Software Factory project](https://softwarefactory-project.io/docs/)


## STATUS

`rpmreq` is **STARTING TO COME INTO EXISTENCE**.

Use github
[Issues](https://github.com/softwarefactory-project/rpmreq/issues)
to make requests and report bugs.

Poke `jruzicka` on `#softwarefactory` or `#rdo` Freenode IRC for more
information.


## Installation


### from source

If you want to hack `rpmreq` or just have the latest code without waiting
for next release, you can use the git repo directly:

    git clone https://github.com/softwarefactory-project/rpmreq
    cd rpmreq
    python setup.py develop --user

You may set the preference over `rpmreq` RPM by correctly positioning
`~/.local/bin/rpmreq` in your `$PATH`.

Or you can use virtualenv to avoid conflicts with RPM:

    git clone https://github.com/softwarefactory-project/rpmreq
    cd rpmreq
    virtualenv --system-site-packages ~/rpmreq-venv
    source ~/rpmreq-venv/bin/activate
    python setup.py develop
    ln `which rpmreq` ~/bin/rpmreq-dev

    rpmreq-dev --version

Required python modules are listed in
[requirements.txt](requirements.txt).


### from PyPI (NOT YET)

For your convenience, `rpmreq` is **GOING TO BE** available from the Cheese Shop:

    pip install rpmreq


## Usage

**TODO**

## Bugs

Please use the
[github Issues](https://github.com/softwarefactory-project/rpmreq/issues)
to report bugs.
