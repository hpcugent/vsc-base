# VSC-tools

Common tools used within our organization.

Originally created by the HPC team of the University of Ghent (http://ugent.be/hpc)
and the VSC (Flemish Supercomputer Centre - https://vscentrum.be/nl/en).

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

## bin
A collection of python scripts :
- __logdaemon.py__: A daemon that listens on a port for udp packets and logs them to file, works toghether with fancylogger.
- __startlogdaemon.py__ : Script that will start the logdaemon for  you and set environment variables for fancylogger.