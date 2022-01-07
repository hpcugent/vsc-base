#!/usr/bin/env python
#
# Copyright 2011-2022 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/hpcugent/vsc-base
#
# vsc-base is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# vsc-base is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with vsc-base. If not, see <http://www.gnu.org/licenses/>.
#
"""
This is a logging server,
it will listen to all interfaces on a system assigned port
and log to ./log.log by default
with it's pidfile written to $TMPDIR/logdaemon.pid

For an example of how to use this, see startlogdaemon.sh

then use mpi to get these environment variables to the clients.

@author: Jens Timmerman (Ghent University)
"""
from __future__ import print_function
from optparse import OptionParser
from vsc.utils import fancylogger
from vsc.utils.daemon import Daemon
import logging
import os
import pickle
import socket
import sys
import traceback

class LogDaemon(Daemon):
    """
    This is the logging daemon, it get a logger and can log to a local file.
    It can start running in the background and log incoming udp packets
    to the created logger.
    """


    def __init__(self, hostname, port, log_dir, filename, pidfile):
        """Constructor"""
        stdin = '/dev/null'
        stdout = os.path.join(log_dir, 'logging_error.log')
        stderr = os.path.join(log_dir, 'logging_error.log')
        Daemon.__init__(self, pidfile, stdin, stdout, stderr)
        self.hostname = hostname
        self.port = port
        #Set up logging
        # get logger, we will log to file
        fancylogger.logToScreen(False)
        # we want to log absolutely everything that's comming at us
        fancylogger.setLogLevel(0)
        self.logfile = os.path.join(log_dir, filename)
        fancylogger.logToFile(self.logfile)
        self.logger = fancylogger.getLogger()
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        """
        overwriting start
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pidf = open(self.pidfile, 'r')
            pid = int(pidf.read().strip())
            pidf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # get socket
        self.socket_.bind((self.hostname, self.port))
        print("FANCYLOG_SERVER_PID=%s" % self.pidfile)
        print("FANCYLOG_SERVER=%s:%d" % (socket.gethostname(), self.socket_.getsockname()[-1]))
        print("FANCYLOG_SERVER_LOGFILE=%s" % self.logfile)
        sys.stdout.flush()

        # Start the daemon
        self.daemonize()
        self.run()


    def run(self):
        """
        Main server loop
        """
        while True:
            try:
                # receive the message, unpickle it, make a record from it and handle the record
                message, _ = self.socket_.recvfrom(8192)
                unpickled = pickle.loads(message[4:])
                logrecord = logging.makeLogRecord(unpickled)
                self.logger.handle(logrecord)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                traceback.print_exc()


def main(args):
    """
    Initiate the daemon
    """
    # parse options
    parser = OptionParser(usage="usage: %s start|stop|restart [options]" % args[0])
    # general options
    parser.add_option("-i", "--ip", dest="host", help="Ip to bind to [default: %default (all)]",
                       default="", type="string")
    parser.add_option("-p", "--port", help="Port to bind to [default: %default]",
                       default=0, type="int")
    parser.add_option(
                      "-l", "--log-dir", dest="logdir",
                       help="Directory to log to [default: current directory]",
                       default=os.getcwd(), type="string"
                       )
    parser.add_option("-f", "--file", help="File to log to", default="log.log",
                      type="string")
    parser.add_option("--pid", help="The location of a .pid file. "\
                      "When not specified, a temporary location will be used ($TMPDIR/logdaemon.pid). "\
                      "The daemon uses this file to make sure no two instances are running "\
                      "with the same .pid file.",
                      default=None)
    (options, args) = parser.parse_args(args)
    if not options.pid:
        tmpdir = os.getenv("TMPDIR", "/tmp")
        pidfile = os.path.join(tmpdir, 'logdaemon.pid')
    else:
        pidfile = os.path.expanduser(options.pid)
    logdir = os.path.expanduser(options.logdir)
    #start daemon
    daemon = LogDaemon(options.host, options.port,
                       logdir, options.file, pidfile)
    if len(args) == 2:
        if 'stop' == args[1]:
            # save state before stopping?
            sys.stderr.write("stopping daemon with pidfile: %s\n" % pidfile)
            daemon.stop()
        elif 'restart' == args[1]:
            daemon.restart()
        elif 'start' == args[1]:
            daemon.start()
        else:
            sys.stderr.write("Unknown command\n")
            sys.stderr.write("usage: %s start|stop|restart [options]\n" % args[0])
            sys.exit(2)
        sys.exit(0)
    else:
        daemon.start()  # blocking call
    return


# get things started
if __name__ == '__main__':
    main(sys.argv)
