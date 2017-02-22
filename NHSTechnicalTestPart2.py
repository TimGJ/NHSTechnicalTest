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
import csv

from NHSPostCode import PostCode

def PerformTests(InputFileName = 'import_data.csv',
                 ErrorFileName = 'failed_validation.csv'):
    """
    Performs the part 2 tests
    
    Parameters:
        
        InputFileName: Name of the input CSV file from which the postcodes are read
        ErrorFileName: Name of the file to which to write invalid postcode records
        
    Returns:
        
        Success: Boolean. True if exectuted successfully else False
    """
    # Open the input and output files and then create a 
    # csv.DictReader and csv.DictWriter associated with each, 
    # assigning the same column names to the output file
    # as the input. Note that as of Python 3.x we need the "newline=''"
    # in the open statement to suppress printing blank lines in the 
    # CSV file if we run this under Windows.

    errs = 0 # Count of malformed records

    logging.info('Starting Part 2 tests')
    try:
        with open(InputFileName) as infile:
            try:
                with open(ErrorFileName, 'w', newline = '') as errfile:
                    reader = csv.DictReader(infile)
                    writer = csv.DictWriter(errfile, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    for i, record in enumerate(reader):
                        if not PostCode(record['postcode']).match:
                            writer.writerow(record)
                            errs += 1
                    logging.info('Part 2 tests completed. Read {:,} rows from {}. {:,} Errors ({:.0%}).'\
                                .format(i+1, InputFileName, errs, errs/(i+1)))
                return True
            except PermissionError:
                logging.error("Can't open {} for writing".format(ErrorFileName))
    except FileNotFoundError:
        logging.error("Can't find file {}".format(InputFileName))
    except IOError:
        logging.error("Can't open file {} for reading".format(InputFileName))
    return False
    

if __name__ == '__main__':

    PerformTests()        