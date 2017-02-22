
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

class PostCode:
    """
    Very simple class to contain a postcode and (if supplied) a row_id
    """
    # Take the raw (i.e. extraneous whitespace) re specified by the customer
    # and then clean it up so it can be parsed by re.compile. (Note that
    # although we don't have to compile the regexp, assuming we are likely to
    # be validating millions of postcodes it is significantly more efficient
    # if we do so)
    
    RawREString = r"""(GIR\s0AA) |
    (
        ( ([A-PR-UWYZ][0-9][0-9]?) |
            (([A-PR-UWYZ][A-HK-Y][0-9](?<!(BR|FY|HA|HD|HG|HR|HS|HX|JE|LD|SM|SR|WC|WN|ZE)[0-9])[0-9]) |
             ([A-PR-UWYZ][A-HK-Y](?<!AB|LL|SO)[0-9]) |
             (WC[0-9][A-Z]) |
             (
               ([A-PR-UWYZ][0-9][A-HJKPSTUW]) |
               ([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY])
             )
            )
          )
        \s[0-9][ABD-HJLNP-UW-Z]{2}
        )"""

    REString = re.sub('\s','',RawREString)
    
    # Compile the re for performance...
    
    RE = re.compile(REString)

    def __init__(self, rawtext, row_id=None):
        """
        Parameters:
            raw:    The raw text of the postcode which will be validated
            row_id: The row_id read from the file. Converted to integer if possible
        """
        self.postcode = rawtext
        self.match = PostCode.RE.match(rawtext)
        try:
            self.row_id = int(row_id) # Convert the rowid to integer which will make sorting etc. much faster
        except (ValueError, TypeError):
            self.row_id = None

    def __repr__(self):
        return "{}: {}".format(self.postcode, self.row_id)
    
    def __lt__(self, other): # Required to sort PostCodes in to row_id order
        if self.row_id and other.row_id: # If they both have row_ids
            return self.row_id < other.row_id
        else:
            return self.postcode < other.postcode


