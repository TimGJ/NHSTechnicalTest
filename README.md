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

1. `NHSPostCode.py` Fundamental definitions (principally the PostCode class)
2. `NHSTechnicalTestPart1.py` Part 1 tests
3. `NHSTechnicalTestPart2.py` Part 2 tests
4. `NHSTechnicalTestPart3.py` Part 3 tests
5. `RunTests.py` The main script used to execute the tests

## Running the software

In a Linux, MacOS or Unix environment, assuming that the above files
are in the current working directory as well as the `import_data.csv`
file simply execute

`$ python3 RunTests.py`

This will write the default output files to the current directory.

For help/options execute

`$ python3 RunTests.py --help`

Output is via the Python logger to sys.stdout. It can be redirected
to a file by using the `--logfile` option

`$ python3 RunTests.py --logfile = test.log`

To specify an input file name use the `--input` option e.g.

`$ python3 RunTests.py --input = /home/fred/import_data.csv`

To specify error (i.e. unmatched) and success (i.e. matched) files
use the `--unmatched` and `--matched` options respectively e.g.

`$ python3 RunTests.py --error = /tmp/bad.csv --matched = /tmp/good.csv`

By default all three sets of tests are run. To specify one or more
parts to run use the `--parts` option e.g.

`$ python3 RunTests.py --parts 2 3`

would only run the Part 2 and Part 3 tests. All command line options may be
abbreviated.

# Validation and Status Codes

In the event that a PostCode does not validate an analysis can optionally
be run. Objects of the `PostCode` class have an attribute `status`.

The following codes are defined

`OK                     ` The code has validated successfully
`OUTWARD_TOO_SHORT      ` The outward part of the code is too short
`OUTARD_TOO_LONG        ` The outward part of the code is too long
`OUTWARD_MALFORMED      ` The outward part is malformed
`INWARD_MALFORMED       ` The inward part is malformed
`TOO_MANY_PARTS         ` The code has too many parts/whitespace
`NO_SPACE               ` There is no space separating the outward and inward parts
`JUNK                   ` The code is junk - i.e. contains non alphanumeric/whitespace
`AA9A_MALFORMED         ` An AA9A type outward code contains an illegal letter
`AA9_MALFORMED          ` An AA9 type outward code contains an illegal letter
`A9_MALFORMED           ` An A9 type outward code contains an illegal letter
`SINGLE_DIGIT_DISTRICT  ` The PostCode district only allows single digits
`DOUBLE_DIGIT_DISTRICT  ` The PostCode district only allows double digits
