from setuptools import setup, find_packages
import io
import os
from uterm import __version__

base_path = os.path.dirname(os.path.realpath(__file__))

setup(
    name='uterm',
    version=__version__,
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    description='Micropython-friendly terminal',
    long_description=io.open(
        os.path.join(base_path, 'README.rst'), encoding='utf-8').read(),
    url='https://github.com/SmileyChris/uterm',
    packages=find_packages(),
    install_requires=[
        'pyserial',
        'pyte',
        'docopt'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-timeout'],
    entry_points={
        'console_scripts': [
            'uterm=uterm.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Embedded Systems',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
