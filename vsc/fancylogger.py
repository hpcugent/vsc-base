##
# Copyright 2011-2012 Jens Timmerman
#
# This file is part of VSC-tools,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
# 
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##
"""
Created on Oct 14, 2011

@author: Jens Timmerman
This module implements a fancy logger on top of python logging

It adds:
- custom specifiers for mpi loggin (the mpirank) with autodetection of mpi
- custom specifier for always showing the calling function's name
- rotating file handler
- a default formatter.
- logging to an UDP server (logdaemon.py f.ex.)
- easily setting loglevel


usage:
>>> import fancylogger
>>> # will log to screen by default
>>> fancylogger.logToFile('dir/filename') 
>>> fancylogger.setLogLevelDebug() #set global loglevel to debug
>>> logger = fancylogger.getLogger(name) #get a logger with a specific name
>>> logger.setLevel(level) #set local debugging level

# if you want the logger to be showing modulename.functionname as the name, use
# creating a logger like this will use the name of the function calling the getLogger function,
# to be the loggers name.
>>> fancylogger.getLogger(fname=True)

# you can still use the handler to set a different formatter by using
>>> handler = fancylogger.logToFile('dir/filename')
>>> formatstring = '%(asctime)-15s %(levelname)-10s %(mpirank)-5s %(funcname)-15s %(threadname)-10s %(message)s'
>>> handler.setFormatter(logging.Formatter(formatstring))

#setting a global loglevel will impact all logers:
>>> from vsc import fancylogger
>>> logger = fancylogger.getLogger("test")
>>> logger.warning("warning")
2012-01-05 14:03:18,238 WARNING    <stdin>.test    MainThread  warning
>>> logger.debug("warning")
>>> fancylogger.setLogLevelDebug()
>>> logger.debug("warning")
2012-01-05 14:03:46,222 DEBUG      <stdin>.test    MainThread  warning

## logging to a udp server:
# set an environment variable FANCYLOG_SERVER and FANCYLOG_SERVER_PORT (optionally)
# this will make fancylogger log to that that server and port instead of the screen.
"""
from logging import Logger
import inspect
import logging.handlers
import threading
import os

# constants  
# TODO: let these be set by environment variables
LOGGER_NAME = "fancylogger"
DEFAULT_LOGGING_FORMAT = '%(asctime)-15s %(levelname)-10s %(name)-15s %(threadname)-10s  %(message)s'
MAX_BYTES = 100 * 1024 * 1024 #max bytes in a file with rotating file handler
BACKUPCOUNT = 10 #number of rotating log files to save

DEFAULT_UDP_PORT = 5005

## mpi rank support
try:
    from mpi4py import MPI
    _MPIRANK = str(MPI.COMM_WORLD.Get_rank())
    if MPI.COMM_WORLD.Get_size() > 1:
        # enable mpi rank when mpi is used
        DEFAULT_LOGGING_FORMAT = '%(asctime)-15s %(levelname)-10s %(name)-15s' \
                                " mpi: %(mpirank)s %(threadname)-10s  %(message)s"
except ImportError:
    _MPIRANK = "N/A"


class FancyLogRecord(logging.LogRecord):
    """
    This class defines a custom log record
    Adding extra specifiers is as simple as adding attributes to the log record
    """
    def __init__(self, *args, **kwargs):
        logging.LogRecord.__init__(self, *args, **kwargs)
        ## modify custom specifiers here
        # actually threadName already exists, this is just a demo
        self.threadname = thread_name()
        # remove LOGGER_NAME prefix from view
        self.name = self.name.replace(LOGGER_NAME + ".", "", 1)
        self.mpirank = _MPIRANK

# Custom logger that uses our log record
class NamedLogger(logging.getLoggerClass()):
    """
    This is a custom Logger class that uses the FancyLogRecord
    and has an extra method raiseException
    """
    _thread_aware = True #this attribute can be checked to know if the logger is thread aware

    def __init__(self, name):
        """
        constructor
        This function is typically called before any
        loggers are instantiated by applications which need to use custom
        logger behavior.
        """
        Logger.__init__(self, name)
        self.logtoscreen = False
        self.logtofile = False
        self.logtoudp = False

    #method definition as it is in logging, can't change this
    def makeRecord(self, name, level, pathname, lineno, msg, args, excinfo, func=None, extra=None):
        """
        overwrite make record to use a fancy record (with more options)
        """
        return FancyLogRecord(name, level, pathname, lineno, msg, args, excinfo)

    def raiseException(self, message, exception=Exception):
        """
        logs an exception (as warning, since it can be caught higher up and handled)
        and raises it afterwards
        """
        self.warning(message)
        raise exception(message)

def thread_name():
    """
    returns the current threads name
    """
    return threading.currentThread().getName()


def getLogger(name=None, fname=False):
    """
    returns a fancylogger
    if fname is True, the loggers name will be 'modulename.functionname'
    where functionname is the name of the function calling this function
    """
    fullname = getRootLoggerName()
    if name:
        fullname = ".".join([fullname, name])
    if fname:
        fullname = ".".join([fullname, _getCallingFunctionName()])

    #print "creating logger for %s"%fullname
    return logging.getLogger(fullname)

def getRootLoggerName():
    """
    returns the name for the root logger for the particular instance
    """
    ret = _getRootModuleName()
    if ret:
        return "%s.%s" % (LOGGER_NAME, ret)
    else:
        return LOGGER_NAME

def _getCallingFunctionName():
    """
    returns the name of the function calling the function calling this function
    (for internal use only)
    """
    try:
        return inspect.stack()[2][3]
    except Exception:
        return None

def _getRootModuleName():
    """
    returns the name of the root module
    this is the module that is actually running everything and so doing the logging
    """
    try:
        return inspect.stack()[-1][1].split('/')[-1].split('.')[0]
    except Exception:
        return None


def logToScreen(boolean=True, handler=None, name=None):
    """
    enable (or disable) logging to screen
    returns the screenhandler (this can be used to later disable logging to screen)
    
    if you want to disable logging to screen, pass the earlier obtained screenhandler
    
    you can also pass the name of the logger for which to log to the screen
    otherwise you'll get all logs on the screen 
    """
    logger = getLogger(name)
    if boolean and not logger.logtoscreen:
        if not handler:
            formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.logtoscreen = True
    elif not boolean:
        if handler:
            logger.removeHandler(handler)
        else:
            #removing the standard stdout logger doesn't work
            #it will be re-added if only one handler is present
            lhStdout = logger.handlers[0]  # stdout is the first handler
            lhStdout.setLevel(101)#50 is critical, so 101 should be nothing
        logger.logtoscreen = False
    return handler

def logToFile(filename, boolean=True, filehandler=None, name=None):
    """
    enable (or disable) logging to file
    given filename
    will log to a file with the given name using a rotatingfilehandler
    this will let the file grow to MAX_BYTES and then rotate it
    saving the last BACKUPCOUNT files. 
    
    returns the filehandler (this can be used to later disable logging to file)
    
    if you want to disable logging to file, pass the earlier obtained filehandler 
    """
    logger = getLogger(name)
    if boolean and not logger.logtofile:
        if not filehandler:
            formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
            filehandler = logging.handlers.RotatingFileHandler(
                                    filename, 'a',
                                    maxBytes=MAX_BYTES,
                                    backupCount=BACKUPCOUNT)
            filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
        logger.logtofile = True
    elif not boolean: #stop logging to file (needs the handler, so fail if it's not specified)
        logger.removeHandler(filehandler)
        logger.logtofile = False
    return filehandler


def logToUDP(hostname, port=5005, boolean=True, datagramhandler=None, name=None):
    """
    enable (or disable) logging to udp
    given hostname and port.
    
    returns the filehandler (this can be used to later disable logging to udp)
    
    if you want to disable logging to udp, pass the earlier obtained filehandler,
    and set boolean = False 
    """
    logger = getLogger(name)
    if boolean and not logger.logtoudp:
        if not datagramhandler:
            formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
            datagramhandler = logging.handlers.DatagramHandler(hostname, port)
            datagramhandler.setFormatter(formatter)
        logger.addHandler(datagramhandler)
        logger.logtoudp = True
    elif not boolean: #stop logging to file (needs the handler, so fail if it's not specified)
        logger.removeHandler(datagramhandler)
        logger.logtoudp = False
    return datagramhandler


def setLogLevel(level):
    """
    set a global log level (for this root logger)
    """
    getLogger().setLevel(level)

def setLogLevelDebug():
    """
    shorthand for setting debug level
    """
    setLogLevel(logging.DEBUG)

def setLogLevelInfo():
    """
    shorthand for setting loglevel to Info
    """
    setLogLevel(logging.INFO)

def setLogLevelWarning():
    """
    shorthand for setting loglevel to Info
    """
    setLogLevel(logging.WARNING)


# Register our logger
logging.setLoggerClass(NamedLogger)

# log to a server if FANCYLOG_SERVER is set.
if 'FANCYLOG_SERVER' in os.environ:
    server = os.environ['FANCYLOG_SERVER']
    port = DEFAULT_UDP_PORT
    if ':' in server:
        server, port = server.split(':')

    # maybe the port was specified in the FANCYLOG_SERVER_PORT env var. this takes precedence
    if 'FANCYLOG_SERVER_PORT' in os.environ:
        port = int(os.environ['FANCYLOG_SERVER_PORT'])
    port = int(port)

    logToUDP(server, port)
else:
    # log to screen by default
    logToScreen(boolean=True)
