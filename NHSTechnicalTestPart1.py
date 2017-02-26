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
import sys
import unittest
from NHSPostCode import PostCode, PCValidationCodes

class PostCodeTest(unittest.TestCase):
    """
    Unit tests test the PostCode validation. Note that these
    test validation against the specified RE and not that the 
    supplied postcode is an entrirely valid UK one.
    
    All test cases specified are run with the analyse flag being
    set to True, False and unset, representing all possible test
    cases.
    
    As the unit tests don't produce any output unless they fail, we 
    also log some output for the record.
    """
           
    def test_good_postcodes(self):
        """
        Test the postcodes which we expect to pass. They should return
        PCValidationCodes.OK whether or not the analysis flag is set.
        
        Note we test for the analyse flag being set True, False and not set
        at all.
        """
        PostCodes = ['EC1A 1BB', 'W1A 0AX',  'M1 1AE',     'B33 8TH',  
                     'CR2 6XH',  'DN55 1PT', 'GIR 0AA',    'SO10 9AA', 
                     'FY9 9AA',  'WC1A 9AA']

        for analyse in [True, False]:
            for postcode in PostCodes:
                p = PostCode(postcode, analyse=analyse)
                self.assertEqual(p.status, PCValidationCodes.OK)
                logging.info("Validating '{}' with analysis={}. Status={}".\
                             format(postcode, analyse, p.status))
        # Now test with the analyse flag not set at all (e.g. default)
        for postcode in PostCodes:
            p = PostCode(postcode)
            self.assertEqual(p.status, PCValidationCodes.OK)
            logging.info("Validating '{}' with no analysis flag. Status={}".\
                             format(postcode, p.status))
                
    def test_bad_postcodes_without_analysis(self):
        """
        Test the list of bad postcodes with the exception of 'LS44PL',
        with analyse not set (i.e. default value). They should all return PCValidationCodes.UNKNOWN, 
        as we know they're bad, but don't know why. (The 'LS44PL' would be detected
        early on uin the constructor, before parsing against the RE and so would
        be expected to return PCValidationCodes.INCORRECT_GROUPING rather than 
        PCValidationCodes.UNKNOWN)
        
        Note that we test for both the analyse flag being set False and also
        being omitted (i.e. default value). Both should return the same result
        """
        
        PostCodes = ['$%± ()()',  'XX XXX',   'A1 9A',    
                    'Q1A 9AA',    'V1A 9AA',  'X1A 9BB',  'LI10 3QP',
                    'LJ10 3QP',   'LZ10 3QP', 'A9Q 9AA',  'AA9C 9AA',
                    'FY10 4PL',   'SO1 4QQ']
        for postcode in PostCodes:
            p = PostCode(postcode)
            self.assertEqual(p.status, PCValidationCodes.UNKNOWN)
            logging.info("Validating '{}' with no analyse flag. Status={}".format(postcode, p.status))
            p = PostCode(postcode, analyse=False)
            self.assertEqual(p.status, PCValidationCodes.UNKNOWN)
            logging.info("Validating '{}' with analyse=False. Status={}".format(postcode, p.status))
            
    def test_junk_with_analysis(self):
        """
        Pass a junk code requesting analysis
        """
        postcode = '$%± ()()'
        p = PostCode(postcode, analyse=True)
        self.assertEqual(p.status, PCValidationCodes.JUNK)
        logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))
        
    def test_outward_aa9_malformed_with_analysis(self):
        """
        Test the outward AA9s with illegal characters in the outward part
        """
        PostCodes = ['LI10 3QP', 'LJ10 3QP', 'LZ10 3QP']
        for postcode in PostCodes:
            p = PostCode(postcode, analyse=True)
            self.assertEqual(p.status, PCValidationCodes.OUTWARD_AA9_MALFORMED)
            logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))

    def test_outward_aa9a_malformed_with_analysis(self):
        """
        Test the outward AA9s with illegal characters in the outward part
        """
        postcode = 'AA9C 9AA'
        p = PostCode(postcode, analyse=True)
        self.assertEqual(p.status, PCValidationCodes.OUTWARD_AA9A_MALFORMED)
        logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))

    def test_outward_malformed_with_analysis(self):
        """
        Test the postcodes with illegal characters in the outward part
        """
        PostCodes = ['Q1A 9AA', 'V1A 9AA', 'X1A 9BB', 'A9Q 9AA']
        for postcode in PostCodes:
            p = PostCode(postcode, analyse=True)
            self.assertEqual(p.status, PCValidationCodes.OUTWARD_MALFORMED)
            logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))

    def test_inward_malformed_with_analysis(self):
        """
        Test the postcodes with illegal characters in the inward part. Note that the postcode
        'XX XXX' has illegal inward and outward parts, so returns the result of the first test
        (inward) performed. If the structure of the code changes this might break.
        
        We don't specifically check for both inward and outward parts being malformed as
        in practice this would happen in so few instances as to be not worthwhile, given 
        that we've already checked that the postcode isn't junk.
        """
        PostCodes = ['XX XXX', 'A1 9A']
        for postcode in PostCodes:
            p = PostCode(postcode, analyse=True)
            self.assertEqual(p.status, PCValidationCodes.INWARD_MALFORMED)
            logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))
        
    def test_single_digit_district_with_analysis(self):
        """
        Test that single digit distrct test works...
        """
        postcode = 'FY10 4PL'
        p = PostCode(postcode, analyse=True)
        self.assertEqual(p.status, PCValidationCodes.SINGLE_DIGIT_DISTRICT)
        logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))
        
    def test_double_digit_district_with_analysis(self):
        """
        Test that double digit distrct test works...
        """
        postcode = 'SO1 4QQ'
        p = PostCode(postcode, analyse=True)
        self.assertEqual(p.status, PCValidationCodes.DOUBLE_DIGIT_DISTRICT)
        logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))        
        
    def test_no_space_with_analysis(self):
        """
        Test the postcode with no space between outward and inward parts. (Not
        parsed by the RE)
        """
        postcode = 'LS44PL'
        p = PostCode(postcode, analyse=True)
        self.assertEqual(p.status, PCValidationCodes.INCORRECT_GROUPING)
        logging.info("Validating '{}' with analyse=True. Status={}".format(postcode, p.status))        
        

def PerformTests():
    """
    Perform the Part 1 tests
    
    Parameters:
        None
        
    Returns:
        None
    """
    logging.info('Starting Part 1 tests')

    unittest.main()

    logging.info('Finished Part 1 tests')



if __name__ == '__main__':

    logging.basicConfig(stream = sys.stdout, level = logging.DEBUG, 
                format = '%(asctime)s:%(levelname)s:%(message)s')
    PerformTests()
    

