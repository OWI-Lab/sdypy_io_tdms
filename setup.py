import os
import re

from setuptools import setup

base_path = os.path.dirname(__file__)

# Read the project version from "__init__.py"
regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

init_file = os.path.join(base_path, 'sdypy_io_tdms', '__init__.py')
with open(init_file, 'r') as f:
    module_content = f.read()

    match = regexp.match(module_content)
    if match:
        version = match.group(1)
    else:
        raise RuntimeError(
            'Cannot find __version__ in {}'.format(init_file))

# Read the "README.rst" for project description
with open('README.rst', 'r') as f:
    readme = f.read()

# Automatically parse the requirements.txt file for project requirements
def parse_requirements(filename):
    ''' Load requirements from a pip requirements file '''
    with open(filename, 'r') as fd:
        lines = []
        for line in fd:
            line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines

requirements = parse_requirements('requirements.txt')

if __name__ == '__main__':
    setup(
        name='sdypy_io_tdms',
        description='TDMS file read and write functions compliant with SDyPy SEP5',
        long_description=readme,
        license='MIT license',
        url='https://github.com/sdypy',
        version=version,
        author='Wout Weijtjens',
        author_email='wout.weijtjens@vub.be',
        maintainer='Wout Weijtjens',
        maintainer_email='wout.weijtjens@vub.be',
        install_requires=requirements,
        keywords=['io', 'tdms', 'SEP5'],
        packages=['sdypy_io_tdms'],
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Programming Language :: Python :: 3.6']
    )
