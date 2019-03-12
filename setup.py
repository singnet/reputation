from setuptools import setup, find_packages
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install

class develop(_develop):
    # Post-installation for dev mode
    def run(self):
        _develop.run(self)

class install(_install):
    # Post-installation for install mode
    def run(self):
        _install.run(self)

setup(
    name='reputation_agency',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/singnet/reputation',
    license='MIT',
    author='SingularityNET Team',
    description='Reputation Agency',
    install_requires=[
      'pandas',
      'numpy',
      'requests'
    ],
    cmdclass={
        'develop': develop,
        'install': install,
    },
    include_package_data=True
)
