import sys
import os
from setuptools import setup, find_packages


os.chdir(os.path.dirname(sys.argv[0]) or ".")


'''
==============================================================================
PACKAGE DATA
==============================================================================
'''
toplevel = 'cffi_utils'
version = '0.1'
packages = find_packages()
description = 'Utilities to write python wrappers around C code'
license = (
    'License :: OSI Approved :: '
    'GNU Lesser General Public License v3 or later (LGPLv3+)'
)

long_description = open('README.rst').read()
url = 'https://github.com/sundarnagarajan/cffi_utils'
download_url = 'https://github.com/sundarnagarajan/cffi_utils.git'
author = 'Sundar Nagarajan'
author_email = ''
maintainer = author
maintainer_email = author_email
install_requires = [
    'cffi>=1.0.0',
    'six>=1.9.0'
],
maintainer = author
maintainer_email = author_email
classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: PyPy',
    ('License :: OSI Approved :: '
     'GNU Lesser General Public License v3 or later (LGPLv3+)'
     )
]
zip_safe = True


'''
==============================================================================
ADDITIONAL DATA FILES
==============================================================================
'''

data_dirs = [
    'doc',
]


'''
==============================================================================
ADDITIONAL keyword args to setup()
==============================================================================
'''
ADDL_KWARGS = dict(
)


'''
==============================================================================
           DO NOT CHANGE ANYTHING BELOW THIS
==============================================================================
'''


def get_dirtree(toplevel, dirlist=[]):
    '''
    toplevel-->str: must be name of a dir under current working dir
    dirlist-->list of str: must all be names of dirs under toplevel
    '''
    ret = []
    curdir = os.getcwd()
    if not os.path.isdir(toplevel):
        return ret
    os.chdir(toplevel)
    try:
        for dirname in dirlist:
            if not os.path.isdir(dirname):
                continue
            for (d, ds, fs) in os.walk(dirname):
                for f in fs:
                    ret += [os.path.join(d, f)]
        return ret
    except:
        return ret
    finally:
        os.chdir(curdir)


# Required keywords
kwdict = dict(
    name=toplevel,
    version=version,
    packages=packages,
    description=description,
    license=license,
)

# Optional keywords
kwdict.update(dict(
    # requires=globals().get('requires,', []),
    install_requires=globals().get('install_requires,', []),
    long_description=globals().get('long_description', ''),
    url=globals().get('url', ''),
    download_url=globals().get('download_url', ''),
    author=globals().get('author', ''),
    author_email=globals().get('author_email', ''),
    maintainer=globals().get('maintainer', ''),
    maintainer_email=globals().get('maintainer_email', ''),
    classifiers=globals().get('classifiers', []),
    keywords=globals().get('keywords', []),
    zip_safe=globals().get('zip_safe', False),
))
kwdict.update(ADDL_KWARGS)

# More optional keywords, but which are added conditionally
ext_modules = globals().get('ext_modules', [])
if ext_modules:
    kwdict['ext_modules'] = ext_modules

dirlist = globals().get('data_dirs', None)
if isinstance(dirlist, list):
    kwdict['package_dir'] = {toplevel: toplevel}
    kwdict['package_data'] = {toplevel:
                              get_dirtree(toplevel, dirlist)}


setup(**kwdict)
