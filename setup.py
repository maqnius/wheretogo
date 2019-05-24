from setuptools import setup, find_packages

setup(
    name='wheretogo',
    version='1.0.0',
    url='https://github.com/maqnius/wheretogo.git',
    author='Mark Niehues',
    author_email='niehues.mark@gmail.com',
    description='Getting Events from some api',
    packages=find_packages(),
    install_requires=['requests >= 2.22.0', 'python-dateutil >= 2.8.0', 'pytz >= 2019.1'],
    python_requires='>=3.6, <4'
)
