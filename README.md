# VSC-tools

Common tools used within our organization.

Originally created by the HPC team of Ghent University (http://ugent.be/hpc)

## vsc
Common namespace used by all our python modules

- __fancylogger__: an extention of the default python logger designed to be easy to use and have a
cople of `fancy` features.
 - custom specifiers for mpi loggin (the mpirank) with autodetection of mpi
 - custom specifier for always showing the calling function's name
 - rotating file handler
 - a default formatter.
 - logging to an UDP server (logdaemon.py f.ex.)
 - easily setting loglevel

### utils
Collection of utilities:
- __daemon.py__ : Daemon class written by Sander Marechal (http://www.jejik.com) to start a python script as a daemon.
- __missing.py__: Small functions and tools that are commonly used but not
  available in the Python (2.x) API.
- __cache.py__ : File cache to store pickled data identified by a key accompanied by a timestamp,

## bin
A collection of python scripts :
- __logdaemon.py__: A daemon that listens on a port for udp packets and logs them to file, works toghether with fancylogger.
- __startlogdaemon.py__ : Script that will start the logdaemon for  you and set environment variables for fancylogger.

# License
VSC-tools is made available under the GNU General Public License (GPL) version 2.

# Acknowledgements
VSC-tools was created with support of [Ghent University](http://www.ugent.be/en),
the [Flemish Supercomputer Centre (VSC)](https://vscentrum.be/nl/en),
the [Hercules foundation and the Department of Economy](http://www.herculesstichting.be/in_English),
and [the Department of Economy, Science and Innovation (EWI)](http://www.ewi-vlaanderen.be/en).

