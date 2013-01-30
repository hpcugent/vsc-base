# vsc-base

[![Build Status](https://jenkins1.ugent.be/job/vsc_base/badge/icon)](https://jenkins1.ugent.be/job/vsc_base/)

Common tools used within our organization.

Originally created by the HPC team of Ghent University (http://ugent.be/hpc).


# Namespaces and tools

## vsc
Common namespace used by all our python modules

### lib
python modules to be used as libraries

#### utils
Collection of utilities:

- __fancylogger__: an extention of the default python logger designed to be easy to use and have a
couple of `fancy` features.
 - custom specifiers for mpi loggin (the mpirank) with autodetection of mpi
 - custom specifier for always showing the calling function's name
 - rotating file handler
 - a default formatter.
 - logging to an UDP server (logdaemon.py f.ex.)
 - easily setting loglevel
- __daemon.py__ : Daemon class written by Sander Marechal (http://www.jejik.com) to start a python script as a daemon.
- __missing.py__: Small functions and tools that are commonly used but not
  available in the Python (2.x) API.
- __cache.py__ : File cache to store pickled data identified by a key accompanied by a timestamp,
- __generaloption.py__ : A general option parser for python. It will fetch options (in this order) from config files, from environment variables and from the command line and parse them in a way compatible with the default python optionparser. Thus allowing a very flexible way to configure your scripts.
It also adds a few other usefull extras.

## bin
A collection of python scripts, these are examples of how you could use fancylogger to log to a daemon, but should not be used directly.
- __logdaemon.py__: A daemon that listens on a port for udp packets and logs them to file, works toghether with fancylogger.
- __startlogdaemon.py__ : Script that will start the logdaemon for  you and set environment variables for fancylogger.

# License
vsc-base is made available under the GNU Library General Public License (LGPL) version 2 or any later version.

# Acknowledgements
vsc-base was created with support of [Ghent University](http://www.ugent.be/en),
the [Flemish Supercomputer Centre (VSC)](https://vscentrum.be/nl/en),
the [Hercules foundation and the Department of Economy](http://www.herculesstichting.be/in_English),
and [the Department of Economy, Science and Innovation (EWI)](http://www.ewi-vlaanderen.be/en).

