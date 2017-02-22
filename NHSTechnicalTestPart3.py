# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 17:32:32 2017

NHS Digital Technical Task - Part 2

Part 3 - Performance engineering

Modify the code in Part 2 to produce two files:
succeeded_validation.csv
failed_validation.csv

The postcodes in the two files need to be ordered as per the row_id, in ascending numeric order.
Analyse the performance of your solution and make an attempt to optimise the performance of the operation (in terms of overall 'wall' time taken). Describe how you improved the performance of the code, and how you measured the impact of your changes.
It is acceptable to not use the regular expression (or different regular expression(s)) for this part of the task, but the output in terms of the correctness of the validation needs to match the critieria in Part 1.
  
@author: Tim Greening-Jackson
"""
import logging
import csv

from NHSPostCode import PostCode

def WriteOutputFile(filename, records, description=None):
    """
    Writes the output of a list of PostCode objects to a CSV file.
    
    Parameters: 
        filename:     The name of the file
        records:      A list of PostCode records in the order in which they should be written
        description:  An optional description which will be sent to the logger
        
    Returns:
        Boolean. True if successful.
        
    """

    try:
        with open(filename, "w", newline='') as outfile:
            if description:
                logging.info("Writing {} list to {} ({:,} records)".format(description, 
                             filename, len(records)))
            writer = csv.writer(outfile)
            writer.writerow(['row_id', 'postcode'])
            [writer.writerow([r.row_id, r.postcode]) for r in records]
            return True
    except PermissionError:
        logging.error("Can't open {} for writing".format(filename))
        return False

def PerformTests(InputFileName   = 'import_data.csv',
                 SuccessFileName = 'succeeded_valdation.csv', 
                 ErrorFileName   = 'failed_validation.csv'):
    """
    Performs the part 3 tests
    
    Parameters:
        
        InputFileName:   Name of the input CSV file from which the postcodes are read
        SuccessFileName: Name of the file to which to write the valid postcode records 
        ErrorFileName:   Name of the file to which to write invalid postcode records
        
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
        with open(InputFileName) as infile:
            reader = csv.reader(infile)
            pcs = [PostCode(r[1], r[0]) for i, r in enumerate(reader)][1:]
            # Having got the list of postcodes,  divide it in to two lists, 
            # for the successful and unsuccessful postcode matches
            
            logging.info("Creating sorted lists")
            successful   = sorted([p for p in pcs if p.match])
            unsuccessful = sorted([p for p in pcs if not p.match])
            WriteOutputFile(SuccessFileName, successful, "matched")
            WriteOutputFile(ErrorFileName, unsuccessful, "unmatched")
            return True
    
    except FileNotFoundError:
        logging.error("Can't find file {}".format(InputFileName))
    except IOError:
        logging.error("Can't open file {} for reading".format(InputFileName))
    return False

if __name__ == '__main__':

    PerformTests()