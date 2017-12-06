# truefx-downloader
Python script to download all historical FX data from www.truefx.com

 TrueFX download script and
 Bulk Import script

download.py

This script will download selected, or all available historical data from https://www.truefx.com

Some things you will need to do:
1. sign up for an account with www.truefx.com ( it's free )
2. save the script to your preferred location and chmod +755 download.py

download.py takes a number of required and optional commandline arguments

Usage: ./download.py truefx-username truefx-password [download-path] [currency1,currency2,... year1,year2,... month1,month2,...]

1. You must provide a truefx username and password at a minimum. This will download all available data to the current working directory - use this if you want everything
2. Optionally, you can provide a preferred download path in the format: '/some/path' note the lack of trailing '/'
3. If you have given a full path, you can then also specify specific currencies, and/or years and/or months

Examples:

$ ./downloader.py JohnUser Mypassword

will download everything to current working directory


$./downloader.py JohnUser Mypassword /home/JohnUser/Mydir

Will download everything to Mydir


$./downloader.py JohnUser Mypassword /home/JohnUser USDJPY,AUDUSD

will download only USDJPY and AUDUSD. But will get all years/months available


$.downloader.py JohnUser Mypassword /home/JohnUser USDJPY,AUDUSD 2017,2016 03,04

will download only USDJPY and AUDUSD for March & April of 2016 and 2017

spaces between the options, but no spaces between comma separated items, i.e. AUDUSD,USDJPY and not AUDUSD, USDJPY.

If you are starting from scratch and wanting to download everything truefx have, I would recommend doing this overnight. there are 15 currencies, 9 years worth of data. So (15 x 12) x 9years = 1620 files @ ~30 - 70Mb each (although 2009 starts in May - so not quite 1620 ). The connection truefx has isn't terribly fast, so you'll be waiting a while. Also, you are looking at 70 - 80Gb of disk space - so might be worth streaming this straight to the NAS, or clearing some space if you intend to download the whole lot.

Unzipped CSV files are ~100 to 600Mb each, so bear this in mind if you plan to add to this script to unzip, add to database etc. 

note: if you get a Traceback error regarding SSL Handshake - ensure you have the Go Daddy CA certs installed on your system ( export them from firefox ). If you can't be bothered doing that, you can simply change the urls in the script to be http instead of https - but then your password will be sent in the clear.

This script is pretty hacky. If the truefx.com folk change things on the website html, this will likely break. But as-is - it works fine.

Bulk-insert.py

This script will take a dir with the resulting CSV files (once you've unzipped them) and load a Postgres Database with the tick data. 
You'll need to create the database & user first.
