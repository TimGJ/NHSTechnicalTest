#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 15:26:44 2017

Simple wrapper to perform all three tests

@author: Tim Greening-Jackson
"""
import logging
import NHSTechnicalTestPart1
import NHSTechnicalTestPart2
import NHSTechnicalTestPart3

if __name__ == '__main__':
    logging.info("Beginning tests")
    NHSTechnicalTestPart1.PerformTests()
    NHSTechnicalTestPart2.PerformTests()
    NHSTechnicalTestPart3.PerformTests()
    logging.info("Tests completed")
    