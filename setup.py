from setuptools import setup, find_packages

setup(name='jss',
      version='0.1.0',
      description='JSON processing command line tool based on JSONSelect',
      author='Dan Vanderkam',
      author_email='danvdk@gmail.com',
      url='https://github.com/danvk/jss/',
      packages=find_packages(exclude=['tests*']),
      install_requires=['pyjsonselect'],
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
