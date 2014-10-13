from setuptools import setup, find_packages

try:
   import pypandoc
   description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   description = ''


setup(name='jss',
      version='0.1.0',
      description='JSON processing command line tool based on JSONSelect',
      long_description=description,
      author='Dan Vanderkam',
      author_email='danvdk@gmail.com',
      url='https://github.com/danvk/jss/',
      packages=['jss'],
      install_requires=['pyjsonselect'],
      entry_points={
          'console_scripts': [
              'jss = jss.jss:main',
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Utilities',
          'Topic :: Text Processing'
      ],
      keywords=[
          'css',
          'json',
          'jsonselect'
      ]
)
