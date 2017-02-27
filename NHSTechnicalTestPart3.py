# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 17:32:32 2017

NHS Digital Technical Task - Part 3

Performance engineering

Modify the code in Part 2 to produce two files:
succeeded_validation.csv
failed_validation.csv

The postcodes in the two files need to be ordered as per the row_id, in ascending numeric order.

Analyse the performance of your solution and make an attempt to optimise the performance of the 
operation (in terms of overall 'wall' time taken). Describe how you improved the performance of 
the code, and how you measured the impact of your changes.

It is acceptable to not use the regular expression (or different regular expression(s)) 
for this part of the task, but the output in terms of the correctness of the validation 
needs to match the critieria in Part 1.
  
@author: Tim Greening-Jackson
"""
import logging
import sys
import csv
import argparse

from NHSPostCode import PostCode, PCValidationCodes

def WriteOutputFile(filename, records, description=None):
    """
    Writes the output of a list of PostCode objects to a CSV file.
    
    Parameters: 
        filename:     The name of the file
        records:      A list of PostCode records in the order in which they should be written
        description:  An optional description which will be sent to the logger
        
    Returns:
        Boolean. True if successful.

    Note:
        As we are interested in performance for bulk import, we are using a
        CSV writer rather than a CSV DictWriter as the performance is significantly
        greater. This means, though, that we manually have to write the field names
        to the first row. We then use a dictionary comprehension to write the contents
        as this is much faster than an unrolled for loop.
        
    """

    try:
        with open(filename, "w", newline='') as outfile:
            if description:
                logging.info("Writing {} list to {} ({:,} records)".format(description, 
                             filename, len(records)))
            writer = csv.writer(outfile)             # Create the writer object
            writer.writerow(['row_id', 'postcode'])  # Write the header row with field names
            # Use a list comprehension for performance
            [writer.writerow([r.row_id, r.postcode]) for r in records]
            return True
    except (PermissionError, FileNotFoundError):
        # PermissionError usually means we are trying to write to a directory
        # or overwrite a file where we don't have appropriate permissions.
        # We can (occasionally) get FileNotFoundError if the file has a filename
        # which is illegal - e.g. contains brackets or other strange characters
        logging.error("Can't open {} for writing".format(filename))
        return False


def PerformTests(InputFileName       = 'import_data.csv',
                 SuccessFileName     = 'succeeded_valdation.csv', 
                 UnmatchedFileName   = 'failed_validation.csv'):
    """
    Performs the part 3 tests
    
    Parameters:
        
        InputFileName:     Name of the input CSV file from which the postcodes are read
        SuccessFileName:   Name of the file to which to write the valid postcode records 
        UnmatchedFileName: Name of the file to which to write invalid postcode records
        
    Returns:
        
        Boolean. True if successful, False on error
        
    Notes:
        
        The PostCode class and associated RE should be relatively efficient
        because:
        
        1. The RE is pre-compiled, dramatically improving its performance
        2. It is (deliberately) case insensitive
        3. The row_id is converted to integer in the constructor, and the
           class contains a __lt__ method. This will allow Python's 
           (very fast, inbuilt) sort routines to sort instances of the class.
           
        As we only have about 2M postcodes records, assuming each to be of the
        order of 20 bytes, the entire dataset will fit in to the memory of
        even the most modest of modern computer systems. Therefore the fastest,
        most efficient and easiest to understand solution is to store the
        entire dataset in memory in two lists, one for the successfully
        validated codes, the other for the unsuccessful ones, and then sort
        both lists prior to output.
        
        In a real-world application there are various ways in which the performance
        of the code could be improved. All of these however would involve either
        departing from the restriction that we can only use standard libraries,
        so we can't use numpy's vectorization and sorting routines, nor (on the
        assumption that this is an exercise in Python) write the code in C. These
        changes would also likely signficantly reduce the readability of the code
        with relatively little performance gain.
        
        The most efficient way to process the postcodes will be using 
        list comprehensions rather than explicit, unrolled for loops. It 
        will also be more efficient to use a CSV reader (i.e. which just
        works on column indicies) rather than a CSV DictReader which will
        create a Python dict object for each row.
        
        We need to skip the first line of the input file. The most efficient
        way to do this is to read it anyway and then discar it by slicing
        the resultant list [1:]
    """

    logging.info('Starting Part 3 tests')
    try:
        logging.info("Reading {}".format(InputFileName))
        with open(InputFileName) as infile:
            reader = csv.reader(infile)
            pcs = [PostCode(r[1], r[0]) for i, r in enumerate(reader)][1:]
            # Having got the list of postcodes,  divide it in to two lists, 
            # for the successful and unsuccessful postcode matches. Using two
            # separate list comprehensions rather than a single for loop which 
            # appends records to two lists will be much faster.
            
            logging.info("Creating sorted lists")
            # Note that as we have an __lt__ method defined in the 
            # PostCode class, we can sort postcodes in to order automatically
            # using the Python sorted keyword. This will be extremely fast 
            # (and much easier to understand and maintain) than explicitly 
            # defining our own sort routines.

            successful   = sorted([p for p in pcs if p.status == PCValidationCodes.OK])
            WriteOutputFile(SuccessFileName,   successful,   "matched")

            unsuccessful = sorted([p for p in pcs if p.status != PCValidationCodes.OK])
            WriteOutputFile(UnmatchedFileName, unsuccessful, "unmatched")
            return True
    
    except FileNotFoundError:
        logging.error("Can't find file {}".format(InputFileName))
    except IOError:
        logging.error("Can't open file {} for reading".format(InputFileName))
    return False


def ParseArguments():
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(description="Perform Part 3 NHS Digital Technical Tests")
    parser.add_argument("--input",       
                        help="Input postcode data", 
                        default="import_data.csv")
    parser.add_argument("--matched",     
                        help="Output matched/validated data", 
                        default="succeeded_validation.csv")
    parser.add_argument("--unmatched",   
                        help="Output unmatched/invalid data", 
                        default="failed_validation.csv")

    return parser.parse_args()

if __name__ == '__main__':
    """
    Performs the Part 3 tests. Simply parses the arguments, sets up the logger
    stream and then calls the function to perform the tests.
    
    Command line arguments:
        --input:       Input file name
        --matched:     Output file name for matched records
        --unmtached:   Output file name for unmatched
        
    """
    args = ParseArguments()
    logging.basicConfig(stream = sys.stdout, level = logging.DEBUG, 
                format = '%(asctime)s:%(levelname)s:%(message)s')

    PerformTests(InputFileName       = args.input,
                 SuccessFileName     = args.matched, 
                 UnmatchedFileName   = args.unmatched)