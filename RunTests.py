#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 15:26:44 2017

Simple wrapper to perform all three sets of tests.

Syntax:
    
    $ python3 RunTests.py --logfile=logfile --

@author: Tim Greening-Jackson
"""
import logging
import sys
import argparse

import NHSTechnicalTestPart1
import NHSTechnicalTestPart2
import NHSTechnicalTestPart3

def ParseArguments():
    """
    Parses the command line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(description="Perform NHS Digital Technical Tests")
    parser.add_argument("-l", "--logfile", help="Logfile")
    parser.add_argument("-i", "--input",   help="Input postcode data", default="import_data.csv")
    parser.add_argument("-m", "--matched", help="Output matched/validated data", default="succeeded_validation.csv")
    parser.add_argument("-e", "--error",   help="Output unmatched/invalid data", default="failed_validation.csv")
    parser.add_argument("-p", "--parts",   help="Parts of tests to run", type = int, nargs = '+', choices = [1,2,3], default=[1,2,3])
    return parser.parse_args()
    
if __name__ == '__main__':
    args = ParseArguments()
    if args.logfile:
        logging.basicConfig(filename = args.logfile, level = logging.DEBUG, 
                    format = '%(asctime)s:%(levelname)s:%(message)s')
    else:        
        logging.basicConfig(stream = sys.stdout, level = logging.DEBUG, 
                    format = '%(asctime)s:%(levelname)s:%(message)s')


    logging.info("Beginning tests")
    if 1 in args.parts:
        NHSTechnicalTestPart1.PerformTests()
    if 2 in args.parts:
        NHSTechnicalTestPart2.PerformTests(InputFileName   = args.input,
                                           ErrorFileName   = args.error)
    if 3 in args.parts:
        NHSTechnicalTestPart3.PerformTests(InputFileName   = args.input,
                                           SuccessFileName = args.matched, 
                                           ErrorFileName   = args.error)
    logging.info("Tests completed")
    