import setuptools

setuptools.setup(
    name='type_name',
    packages=['type_name'],
    author='Software Innovation Bergen, Statoil ASA and TNO',
    install_requires=['enum34'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
