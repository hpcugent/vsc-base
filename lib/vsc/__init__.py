# allow other packages to extend this namespace, zip safe setuptools style
import pkg_resources
pkg_resources.declare_namespace(__name__)
