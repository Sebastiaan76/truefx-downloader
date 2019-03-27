#!/usr/bin/env python3
import Arguments
import requests
from bs4 import BeautifulSoup
from clint.textui import progress
import zipfile
import os


class Download:
    """This class handles all the downloading of data from truefx.com. It takes an Arguments object to ascertain
    what username, password and files it needs to download, and to where.
    You need this CA bundle to avoid ssl errors: https://ssl-ccp.godaddy.com/repository/gd_bundle-g2-g1.crt"""
    def __init__(self, args_obj):
        self.username = args_obj.username
        self.password = args_obj.password
        self.currencies = args_obj.currencies
        self.years = args_obj.years
        self.months = args_obj.months
        self.path = args_obj.path
        self.html = None
        self.session = None
        self.file_count = (len(self.months) * len(self.years)) * len(self.currencies)
        self.download_counter = 0
        self.file_names = []

    def open_session(self):
        """this function establishes the session and parses the main download page. We then call traverse()"""
        payload = {'USERNAME': '{}'.format(self.username), 'PASSWORD': '{}'.format(self.password)}
        url = 'https://www.truefx.com/?page=downloads'
        with requests.Session() as self.session:
            self.session.verify = 'gd_bundle-g2-g1.crt'
            self.session.post('https://www.truefx.com/?page=loginz', data=payload)
            response = self.session.get(url)
            self.html = BeautifulSoup(response.content, 'html.parser')
            self.traverse()
        return

    def traverse(self):
        """this function traverses the truefx download folders one by one until we find the zip files we want
        once it finds them - we call the download_file() function"""
        for link in self.html.find_all('a'):
            if 'color:#CCC;' not in str(link.get_attribute_list('style')) and 'folderbg' in str(link.get_attribute_list('class')):
                next_level = 'https://www.truefx.com/{}'.format(str(link.get("href")))
                response_next = self.session.get(next_level)
                self.html = BeautifulSoup(response_next.content, 'html.parser')

                # recursive call
                if not self.download_counter == self.file_count:
                    self.traverse()
                else:
                    return

            elif 'dl-zip' in str(link.get_attribute_list('class')):
                for cur in self.currencies:
                    filename = link.get('href').split('/')[-1].split('.')[0].split('-')
                    if cur in str(link.get('href')) and filename[1] in self.years and filename[2] in self.months:
                        self.download_file('https://www.truefx.com' + str(link.get('href')))

        if self.download_counter == self.file_count:
            print("Finished! All files downloaded. Downloaded {} files.".format(self.download_counter))
        return

    def download_file(self, url):
        """this function downloads the files - change the path below to your preferred full path
        make sure you have permission to write to the directory you choose"""
        self.download_counter += 1
        local_filename = self.path + url.split('/')[-1]
        self.file_names.append(local_filename)
        print('downloading: {}'.format(url))
        r = requests.get(url, verify='gd_bundle-g2-g1.crt', stream=True)

        with open(local_filename, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return

    def unzip_files(self):
        for file in self.file_names:
            with zipfile.ZipFile(file, 'r') as z:
                z.extractall(self.path)
                print("unzipped: {}".format(file))

    def remove_zips(self):
        for file in self.file_names:
            os.remove(file)
            print("deleted zip file: {}".format(file))


if __name__ == "__main__":

    args = Arguments.Arguments()
    dl = Download(args)
    dl.open_session()

    # comment out the below if you don't want to unzip the files programatically
    dl.unzip_files()
    dl.remove_zips()

