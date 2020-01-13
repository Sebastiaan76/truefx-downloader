NOTE:
The main download script downloader.py currently doesn't work. The folks at www.truefx.com did a complete site redesign, and as such I'll need to basically re-write this script. Currently time doesn't allow that, so feel free to use this code or parts of it to make your own re-factor!

The Database.py and Candle.py scripts should still be very useful once you have the CSV files downloaded. So that's some consolation :)


# truefx-downloader
This repository contains a number of useful tools to download, transform and import historical FX data from http://www.truefx.com.

These are: 
* downloader.py - use this to download historical data from truefx.com.
* Database.py - use this to import the resulting directory of CSV files into a postgres database
* Candle.py - use this to transform tick data from either CSV or postgres into OHLC data - i.e. candlesticks.

 

## download.py

This script will download selected, or all available historical data from https://www.truefx.com

Some things you will need to do:
1. sign up for an account with www.truefx.com ( it's free )
2. save the script to your preferred location and chmod +755 downloader.py

```
usage: python downloader.py [-h] [-c CURRENCIES] [-y YEARS] [-m MONTHS] [-p PATH] username password

NOTE: username and password must be provided. If no other options are
specified, then all available files will be downloaded to the current working
directory.

positional arguments:
  username              Your www.truefx.com username
  password              Your www.truefx.com password

optional arguments:
  -h, --help            show this help message and exit
  -c CURRENCIES, --currencies CURRENCIES
                        the currencies you want to download. Comma separated
                        without spaces or slashes. The following currencies
                        are supported:AUDJPY,AUDNZD,AUDUSD,CADJPY,CHFJPY,EURCH
                        F,EURGBP,EURJPY,EURUSD,GBPJPY,GBPUSD,NZDUSD,USDCAD,USD
                        CHF,USDJPY
  -y YEARS, --years YEARS
                        the year or years you want downloaded. comma
                        separated, no spaces. i.e. 2017,2018. valid options
                        are 2009 to present year
  -m MONTHS, --months MONTHS
                        Month or months of data to download for given year(s),
                        comma separated, no spaces, 2 decimal spaces i.e.
                        01,02,03 ... 12. 01 thru 12 are valid options
  -p PATH, --path PATH  Path of where you would like the downloaded files.
                        Directories will be created if they don't exist. If
                        not specified, then the current working directory is
                        used e.g /home/john/myfxstuff
   ``` 

example:
`python downloader.py -c AUDUSD -m 03,04 -y 2017,2018 -p /home/joeblogs/mydata/ joeblogs apssword123`

The above would login as joeblogs, download March & April of 2017 & 2018 for AUDUSD to the specified path.
A total of 4 files. They would then be unzipped and the zip files deleted, leaving 4 CSV files. Ready for _Database.py_

_*Note*_: truefx.com uses a Godaddy SSL cert that doesn't seem to be recognized by the CA store used by the python requests
module this tool uses. Hence I've provided the certificate chain in this repo as **gd_bundle-g2-g1.crt**. Alternatively, you can download it directly here:
<https://ssl-ccp.godaddy.com/repository/gd_bundle-g2-g1.crt> . As long as you have that in the working directory, all will be well. Same link is provided in the comments.


## Database.py
This script will take a directory containing TrueFX CSV files, and import them into a Postgres Database.
You'll need to create a blank database called 'fx_data'. The script will create tables etc.

Can you change the name of the database? sure. Just be sure to change all references to 'fx_data' in the script too.

This script will also take a hash of the file, so you can't import a CSV file twice, so if you download more files later, and re-run
the Database.py script to import, it'll just skip the previously imported ones. 

To use, simply edit the details at the bottom of the file in the db_obj = Import(.....) call.

## Candle.py

This script will take a CSV file, or postgres database table of ticks (i.e. what you would have ended up with after running Database.py)
and create a new table of OHLC or Candlestick data for a desired timeframe. The number of ticks that make up the Candle will be used as volume - i.e. tick volume.

To use this tool, simply edit the variables at the bottom where indicated: currency, timeframe and database.
currency should be a string as so: 'EURCHF' or whichever currency you need. timeframe should be an integer representing the number of minutes in the candle - i.e. the timeframe.
Typically 1, 5, 15, 60, 240 min etc and database, you'll need to edit the dictionary values with the appropriate database connection details for your postgres database.


