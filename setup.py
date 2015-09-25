from setuptools import setup, find_packages

setup(
    name='python-cloud-monitor',
    version='0.1',
    description='Monitor littleBits cloud devices for changes and report to slack',
    packages=find_packages(exclude=['build', 'dist', '*.egg-info']),
    install_requires=['slacker', 'websocket-client'],
    entry_points = {
        'console_scripts':
            ['cloud-monitor=python_cloud_monitor.cloud_monitor:main'],
    },
)
