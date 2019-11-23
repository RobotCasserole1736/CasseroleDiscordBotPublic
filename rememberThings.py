from fuzzyResponseParser import *
import os, sys
import re

MEMORY_FILE_NAME = "./things_remembered.txt"

class ThingRememberer():

    def __init__(self):
        pass


    def parse(self, inputString):
        inputString = inputString.lower().strip()
        if(inputString.startswith("Remember that"))

    def storeFact(self, fact):
        fp = open(MEMORY_FILE_NAME, "w")
        


    def recallFact(self, querey):
        fp = open(MEMORY_FILE_NAME, "r")
        