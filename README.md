# VSC-tools

Common tools used within our organization.

Originally created by the HPC team of Ghent University (http://ugent.be/hpc).


# Namespaces and tools

## vsc
Common namespace used by all our python modules

- __fancylogger__: an extention of the default python logger designed to be easy to use and have a
couple of `fancy` features.
 - custom specifiers for mpi loggin (the mpirank) with autodetection of mpi
 - custom specifier for always showing the calling function's name
 - rotating file handler
 - a default formatter.
 - logging to an UDP server (logdaemon.py f.ex.)
 - easily setting loglevel

### ldap Collection of utilities to ease interaction with the LDAP servers.
Examples of the schema's used can be provided, although we do not include them
ny default.
- __filter.py__: Construction of LDAP filters that can be combined in intuitive
  ways using well-known operators, such as __and__, __or__, and __not__.
- __group.py__: A group in LDAP, based on the posixGroup object class --
  extended with several fields. Has one or more members and at least one
  moderator.
- __project.py__: Projects that are run on the HPC infrastructure. These are
  autogroups, meaning their member list is built automagically.
- __user__.py: A user in LDAP.
- __utils.py__: Low-level LDAP utilities, such as making (and maintaining) a
  bind the the LDAP server. Higher level utilities for querying LDAP and the
  base class for entitites in LDAP.
- __vo.py__: A virtual organisation is a special kind of group.

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

