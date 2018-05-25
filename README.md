# vsc-base

### Build Status

- Python 2.6 : [![Build Status](https://jenkins1.ugent.be/job/vsc-base-python26/badge/icon)](https://jenkins1.ugent.be/job/vsc-base-python26/)
- Python 2.7 : [![Build Status](https://jenkins1.ugent.be/job/vsc-base-python27/badge/icon)](https://jenkins1.ugent.be/job/vsc-base-python27/)

# Description

Common tools used within our organization.
Originally created by the HPC team of Ghent University (http://ugent.be/hpc).

# Documentation
https://jenkins1.ugent.be/job/vsc-base-python26/Documentation/

# Namespaces and tools

## lib/utils
python utilities to be used as libraries

- __fancylogger__: an extention of the default python logger designed to be easy to use and have a couple of `fancy` features.

 - custom specifiers for mpi loggin (the mpirank) with autodetection of mpi
 - custom specifier for always showing the calling function's name
 - rotating file handler
 - a default formatter.
 - logging to an UDP server (logdaemon.py f.ex.)
 - easily setting loglevel

- __daemon.py__ : Daemon class written by Sander Marechal (http://www.jejik.com) to start a python script as a daemon.
- __missing.py__: Small functions and tools that are commonly used but not available in the Python (2.x) API.
- ~~__cache.py__ : File cache to store pickled data identified by a key accompanied by a timestamp.~~ (moved to [vsc-utils](https://github.com/hpcugent/vsc-utils))
- __generaloption.py__ : A general option parser for python. It will fetch options (in this order) from config files, from environment variables and from the command line and parse them in a way compatible with the default python optionparser. Thus allowing a very flexible way to configure your scripts. It also adds a few other useful extras.
- __affinity.py__ : Linux cpu affinity.

 - Based on `sched.h` and `bits/sched.h`,
 - see man pages for `sched_getaffinity` and `sched_setaffinity`
 - also provides a `cpuset` class to convert between human readable cpusets and the bit version Linux priority
 - Based on sys/resources.h and bits/resources.h see man pages for `getpriority` and `setpriority`

- __asyncprocess.py__ : Module to allow Asynchronous subprocess use on Windows and Posix platforms

 - Based on a [python recipe](http://code.activestate.com/recipes/440554/) by Josiah Carlson
 - added STDOUT handle and recv_some

- __daemon.py__ : [A generic daemon class by Sander Marechal](http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)
- __dateandtime.py__ : A module with various convenience functions and classes to deal with date, time and timezone.
- __nagios.py__ : This module provides functionality to cache and report results of script executions that can readily be interpreted by nagios/icinga.
- __run.py__ : Python module to execute a command, can make use of asyncprocess, answer questions based on a dictionary

 - supports a whole lot of ways to input, process and output the command. (filehandles, PIPE, pty, stdout, logging...)

- __mail.py__ : Wrapper around the standard Python mail library.

 - Send a plain text message
 - Send an HTML message, with a plain text alternative

## bin
A collection of python scripts, these are examples of how you could use fancylogger to log to a daemon, but should not be used directly.
- __logdaemon.py__: A daemon that listens on a port for udp packets and logs them to file, works toghether with fancylogger.
- __startlogdaemon.py__ : Script that will start the logdaemon for  you and set environment variables for fancylogger.

# License
vsc-base is made available under the GNU Library General Public License (LGPL) version 2 or any later version.

# Acknowledgements
vsc-base was created with support of [Ghent University](http://www.ugent.be/en),
the [Flemish Supercomputer Centre (VSC)](https://vscentrum.be/nl/en),
the [Flemish Research Foundation (FWO)](http://www.fwo.be/en),
and [the Department of Economy, Science and Innovation (EWI)](http://www.ewi-vlaanderen.be/en).

