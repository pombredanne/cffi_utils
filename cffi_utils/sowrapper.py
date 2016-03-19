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
from distutils import sysconfig as dist_sysconfig


def get_lib_ffi_resource(module_name, libpath, c_hdr):
    '''
    module_name-->str: module name to retrieve resource
    libpath-->str: shared library filename with optional path
    c_hdr-->str: C-style header definitions for functions to wrap
    Returns-->(ffi, lib)

    Use this method when you are loading a package-specific shared library
    If you want to load a system-wide shared library, use get_lib_ffi_shared
    instead

    PEP3140: ABI version tagged .so files:
        https://www.python.org/dev/peps/pep-3149/

    There's still one unexplained bit: pypy adds '-' + sys._multiarch()
    at the end (looks like 'x86_64-linux-gnu'), but neither py2 or py3 do

    _I_ think Py2 and Py3 _MAY_ start adding sys._multiarch at some time

    So, we generate three forms:
        1. With sys._multiarch
        2. Without sys._multiarch
        3. libpath as-is
    For different versions we try these in different orders (for efficiency):
        Python2                 Python3                 Pypy

        2 --> 1 --> 3           2 --> 1 --> 3           1 --> 2 --> 3
    '''
    ending = '.so'
    base = libpath.rsplit(ending, 1)[0]
    abi = dist_sysconfig.get_config_var('SOABI')
    if abi != '':
        abi = '.' + abi
    else:
        abi = ''
    multi_arch = '-' + sys._multiarch

    if six.PY2 and sys.subversion[0].lower() == 'pypy':
        n1 = base + abi + multi_arch + ending
        n2 = base + abi + ending
        n3 = libpath
    else:
        n1 = base + abi + ending
        n2 = base + abi + multi_arch + ending
        n3 = libpath

    try:
        libres = resource_filename(module_name, n1)
        return get_lib_ffi_shared(libpath=libres, c_hdr=c_hdr)
    except:
        try:
            libres = resource_filename(module_name, n2)
            return get_lib_ffi_shared(libpath=libres, c_hdr=c_hdr)
        except:
            libres = resource_filename(module_name, n3)
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
