# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 17:32:32 2017

NHS Digital Technical Task - Part 1


Write unit tests and implement the regular expression to check the validity of the following postcodes:
Postcode	Expected problem
$%± ()()	Junk
XX XXX	Invalid
A1 9A	Incorrect inward code length
LS44PL	No space
Q1A 9AA	'Q' in first position
V1A 9AA	'V' in first position
X1A 9BB	'X' in first position
LI10 3QP	'I' in second position
LJ10 3QP	'J' in second position
LZ10 3QP	'Z' in second position
A9Q 9AA	'Q' in third position with 'A9A' structure
AA9C 9AA	'C' in fourth position with 'AA9A' structure
FY10 4PL	Area with only single digit districts
SO1 4QQ	Area with only double digit districts
EC1A 1BB	None
W1A 0AX	None
M1 1AE	None
B33 8TH	None
CR2 6XH	None
DN55 1PT	None
GIR 0AA	None
SO10 9AA	None
FY9 9AA	None
WC1A 9AA	None
Please read (https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Validation), 
does the regular expression validate all UK postcode cases?

@author: Tim Greening-Jackson
"""
import logging
from NHSPostCode import PostCode

def PerformTests():
    """
    Perform the Part 1 tests
    
    Parameters:
        None
        
    Returns:
        None
    """
    logging.info('Starting Part 1 tests')

    BadPostCodes = ['$%± ()()',  'XX XXX',   'A1 9A',    'LS44PL',
                    'Q1A 9AA',    'V1A 9AA',  'X1A 9BB',  'LI10 3QP',
                    'LJ10 3QP',   'LZ10 3QP', 'A9Q 9AA',  'AA9C 9AA',
                    'FY10 4PL',   'SO1 4QQ']
    
    GoodPostCodes = ['EC1A 1BB', 'W1A 0AX',  'M1 1AE',     'B33 8TH',  
                     'CR2 6XH',  'DN55 1PT', 'GIR 0AA',    'SO10 9AA', 
                     'FY9 9AA',  'WC1A 9AA']
    
    for pcset, description in zip([BadPostCodes, GoodPostCodes], 
                                  ["Malformed", "Correctly formed"]):
        logging.info("Testing {} postcodes".format(description))
        for result in [PostCode(p) for p in pcset]:
            if result.match:
                logging.info("Postcode {:10} matched OK".format(result.postcode))
            else:
                logging.info("Postcode {:10} failed to match".format(result.postcode))
    logging.info('Finished Part 1 tests')


if __name__ == '__main__':

    PerformTests()
    

