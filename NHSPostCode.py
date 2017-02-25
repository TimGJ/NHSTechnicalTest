
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 19:40:21 2017

Common classes and other definitions for the NHS technical test

Write code that will validate UK postcodes.
You are given a regular expression that validates postcodes (shown in verbose form below):
    (GIR\s0AA) |
    (
        # A9 or A99 prefix
        ( ([A-PR-UWYZ][0-9][0-9]?) |
             # AA99 prefix with some excluded areas
            (([A-PR-UWYZ][A-HK-Y][0-9](?<!(BR|FY|HA|HD|HG|HR|HS|HX|JE|LD|SM|SR|WC|WN|ZE)[0-9])[0-9]) |
             # AA9 prefix with some excluded areas
             ([A-PR-UWYZ][A-HK-Y](?<!AB|LL|SO)[0-9]) |
             # WC1A prefix
             (WC[0-9][A-Z]) |
             (
                # A9A prefix
               ([A-PR-UWYZ][0-9][A-HJKPSTUW]) |
                # AA9A prefix
               ([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY])
             )
            )
          )
          # 9AA suffix
        \s[0-9][ABD-HJLNP-UW-Z]{2}
        )

NOTES

The exercise is to implement the regular expression (re) above AS IS.

1. As it is, the re will match postcodes which match the beginning of the
   string but would ignore junk after it - e.g. "M1 7EPTHIS IS JUNK"
   This (presumably) is undesirable and we would be better getting it to match 
   end-line character by adding "$" to the end of the RE. But this isn't 
   what the specification states. We can, however, work around this by 
   using match.groups()[1] which will return only the validated postcode 
   and not any extraneous trailer, assuming it has matched. This will return
   a "clean" postcode

2. The specification also mandates a single whitespace (\s) character
   separating the inward and outward parts. It might be better to allow 0
   or more, i.e. \s*. From experience of parsing postcode data from various
   sources (e.g. Ofcom, local authorities) this is often not the case. So 
   "M1 7EP" might be presented as "M17EP" or "M1  7EP" both of which would 
   fail here. (Sepcifically this is a failure case for LS44PL above)
   
   Some "official" datasets (e.g. OS CodePoint Open) assume that postcodes are of a
   fixed width (7 chars) and so would format AA99 9AA as "AA999AA" and
   "A9 9AA" as "A9  9AA". Other datasets (e.g. Ofcom broadband data) assume
   that there is no space between in the inbound and outbound parts of the
   postcode - so "A9 9AA" would be "A99AA". The OS AddressBase Premium 
   database formats all postcodes with a single space between the inbound 
   and outbound parts of the postcode. This applies to both the BLPU
   postcodes (i.e. land registry) and the Royal Mail delivery point
   addresses.

3. Assuming that the re specified is a perl/python format one, then it 
   will be case sensitive and so would only allow postcodes where all letters
   are UPPERCASE. From experience, pretty much all postcodes are in UPPERCASE
   but we could add the re.IGNORECASE flag if we wanted it to handle lowercase
   letters within the context of a legal postcode. However there would, of course,
   be a performance penalty for a case-insensitive match, and so the re will
   be more efficient if we don't do it.
   
4. Although it is strictly beyond the scope of this exercise, the re has
   been tested on ALL 1.7M UK postcodes and has validated them all successfully.
   It will, of course, validate various nonexistent postcodes, provided they are
   legal within the scope of the re definition.
   
5. It doesn't correctly match some postcodes (i.e. allows false positives).

   A. Only postcode areas BL, BS, CM, CR, FY, HA, PR, SL, SS have a district 0,
      but the re will allow e.g. M0.

   B. Similarly it will allow things like "M1A 9AA"

   C. Despite appearing to handle it, the re also allows the WC area to 
      have districts which do not have a trailing letter - e.g. it allows 
      WC4 9PP. All postcodes in the WC area are of the form WC9A 9AA.
   
    
@author: Tim Greening-Jackson
"""
import re
import unittest
import enum
import logging
import sys

# Set up logging (principally used for interactive debugging
# purposes)

logging.basicConfig(stream = sys.stdout, level = logging.DEBUG, 
                format = '%(asctime)s:%(levelname)s:%(message)s')


class PCValidationCodes(enum.Enum):
    """
    Enumeration to contain the possible reasons for 
    a PostCode not to validate according to the rules
    and testcases defined.
    """
    OK                     = enum.auto()
    OUTWARD_TOO_SHORT      = enum.auto()
    OUTARD_TOO_LONG        = enum.auto()
    OUTWARD_MALFORMED      = enum.auto()
    INWARD_MALFORMED       = enum.auto()
    TOO_MANY_PARTS         = enum.auto()
    NO_SPACE               = enum.auto()
    JUNK                   = enum.auto()
    AA9A_MALFORMED         = enum.auto()
    AA9_MALFORMED          = enum.auto()
    A9_MALFORMED           = enum.auto()
    SINGLE_DIGIT_DISTRICT  = enum.auto()
    DOUBLE_DIGIT_DISTRICT  = enum.auto()


class PostCode:
    """
    Very simple class to contain a postcode and (if supplied) a row_id
    """
    # Compile the RE for speed (note that the re.VERBOSE flag should
    # automatically trim whitespace and comments)
    
    
    REString = """
    (GIR\s0AA) |
    (
        # A9 or A99 prefix
        ( ([A-PR-UWYZ][0-9][0-9]?) |
             # AA99 prefix with some excluded areas
            (([A-PR-UWYZ][A-HK-Y][0-9](?<!(BR|FY|HA|HD|HG|HR|HS|HX|JE|LD|SM|SR|WC|WN|ZE)[0-9])[0-9]) |
             # AA9 prefix with some excluded areas
             ([A-PR-UWYZ][A-HK-Y](?<!AB|LL|SO)[0-9]) |
             # WC1A prefix
             (WC[0-9][A-Z]) |
             (
                # A9A prefix
               ([A-PR-UWYZ][0-9][A-HJKPSTUW]) |
                # AA9A prefix
               ([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY])
             )
            )
          )
          # 9AA suffix
        \s[0-9][ABD-HJLNP-UW-Z]{2}
        )
    """
    RE = re.compile(REString, re.VERBOSE)

    def __init__(self, rawtext, row_id=None, analyse=False):
        """
        Parameters:
            raw:     The raw text of the postcode which will be validated

            row_id:  The row_id read from the file. Converted to integer if possible

            analyse: In production/bulk import we wouldn't want to to analyse the reason
                     that a particular PostCode didn't validate for reasons of performance.
                     However, in unit testing we would. So this flag controls validation
                     of those postcodes which don't validate
                     
        Note:
            
            It is reasonable to assume that only a small minority (from experience
            < 10%) of postcodes will be invalid and that in a bulk-import operation
            we wouldn't want to find out the reasons for individual postcodes being
            rejected. So it is much more efficient to make a single call to a monolithic
            RE which will parse the entire thing rather than splitting it. So we do
            the initial match against the supplied RE and only if that fails do we 
            consider going in to finer detail.
            
        """
        self.postcode = rawtext                     # The raw text of the postcode
        self.match    = PostCode.RE.match(rawtext)  # Match against the specified RE
        self.inward   = None                        # Placeholder for inward part of PC
        self.outward  = None                        # Placeholder for outward part of PC

        try:
            self.row_id = int(row_id)               # Convert the rowid to integer which will make sorting etc. much faster
        except (ValueError, TypeError):
            self.row_id = None

        if not self.match and analyse:              # If it hasn't matched, find out why
            self.errorcode = self.Analyse()
        else:
            self.errorcode = None

    def __repr__(self):
        return "{}: {}".format(self.postcode, self.row_id)
    
    def __lt__(self, other):                       # Required to sort PostCodes in to row_id order
        if self.row_id and other.row_id:           # If they both have row_ids
            return self.row_id < other.row_id
        else:                                      # But we might also want to sort postcodes with no row_id
            return self.postcode < other.postcode

    def Analyse(self):
        """
        Analyses a piece of text which has failed validation to find out why.
        
        Python REs either match completely or they fail. There is no partial 
        matching of certain groups (unlike the Java function hitEnd()). 
        
        Therefore to work out why a particular piece of input
        text failed to match the given RE, we must divide the RE in to its 
        component groups. Ordinarily we would use a library like pyparsing 
        to divide the RE in to manageable chunks, but it's not part of the 
        standard libary, so we manually divide the RE and test it in stages.
        
        This, obviously, has two potential problems. Firstly we might somehow
        accidentally mangle the parts of the RE in the process of transcription
        copying. Secondly if the specification of the parent RE changes, we must
        ensure that the various child REs below are updated appropriately.
        
        """
        # Split the postcode in to its inward and outward parts. So for M1 7EP 
        # the inward is "M1" and the outward "7EP"
        parts = re.split("\s", self.postcode.strip())
        if len(parts) > 2:
            return PCValidationCodes.TOO_MANY_PARTS
        elif len(parts) == 1:
            return PCValidationCodes.NO_SPACE
        else:
            self.outward  = parts[0]
            self.inward   = parts[1]


        status = self.test_junk()            # See if it's junk/nonsense
        if status != PCValidationCodes.OK:
            return status

        status = self.test_inward()          # Test the inward part 
        if status != PCValidationCodes.OK:
            return status

        status = self.test_outward()         # Test the outward part
        if status != PCValidationCodes.OK:
            return status

        return PCValidationCodes.OK
        

    def test_junk(self):
        """
        Tests if the postcode is "junk". This is undefined in the specification,
        but is taken to mean that is not two groups of alphanumeric characters
        separated by a single whitespace.
        """
        
        if re.match(r'^\w+\s\w+$', self.postcode):
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.JUNK

    def test_outward(self):
        """
        Tests the outward part of the postcode (e.g. "M" for "M1 7EP"). 
        
        First check it for length. Next determine what kind of 
        inward code it is (as they all have potentially separate rules).
        """
        MinOutwardLength  = 2 # Minumum number of characters (2) e.g. "M1"
        MaxOutwardLength  = 4 # Maximum number of characters (4) e.g. "SW1A"

        if len(self.outward) < MinOutwardLength:
            return PCValidationCodes.OUTWARD_TOO_SHORT
        elif len(self.inward) > MaxOutwardLength:
            return PCValidationCodes.OUTWARD_TOO_LONG
        elif re.match("^[A-Z]{2}\d[A-Z]$", self.outward):   # Is it an AA9A
            return self.test_aa9a_district()
        elif re.match("^[A-Z]{2}\d{1,2}$", self.outward):   # Is it an AA9/AA99
            return self.test_aa9_district()
        elif re.match("^[A-Z]\d{1,2}$", self.outward):      # Is it an A9/A99
            return self.test_a9_district()
        else:
            return PCValidationCodes.OUTWARD_MALFORMED

    def test_inward(self):        
        """
        Tests that the inward part (e.g. "7EP") is correctly formed as per the
        supplied RE
        """
        if re.match('[0-9][ABD-HJLNP-UW-Z]{2}', self.inward):
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.INWARD_MALFORMED
        
    def test_aa9a_district(self):
        """
        Tests for post areas and districts of the form SW1A etc.

        Returns 

            PCValidationCodes.OK if valid else 
            PCValidationCodes.AA9A_MALFORMED
            
        Note
        
            We are testing against the RE as supplied. We could (but this
            is beyond the scope of this exercise) test for things like
            the only allowable districts in the EC area are EC1x - EC4x etc.,
            the only allowable areas as EC, SW, NW etc.
        """
        match = re.match('^([A-PR-UWYZ])([A-HK-Y])([0-9])([ABEHMNPRVWXY])$', self.outward)

        if match:
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.AA9A_MALFORMED
            

    def test_aa9_district(self):
        """
        Test for post areas and districts of the form LS1, LS22 etc.

        Returns 

            PCValidationCodes.OK if valid else 
            PCValidationCodes.AA9_MALFORMED
        """
        SingleDigitDistricts = "BR|FY|HA|HD|HG|HR|HS|HX|JE|LD|SM|SR|WC|WN|ZE".split("|")
        DoubleDigitDistricts = "AB|LL|SO".split("|")
        match = re.match('^([A-PR-UWYZ][A-HK-Y])([0-9]+)$', self.outward)

        if match:
            if match.groups()[0] in SingleDigitDistricts and len(match.groups()[1]) > 1:
                return PCValidationCodes.SINGLE_DIGIT_DISTRICT
            elif match.groups()[0] in DoubleDigitDistricts and len(match.groups()[1]) < 2:
                return PCValidationCodes.DOUBLE_DIGIT_DISTRICT
            else:
                return PCValidationCodes.OK
        else:
            return PCValidationCodes.AA9_MALFORMED

    def test_a9_district(self):
        """
        Test for post areas and districts of the form M1 etc.

        Returns 

            PCValidationCodes.OK if valid else 
            PCValidationCodes.A9_MALFORMED
            
        Note.
            We are testing against the RE as supplied. We could (but this
            is beyond the scope of this exercise) test that it's a valid
            single letter area - i.e. in [B, E, G, L, M, N, S, W].

        """
        match = re.match('^([A-PR-UWYZ])([0-9]+)$', self.outward)
        if match:
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.A9_MALFORMED


    
if __name__ == '__main__':
    
    p = PostCode("M1 7EP")