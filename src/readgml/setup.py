from distutils.core import setup, Extension

setup(name='readgml',
    ext_modules=[
        Extension('readgml',
            ['read_gml.c'],
            include_dirs = ['.'],
            define_macros = [],
            undef_macros = [],
            library_dirs = ['.'],
            libraries = []
        )
    ]
)