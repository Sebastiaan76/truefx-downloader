# truefx-downloader
Python script to download all historical FX data from www.truefx.com

 TrueFX download script

This script will download all available historical data from https://www.truefx.com

Some things you will need to do:
1. sign up for an account with www.truefx.com ( it's free )
2. edit the script to include your username and password in the script 
3. edit the script to ensure files are downloaded to your preferred destination by editing the path - i.e. '/home/<yourlocalusername>/somedirthatexistsalready' 

Once ready to go, simply do:
$ python download.py

I would recommend doing this overnight. there are 15 currencies, 9 years worth of data. So (15 x 12) x 9years = 1620 files @ ~30 - 70Mb each (although 2009 starts in May - so not quite 1620 ). The connection truefx has isn't terribly fast, so you'll be waiting a while. Also, you are looking at 70 - 80Gb of disk space - so might be worth streaming this straight to the NAS, or clearing some space if you intend to download the whole lot.

Unzipped CSV files are ~600Mb each, so bear this in mind if you plan to add to this script to unzip, add to database etc. 

note: if you get a Traceback error regarding SSL Handshake - ensure you have the Go Daddy CA certs installed on your system ( export them from firefox ). If you can't be bothered doing that, you can simply change the urls in the script to be http instead of https - but then your password will be sent in the clear.

TODOs:
1. make it possible to select only certain currencies
2. make it possible to select on certain years
3. more robust error checking ( ok, some checking )

This script is pretty hacky. If the truefx.com folk change things on the website html, this will likely break. But as-is - it works fine.
