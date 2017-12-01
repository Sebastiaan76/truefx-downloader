import requests
from bs4 import BeautifulSoup
from clint.textui import progress
import sys
import os


def download_file(url, download_path):
    """this function downloads the files - change the path below to your preferred full path
    make sure you have permission to write to the directory you choose"""
    local_filename = download_path + url.split('/')[-1]
    print('downloading: {}'.format(url))
    r = requests.get(url, stream=True)

    with open(local_filename, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()
    return


def traverse(html, session, download_path):
    """this function traverses the truefx download folders one by one until we find the zip files we want
    once it finds them - we call the download_file() function"""
    for link in html.find_all('a'):
        if 'color:#CCC;' not in str(link.get_attribute_list('style')) and 'folderbg' in str(link.get_attribute_list('class')):
            next_level = 'https://www.truefx.com/{}'.format(str(link.get("href")))
            response_next = session.get(next_level)
            next_html = BeautifulSoup(response_next.content, 'html.parser')

            # recursive call
            traverse(next_html, session, download_path)

        elif 'dl-zip' in str(link.get_attribute_list('class')):
            download_file('https://www.truefx.com' + str(link.get('href')), download_path)
    return


def find_files(username, password, download_path):
    """this function establishes the session and parses the main download page. We then call traverse()"""
    payload = {'USERNAME': '{}'.format(username), 'PASSWORD': '{}'.format(password)}
    url = 'https://www.truefx.com/?page=downloads'
    with requests.Session() as session:
        session.post('https://www.truefx.com/?page=loginz', data=payload)
        response = session.get(url)
        html = BeautifulSoup(response.content, 'html.parser')
        traverse(html, session, download_path)
    return

if __name__ == "__main__":
    def main():
        if len(sys.argv) <=2:
            print("\nusage: python download.py <truefx-username> <password> [save path]\nIf no save path given, current directory is used")
            return 1
        elif len(sys.argv) == 3:
            path = "{}/".format(os.getcwd())
            find_files(sys.argv[1], sys.argv[2], path)
        elif len(sys.argv) == 4:
            if not os.path.exists(sys.argv[3]):
                os.mkdir(sys.argv[3])
            if sys.argv[3][-1] != '/':
                path = "{}/".format(sys.argv[3])
            else:
                path = sys.argv[3]
            find_files(sys.argv[1], sys.argv[2], path)
main()