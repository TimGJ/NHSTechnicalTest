# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 17:32:32 2017

NHS Digital Technical Task - Part 2

Part 2 - Bulk import
Imagine you are migrating demographic data, which includes postcode 
information and you need to check the data for invalid postcodes.

Write bulk import code that will validate the postcodes in the data file 
of around 2 million postcodes (download from google drive - 
https://drive.google.com/file/d/0BwxZ38NLOGvoTFE4X19VVGJ5NEk/view?usp=sharing) 
named import_data.csv.gz and report on the row_id where validation fails, 
the structure of import_data.csv.gz is shown below:
row_id	postcode
1	AABC 123
2	AACD 4PQ
...	...
If you need to untar the file, that is acceptable.
At the end of running the bulk import you should produce a file named, 
failed_validation.csv with the same columns as above.
  
@author: Tim Greening-Jackson
"""

import logging
import sys
import csv
import argparse

from NHSPostCode import PostCode, PCValidationCodes


def ProcessFiles(infile, errfile):
    """
    Processes the records in infile and writes ones which don't 
    have postcodes which match the RE to errfile in the same 
    format as infile.
    
    Parameters:
        infile: Handle of input file (opened before call)
        errfile: Handle of error (unmatched) file (opened before call)
        
    Returns:
        rows: Total number of rows processed
        errs: Total number of errored/malformed rows
    """
    rows = 0 # Total rows read 
    errs = 0 # Total errored rows
    # Create a dictionary reader which will read each line in to a 
    # dict keyed on field names. Then use the same fieldnames to drive
    # a dictwriter to output the errored records.
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(errfile, fieldnames=reader.fieldnames)
    writer.writeheader()   # Write the header line with the field names
    for record in reader:  # Iterate through all input records
        rows += 1
        # If a postcode doesn't validate OK then write that row to the unmatched file
        if PostCode(record['postcode']).status != PCValidationCodes.OK:
            writer.writerow(record)
            errs += 1
    return rows, errs

    
def PerformTests(InputFileName     = 'import_data.csv',
                 UnmatchedFileName = 'failed_validation.csv'):
    """
    Performs the part 2 tests
    
    Parameters:
        
        InputFileName: Name of the input CSV file from which the postcodes are read
        ErrorFileName: Name of the file to which to write invalid postcode records
        
    Returns:
        
        Success: Boolean. True if exectuted successfully else False
    """
    # Open the input and output files and then process their contents.
    # Note that as of Python 3.x we need the "newline=''"
    # in the open statement to suppress printing blank lines in the 
    # CSV file if we run this under Windows.

    # Try opening the input file, handling any plausible exceptions
    try:   
        logging.info("Opening {} for reading".format(InputFileName))
        with open(InputFileName) as infile: 
        # With the input sucesfully openend, try opening the output and handle exceptions                               
            try: 
                logging.info("Opening {} for writing ".format(UnmatchedFileName))
                with open(UnmatchedFileName, 'w', newline = '') as errfile:
                    rows, errs = ProcessFiles(infile, errfile) # Process the two files
                    logging.info('Read {:,} rows from {}. Wrote {:,} errored rows ({:.1%}).'\
                                 .format(rows, InputFileName, errs, errs/rows))
                    return True # Completed successfully
            except (PermissionError, FileNotFoundError):
                # PermissionError usually means we are trying to write to a directory
                # or overwrite a file where we don't have appropriate permissions.
                # We can (occasionally) get FileNotFoundError if the file has a filename
                # which is illegal - e.g. contains brackets or other strange characters
                logging.error("Can't open {} for writing".format(ErrorFileName))
    except FileNotFoundError: # Given it a file name which doesn't exist or we can't read
        logging.error("Can't find file {}".format(InputFileName))
    except IOError:           # Usually caused if the file is already open elsewhere
        logging.error("Can't open file {} for reading".format(InputFileName))
    return False
    

def ParseArguments():
    """
    Parse the command line arguments
    """
    parser = argparse.ArgumentParser(description="Perform Part 2 NHS Digital Technical Tests")
    parser.add_argument("--input",   
                        help="Input postcode data", 
                        default="import_data.csv")
    parser.add_argument("--unmatched",   
                        help="Output unmatched/invalid data", 
                        default="failed_validation.csv")
    return parser.parse_args()

if __name__ == '__main__':
    """
    Performs the Part 2 tests. Simply parses the arguments, sets up the logger
    stream and then calls the function to perform the tests.

    Command line arguments:
        --input:       Input file name
        --unmtached:   Output file name for unmatched
    """
    args = ParseArguments()
    logging.basicConfig(stream = sys.stdout, level = logging.DEBUG, 
                format = '%(asctime)s:%(levelname)s:%(message)s')

    PerformTests(InputFileName     = args.input,
                 UnmatchedFileName = args.unmatched)

