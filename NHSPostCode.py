
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
   So all UK postcodes can be validated, although there will be false positives.
   These would include various nonexistent postcodes, provided they are
   legal within the scope of the re definition,
   
5. It doesn't correctly match some postcodes (i.e. allows false positives).

   A. Only postcode areas BL, BS, CM, CR, FY, HA, PR, SL, SS have a district 0,
      but the re will allow e.g. M0.

   B. Similarly it will allow things like "M1A 9AA"

   C. Despite appearing to handle it, the re also allows the WC area to 
      have districts which do not have a trailing letter - e.g. it allows 
      WC4 9PP. All postcodes in the WC area are of the form WC9A 9AA.

   D. There are only certain single-letter postcode areas allowed,
      [B, E, G, L, M, N, S, W], the RE does not enforce this.

   It would be possible to extend the RE to cope with all these cases, 
   but that would add to its complexity, reduce its performance and 
   still not guarantee to catch all invalid postcodes. 
   
    
@author: Tim Greening-Jackson
"""
import re
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
    UNKNOWN                = enum.auto()
    OUTWARD_MALFORMED      = enum.auto()
    OUTWARD_AA9A_MALFORMED = enum.auto()
    OUTWARD_AA9_MALFORMED  = enum.auto()
    OUTWARD_A9_MALFORMED   = enum.auto()
    INWARD_MALFORMED       = enum.auto()
    INCORRECT_GROUPING     = enum.auto()
    JUNK                   = enum.auto()
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
        try:                                        # Convert the row_id to integer
            self.row_id = int(row_id)               # if it is amenable, as this will
        except (TypeError, ValueError):             # be much easier and faster for
            self.row_id = None                      # searching/sorting etc.  
            

        # Split the postcode in to its inward and outward groups, so for M1 7EP 
        # the outward is "M1" and the inward "7EP". If there aren't exactly
        # two groups then reject the postcode (no need to do the re.match())
        
        groups = re.split("\s", self.postcode.strip())

        if len(groups) != 2:
            self.outward  = None                    # Shouldn't need to set these
            self.inward   = None                    # to None but probably wiser
            self.match    = None                    # in case someone refers to them elsewhere.
            self.status   = PCValidationCodes.INCORRECT_GROUPING
        else:
            self.outward  = groups[0]
            self.inward   = groups[1]           
            self.match    = PostCode.RE.match(rawtext) 
            if self.match:                          # Clean match against RE
                self.status   = PCValidationCodes.OK   
            else:                                   # Match failed
                if analyse:                         # Do we test to see why it failed?...
                    self.status = self.Analyse()
                else:                               # ... or just put it down as UNKNOWN?
                    self.status = PCValidationCodes.UNKNOWN
            

    def __repr__(self):
        return "{}: {}".format(self.postcode, self.row_id)
    
    def __lt__(self, other):                       # Required to sort PostCodes in to row_id order
        if self.row_id and other.row_id:           # If they both have row_ids
            return self.row_id < other.row_id
        else:                                      # But we might also want to sort postcodes with no row_id
            return self.postcode < other.postcode

    def Analyse(self):
        """
        Analyses a postcode for validation.
        
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

        status = self.ValidateCharacters()       # See if it's junk/nonsense
        if status != PCValidationCodes.OK:
            return status

        status = self.ValidateInward()          # Test the inward part 
        if status != PCValidationCodes.OK:
            return status

        status = self.ValidateOutward()         # Test the outward part
        if status != PCValidationCodes.OK:
            return status

        return PCValidationCodes.OK
        

    def ValidateCharacters(self):
        """
        Tests if the postcode is "junk". This is undefined in the specification,
        but is taken to mean that is not two groups of alphanumeric characters
        separated by a single whitespace.
        """
        
        if re.match(r'^\w+\s\w+$', self.postcode):
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.JUNK

    def ValidateOutward(self):
        """
        Tests the outward part of the postcode (e.g. "M" for "M1 7EP"). 
        
        Determine what kind of outward code it is 
        (as they all have potentially separate rules).
        """
        if re.match("^[A-Z]{2}\d[A-Z]$", self.outward):   # Is it an AA9A
            return self.ValidateOutwardAA9A()
        elif re.match("^[A-Z]{2}\d{1,2}$", self.outward): # Is it an AA9/AA99
            return self.ValidateOutwardAA9()
        elif re.match("^[A-Z]\d{1,2}$", self.outward):    # Is it an A9/A99
            return self.ValidateOutwardA9()
        else:
            return PCValidationCodes.OUTWARD_MALFORMED    # Don't know what it is

    def ValidateInward(self):        
        """
        Tests that the inward part (e.g. "7EP") is correctly formed as per the
        supplied RE
        """
        if re.match('[0-9][ABD-HJLNP-UW-Z]{2}', self.inward):
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.INWARD_MALFORMED
        
    def ValidateOutwardAA9A(self):
        """
        Tests for post areas and districts of the form SW1A etc.

        Returns 

            PCValidationCodes.OK if valid else 
            PCValidationCodes.OUTWARD_AA9A_MALFORMED
            
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
            return PCValidationCodes.OUTWARD_AA9A_MALFORMED
            

    def ValidateOutwardAA9(self):
        """
        Test for post areas and districts of the form LS1, LS22 etc.

        Returns 

            PCValidationCodes.OK if valid else
            PCValidationCodes.SINGLE_DIGIT_DISTRICT if a single digit district has double digits
            PCValidationCodes.DOUBLE_DIGIT_DISTRICT if a double digit district has a single digit
            PCValidationCodes.OUTWARD_AA9_MALFORMED

        Note.
            We are testing against the RE as supplied. We could (but this
            is beyond the scope of this exercise) test for areas which
            are allowed a zero districts etc.
        """
        SingleDigitDistricts = "BR|FY|HA|HD|HG|HR|HS|HX|JE|LD|SM|SR|WC|WN|ZE".split("|")
        DoubleDigitDistricts = "AB|LL|SO".split("|")
        match = re.match('^([A-PR-UWYZ][A-HK-Y])([0-9]+)$', self.outward)

        # Some areas e.g. AB can only have double digit districts e.g. AB23
        # whereas others e.g. FY can only have single digits. So if the pattern
        # matches then check that's OK and if so return OK. 
        #
        # If it doesn't match then by definition it's malformed.
        if match:
            if match.groups()[0] in SingleDigitDistricts and len(match.groups()[1]) > 1:
                return PCValidationCodes.SINGLE_DIGIT_DISTRICT
            elif match.groups()[0] in DoubleDigitDistricts and len(match.groups()[1]) < 2:
                return PCValidationCodes.DOUBLE_DIGIT_DISTRICT
            else:
                return PCValidationCodes.OK
        else:
            return PCValidationCodes.OUTWARD_AA9_MALFORMED

    def ValidateOutwardA9(self):
        """
        Test for post areas and districts of the form M1 etc.

        Returns 

            PCValidationCodes.OK if valid else 
            PCValidationCodes.OUTWARD_A9_MALFORMED
            
        Note.
            We are testing against the RE as supplied. We could (but this
            is beyond the scope of this exercise) test that it's a valid
            single letter area - i.e. in [B, E, G, L, M, N, S, W].
            
            This is a very simple check against a simple RE as specified.

        """
        match = re.match('^([A-PR-UWYZ])([0-9]+)$', self.outward)
        if match:
            return PCValidationCodes.OK
        else:
            return PCValidationCodes.OUTWARD_A9_MALFORMED


    
if __name__ == '__main__':
    
    pass