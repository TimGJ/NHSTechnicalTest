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

    # Try opening the output file, and handle any plausible errors which
    # might occur
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

def SortPostCodeList(postcodes):
    """
    Sorts a list of PostCode objects in to order in place
    
    Sorting is as defined by the PostCode class (currently on the basis
    of numeric row_id as specified in the class' __lt__ method)
    
    Parameters:
        postcodes:  List of PostCode objects
        
    Returns:
        
        None
    
    Notes:
        
        We are using the list.sort() method rather than the sorted(list)
        keyword. The list.sort() method sorts the list in place, whereas
        sorted(list) produces a new copy in memory. list.sort() is therefore
        more efficient, particularly on larger lists. In testing, the
        sorted(list) approach was found to be 23% faster!
        
        However, the .sort() method applies only to lists, whereas sorted()
        can be used on any iterable - e.g. sets, dictionaries. 
        
        The routine will sort a homogeneous list of any type of object,
        not just PostCodes provided those objects are sortable (i.e. have
        an __lt__ method). But the list has to be homogeneous (i.e. composed
        entirely of the same type of object). In case we are accidentally fed
        a heterogeneous list, then we should catch TypeError and handle 
        it gracefully. 
    """
    try:
        postcodes.sort()
    except TypeError:
        logging.error("Type mismatch in list")

def SplitAndSortPostCodeList(postcodes):
    """
    Splits the list of PostCode objects, pcs, in to two other lists:
    matched and unmatched (on the basis of PostCode.status == 
    PCValidationCodes.OK). Then sorts the lists before returning them. 
    
    Parameters:
        postcodes:    List of PostCode objects

    Returns:
        successful:   Sorted list of successfully matched PostCode objects
        unsuccessful: Sorted list of unsuccessfully matched PostCode objects

    Notes:

        Creates two lists of postcodes. We are essentially doing:

        successful   = []
        unsuccessful = []
        for p in postcodes:
            if p.status == PCValidationCodes.OK:
                successful.append(p)
            else:
                unsuccessful.append(p)
    
         But using list comprehensions is significantly faster (in testing 12%). 
         
         This is because list comprehesions are performed in the underying C code 
         which is much faster than an unrolled for loopin which each statement
         has to be interpreted by the interpreter, even though we have to 
         traverse the entire list twice.

    """
    
    # Create the two lists of successfully and unsuccessfully validated PostCodes
    successful   = [p for p in postcodes if p.status == PCValidationCodes.OK]
    unsuccessful = [p for p in postcodes if p.status != PCValidationCodes.OK]

    # Now sort them in place (hence no assignment required)
    SortPostCodeList(successful)
    SortPostCodeList(unsuccessful)
    return successful, unsuccessful
    
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
        2. It is (deliberately) case insensitive, simplifying lookup
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
        assumption that this is an exercise in Python) write the code in C or Go. These
        changes would also likely signficantly reduce the readability of the code
        with relatively little performance gain.
        
        The most efficient way to process the postcodes will be using 
        list comprehensions rather than explicit, unrolled for loops. It 
        will also be more efficient to use a CSV reader (i.e. which just
        works on column indicies) rather than a CSV DictReader which will
        create a Python dict object for each row.
        
        We need to skip the first line of the input file. The most efficient
        way to do this is to read it anyway and then discard it by slicing
        the resultant list [1:]
    """

    # Try opening the input file and deal with any plausible exceptions
    try:
        logging.info("Reading {}".format(InputFileName))
        with open(InputFileName) as infile:
            
            # Having successfully opened the file, create the csv reader and then
            # iterate over it, creating a PostCode object for each record. 
            # 
            # We do this using a list comprehension rather than an unrolled
            # for loop for reasons of performance and readability.
            #
            # However, as we are doing this with a csv.reader rather than 
            # a csv.DictReader it will read the first line, which contains the
            # field names, as a record. So we need to discard that (hence the [1:]
            # slice.
            
            reader = csv.reader(infile)
            postcodes = [PostCode(r[1], r[0]) for r in reader][1:]
            
            # Note that we omit the optional "analyse" parameter when
            # we create the PostCode objects, so invalid ones will
            # simply have PostCode.status = PCValidationCodes.UNKNOWN
            # for reasons of performance. Individual PostCode objects :
            # can still be analysed by calling their foo.Analyse() method
            # which will set foo.status to the appropriate value.

            logging.info("Creating sorted lists")

            # Having created the list of postcodes, split it in to two
            # sorted lists, one containing successfully validated postcodes and
            # the other unsuccessful ones. 

            successful, unsuccessful = SplitAndSortPostCodeList(postcodes)
            WriteOutputFile(SuccessFileName,   successful,   "matched")
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