##
# Copyright 2015-2015 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/vsc-base
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
##
"""
Module providing custom exceptions.

@author: Kenneth Hoste (Ghent University)
@author: Riccardo Murri (University of Zurich)
"""
import inspect
import logging
from vsc.utils import fancylogger


def get_callers_logger():
    """
    Get logger defined in caller's environment
    @return: logger instance (or None if none was found)
    """
    logger_cls = logging.getLoggerClass()
    frame = inspect.currentframe()
    logger = None

    # frame may be None, see https://docs.python.org/2/library/inspect.html#inspect.currentframe
    if frame is not None:
        try:
            # consider calling stack in reverse order, i.e. most inner frame (closest to caller) first
            for frameinfo in inspect.getouterframes(frame)[::-1]:
                bindings = inspect.getargvalues(frameinfo[0]).locals
                for val in bindings.values():
                    if isinstance(val, logger_cls):
                        logger = val
                        break
        finally:
            # make very sure that reference to frame object is removed, to avoid reference cycles
            # see https://docs.python.org/2/library/inspect.html#the-interpreter-stack
            del frame

    return logger


class LoggedException(Exception):
    """Exception that logs it's message when it is created."""

    # logger module to use (must provide getLogger() function)
    LOGGER_MODULE = fancylogger
    # logging method to use
    # takes a logger instance and an argument of type string, i.e. the log message
    # note: 'self' (LoggedException instance) is passed as 1st argument, which is typically just ignored
    LOGGING_METHOD = lambda _, logger, msg: logger.error(msg)

    def __init__(self, msg, logger=None):
        """
        Constructor.
        @param logger: logger to use
        """
        # try to use logger defined in caller's environment
        if logger is None:
            logger = get_callers_logger()
            # search can fail, use root logger as a fallback
            if logger is None:
                logger = self.LOGGER_MODULE.getLogger()

        self.LOGGING_METHOD(logger, msg)

        super(LoggedException, self).__init__(msg)
