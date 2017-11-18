import requests
from bs4 import BeautifulSoup
from clint.textui import progress

# this function downloads the files - change the path below to your preferred full path
# make sure you have permission to write to the directory you choose
def download_file(url):
    local_filename = '/home/seb-i3/truefx/' + url.split('/')[-1]
    print('downloading: {}'.format(url))
    r = requests.get(url, stream=True)

    with open(local_filename, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

    return local_filename

# this function traverses the truefx download folders one by one until we find the zip files we want
# once it finds them - we call the download_file() function
def traverse(html, session):
    for link in html.find_all('a'):
        if 'color:#CCC;' not in str(link.get_attribute_list('style')) and 'folderbg' in str(link.get_attribute_list('class')):
            next_level = 'https://www.truefx.com/' + str(link.get("href"))
            response_next = session.get(next_level)
            next_html = BeautifulSoup(response_next.content, 'html.parser')

            # recursive call
            traverse(next_html, session)

        elif 'dl-zip' in str(link.get_attribute_list('class')):
            download_file('https://www.truefx.com' + str(link.get('href')))

    return

# this function establishes the session and parses the main download page. We then call traverse()
def find_files(url):
    # Put your truefx username and password in place of <username> and <password> leave the ' ' quotes
    payload = {'USERNAME': '<username>', 'PASSWORD': '<password>'}

    with requests.Session() as session:
        session.post('https://www.truefx.com/?page=loginz', data=payload)
        response = session.get(url)
        html = BeautifulSoup(response.content, 'html.parser')
        traverse(html, session)
    return


# Call the find_files function to start things off
find_files('https://www.truefx.com/?page=downloads')
