import setuptools

setuptools.setup(
    name='protoconf',
    packages=['protoconf'],
    author='Software Innovation Bergen, Statoil ASA and TNO',
    install_requires=['decorator', 'enum34'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
