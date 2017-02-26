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

###`OK`
The postcode has matched correctly against the RE.

###`UNKNOWN`
The postcode has failed to match against the RE, but the cause is unknown
(the `analyse` flag was either not set or set to `False`)

###`OUTWARD_MALFORMED`
The outward group of the postcode (i.e. to the left of the space) does not fit
the known/allowed patterns e.g. `AA9A`

###`OUTWARD_AA9A_MALFORMED`
The outward group of an `AA9A` postcode is malformed. This is usually because it contains
an illegal character (e.g. `Q`)

###`OUTWARD_AA9_MALFORMED`  
The outward group of an `AA9` postcode is malformed. This is usually because it contains
an illegal character (e.g. `Q`). Note that errors in single and double digit areas
have separate codes, `SINGLE_DIGIT_DISTRICT` and `DOUBLE_DIGIT_DISTRICT`. 


###`OUTWARD_A9_MALFORMED`   
The outward group of an `A9` postcode is malformed. This is usually because it contains
an illegal character (e.g. `Q`)

###`INWARD_MALFORMED`       
The inward group (to the right of the space)  of any postcode is malformed, usually because
it contains an illegal character (e.g. `I`)

###`INCORRECT_GROUPING`
The number of groups (i.e. sets of alphanumeric characters separated by a single whitespace)
is not exactly two.

###`JUNK`
The postcode contains non alphanumeric/whitespace characters. 

###`SINGLE_DIGIT_DISTRICT`
The postcode area should only have single digit districts.

###`DOUBLE_DIGIT_DISTRICT`
The postcode area should only have double digit districts.