# NHSTechnicalTest
## Language and environment
The software is written in pure Python 3 and although written
and intended for use in a Linux environment should run
in pretty much any Python 3 environment.

It is assumed that a suitable file containing the input data is
available. By default this would be the file `import_data.csv`
in the current working directory, but a different location
may be specified either on the command line or passed as a parameter
to the appropriate scripts.

## Files
The software consists of the following source files

`NHSPostCode.py` Fundamental definitions (principally the PostCode class)
`NHSTechnicalTestPart1.py` Part 1 tests
`NHSTechnicalTestPart2.py` Part 2 tests
`NHSTechnicalTestPart3.py` Part 3 tests
`RunTests.py` The main script used to execute the tests

## Running the software

In a Linux, MacOS or Unix environment, assuming that the above files
are in the current working directory as well as the `import_data.csv`
file simply execute

`$ python3 RunTests.py`

For help/options execute

`$ python3 RunTests.py --help`



