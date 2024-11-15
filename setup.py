import sys
import platform

from setuptools import find_packages, setup

# Base requirements for all platforms
install_requires = [
    'apache-airflow[google]',
    'pandas==2.2.3',
    'pendulum==3.0.0',
]

extras_require = {
    'formatting': ['yapf==0.43.0', 'pre-commit'],
    'apple_silicon': [],
}

# Check if running on macOS with Apple Silicon
if sys.platform.startswith('darwin') and platform.machine() == 'arm64':
    install_requires.extend(extras_require['apple_silicon'])

setup(
    name='dnmaf',
    version='0.0.1',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
)
