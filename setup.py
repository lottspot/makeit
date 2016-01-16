from setuptools import setup

setup(
    name='makeit',
    version='0.0',
    description='A reimagined task loader for doit',
    author='James Lott',
    author_email='james@lottspot.com',
    license='MIT',
    keywords='doit build automation',
    packages=['makeit'],
    install_requires=['doit>=0.28'],
    test_suite='tests'
)