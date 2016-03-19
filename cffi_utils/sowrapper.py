'''
    sowrapper: Utility functions to locate and load shared libraries

    Copyright (C) 2016 Sundar Nagarajan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    For details of the GNU General Pulic License version 3, see the
    LICENSE.txt file that accompanied this program
'''
from .ffi import FFIExt
import six
import sys
from pkg_resources import resource_filename
from distutils import sysconfig
from distutils.util import get_platform


def get_lib_ffi_resource(module_name, libpath, c_hdr):
    '''
    module_name-->str: module name to retrieve resource
    libpath-->str: shared library filename with optional path
    c_hdr-->str: C-style header definitions for functions to wrap
    Returns-->(ffi, lib)

    The 'clobbered' paths are tried FIRST, falling back to trying the
        unchanged libpath
    For generating the 'clobbered' filenames,libpath has to end in '.so'

    Use this method when you are loading a package-specific shared library
    If you want to load a system-wide shared library, use get_lib_ffi_shared
    instead
    '''
    # The lib name gets clobbered by FFI in Python3 and pypy
    # The format of the clobbered name doesn't seem to be documented anywhere
    # and is generated here by visual inspection :-(
    lib_base = libpath.rsplit('.so', 1)[0]
    ending = sysconfig.get_config_var('SO')
    plat_name = get_platform().replace('-', '_')
    if six.PY2 and sys.subversion[0].lower() == 'pypy':
        clobbered_path = '%s.%s-26-%s' % (
            lib_base, sys.subversion[0].lower(), sys._multiarch,
        ) + ending
    elif six.PY2:
        clobbered_path = lib_base + ending
    elif six.PY3:
        clobbered_path = lib_base + '.' + plat_name + ending

    try:
        libres = resource_filename(module_name, clobbered_path)
        return get_lib_ffi_shared(libpath=libres, c_hdr=c_hdr)
    except:
        # On Py2 we only need to try once
        if clobbered_path == libpath:
            raise
    try:
        libres = resource_filename(module_name, clobbered_path)
        return get_lib_ffi_shared(libpath=libres, c_hdr=c_hdr)
    except:
        # we need third attempt only on pypy!
        if six.PY3:
            raise
    # if PYPY try ./libpath
    libres = './' + os.path.basename(clobbered_path)
    return get_lib_ffi_shared(libpath=libres, c_hdr=c_hdr)


def get_lib_ffi_shared(libpath, c_hdr):
    '''
    libpath-->str: shared library filename with optional path
    c_hdr-->str: C-style header definitions for functions to wrap
    Returns-->(ffi, lib)
    '''
    lib = SharedLibWrapper(libpath, c_hdr)
    ffi = lib.ffi
    return (ffi, lib)


class SharedLibWrapper(object):
    def __init__(self, libpath, c_hdr):
        '''
        libpath-->str: library name; can also be full path
        c_hdr-->str: C-style header definitions for functions to wrap
        ffi-->FFIExt or cffi.FFI
        '''
        self._libpath = libpath
        self._c_hdr = c_hdr
        self.ffi = FFIExt()

        self.ffi.cdef(self._c_hdr)
        self._lib = self.ffi.dlopen(self._libpath)

    def __getattr__(self, name):
        if self._lib is None:
            return self.__getattribute__(name)
        return getattr(self._lib, name)

    def get_extension(self):
        return [self.ffi.verifier.get_extension()]
