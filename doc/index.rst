.. vsc-base documentation master file, created by
   sphinx-quickstart on Mon Apr 29 17:56:48 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to vsc-base's documentation!
====================================
In this document we will try to explain how to use some of the vsc-base tools.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Option parsing
--------------
A lot of python scripts start of with parsing options. :py:mod:`vsc.utils.generaloption` provides a very general way of getting options.
It provides the :py:func:`vsc.utils.generaloption.simple_option` function, which lets you easily parse options from:
 * A config file
 * Environment variables
 * The command line

This is the simplest way to use generaloption, however, you can easily extend the :py:class:`vsc.utils.generaloption.GeneralOption` class to
provide a lot more fine graned options.

Example usage
^^^^^^^^^^^^^
You can use the :py:func:`vsc.utils.generaloption.simple_option` function to easily get a general option parser.
a general options dict has as key the long option name, and is followed by a list/tuple mandatory are 4 elements:
option help, type, action, default a 5th element is optional and is the short help name (if any)::

    """This is an example on how to use simple_option"""
    from vsc.utils.generaloption import simple_option
    opts = {
        "path": ("Specify the path to look for profiles.", None, "store",'defpath', "p"),
        "host": ("Specify a specific hostname (will guess the profile filename).", None, "store", None, "O"),
        "pxepath": ("Specify a path for the pxe base dir.", None, "store", 'pxepath', "P"),
        "vsmpversion": ("Specify a vsmp version.", None, "store", 'version', "V"),
        "imagerbase": ("Specify a path to imager subdirs (imager to be found in this path + /vSMP_version).", None, "store", 'imagerbase', "i"),
        "boot": ("Boot from pxe, hdd0", None, "store", 'boot', "b"),
        'licmgr': ("License host:port", None, "store", "%s:%s" % ('lic_host', 'lic_port'), "L")
    }
    parser = simple_option(opts, config_files=["/etc/myconfig.cfg", "%s/.myconfig.cfg" % os.path.expanduser("~")])
    options = parser.options
    parser.log.debug(options.path)

running this script with the -H option will give::
    Usage: test.py [options]


      This is an example on how to use simple_option

    Options:
      -h, --shorthelp       show short help message and exit
      -H, --help            show full help message and exit

      Main options (configfile section MAIN):
        -b BOOT, --boot=BOOT
                            Boot from pxe, hdd0 (def boot)
        -O HOST, --host=HOST
                            Specify a specific hostname (will guess the profile filename).
        -i IMAGERBASE, --imagerbase=IMAGERBASE
                            Specify a path to imager subdirs (imager to be found in this path + /vSMP_version). (def imagerbase)
        -L LICMGR, --licmgr=LICMGR
                            License host:port (def lic_host:lic_port)
        -p PATH, --path=PATH
                            Specify the path to look for profiles. (def defpath)
        -P PXEPATH, --pxepath=PXEPATH
                            Specify a path for the pxe base dir. (def pxepath)
        -V VSMPVERSION, --vsmpversion=VSMPVERSION
                            Specify a vsmp version. (def version)

      Debug and logging options (configfile section MAIN):
        -d, --debug         Enable debug log mode (def False)
        --info              Enable info log mode (def False)
        --quiet             Enable info quiet/warning mode (def False)

      Configfile options (configfile section MAIN):
        --configfiles=CONFIGFILES
                            Parse (additional) configfiles (type comma-separated list)
        --ignoreconfigfiles=IGNORECONFIGFILES
                            Ignore configfiles (type comma-separated list)

    Boolean options support disable prefix to do the inverse of the action, e.g. option --someopt also supports --disable-someopt.

    All long option names can be passed as environment variables. Variable name is SCRIPT_<LONGNAME> eg. --someopt is same as setting SCRIPT_SOMEOPT in the environment.


GeneralOption will now use a configfile (in /etc/myconfig.cfg or ~/.myconfig.cfg) to look up options.
The options in the config file can be overwritten when you set an environment variable (e.g., SCRIPT_DEBUG).
You can then furhter overwrite these options on the command line.

You will automatically have a short and long help, get the docstring in the help and get a :py:class:`vsc.utils.fancylogger.FancyLogger` logger and logging options.
(try running script.py -d)

Advanced option parsing
^^^^^^^^^^^^^^^^^^^^^^^



Config file format
^^^^^^^^^^^^^^^^^^
