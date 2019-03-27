#!/usr/bin/env python3
import datetime
import argparse
import sys
import os


class Arguments:
    """This Class parses command line arguments and performs a number of checks to ensure valid entries.
    Defaults are created if no optional arguments are provided. Defaults are ALL years, months and currencies"""

    def __init__(self):

        # set defaults - these are used if no optional arguments are provided
        self.currencies = ",".join(['AUDJPY', 'AUDNZD', 'AUDUSD', 'CADJPY', 'CHFJPY', 'EURCHF', 'EURGBP',
                                    'EURJPY', 'EURUSD', 'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY'])
        self.months = ",".join(["{:02d}".format(x) for x in range(1, 13)])
        self.years = ",".join([str(y) for y in range(2009, datetime.datetime.today().year + 1)])
        self.path = "{}/".format(os.getcwd())

        # use argparse to handle command line arguments
        parser = argparse.ArgumentParser(description="NOTE: username and password must be provided. "
                                                     "If no other options are specified, then all available files "
                                                     "will be downloaded to the current working directory.",
                                         epilog="Written by Sebastiaan Stoffels")
        parser.add_argument("username", help="Your www.truefx.com username")
        parser.add_argument("password", help="Your www.truefx.com password")
        parser.add_argument("-c", "--currencies", default=self.currencies, type=str.upper,
                            help="the currencies you want to download. Comma separated without spaces or slashes. "
                                 "The following currencies are supported:"
                                 "AUDJPY,AUDNZD,AUDUSD,CADJPY,CHFJPY,EURCHF,EURGBP,EURJPY,EURUSD,GBPJPY,GBPUSD,"
                                 "NZDUSD,USDCAD,USDCHF,USDJPY")
        parser.add_argument("-y", "--years", default=self.years,
                            help="the year or years you want downloaded. comma separated, no spaces. "
                                 "i.e. 2017,2018. valid options are 2009 to present year")
        parser.add_argument("-m", "--months", default=self.months,
                            help="Month or months of data to download for given year(s), comma separated, "
                                 "no spaces, 2 decimal spaces i.e. 01,02,03 ... 12. 01 thru 12 are valid options")
        parser.add_argument("-p", "--path", default=os.getcwd(),
                            help="Path of where you would like the downloaded files. Directories will be created if "
                                 "they don't exist. If not specified, then the current working directory is used "
                                 "e.g /home/john/myfxstuff")
        self.args = parser.parse_args()

        # required arguments
        self.username = self.args.username
        self.password = self.args.password

        # If optional arguments are provided - check them & override the defaults
        if self.check_subset(self.args.currencies, self.currencies):
            self.currencies = self.args.currencies.split(",")

        self.args.months = ",".join(["{:02d}".format(int(mon)) for mon in self.args.months.split(",")])
        if self.check_subset(self.args.months, self.months):
            self.months = ["{:02d}".format(int(mon)) for mon in self.args.months.split(",")]

        if self.check_subset(self.args.years, self.years):
            self.years = self.args.years.split(",")

        self.path = self.args.path if self.args.path else self.path

        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if self.path[-1] != "/":
            self.path = "{}/".format(self.path)

    def check_subset(self, args, master):
        """Helper function - checks whether arguments given are part of the master list"""
        if set(args.split(",")).issubset(master.split(",")):
            return True
        else:
            sys.exit("Error: Invalid input given. Please ensure valid currencies, months & years are given. "
                     "run command with --help for more guidance")
