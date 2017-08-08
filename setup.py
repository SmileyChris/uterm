from setuptools import setup, find_packages
import io
import os

base_path = os.path.dirname(os.path.realpath(__file__))

setup(
    name='uterm',
    version='0.7',
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
    ],
    entry_points={
        'console_scripts': [
            'uterm=uterm.terminal:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Embedded Systems',
    ]
)
