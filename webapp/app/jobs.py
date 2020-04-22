import time
import re
import os
import uuid


# def fix_bad_file_name(file_name):
#     file_name_extension = re.search(r"(\..*)$", file_name).group(1)
#     file_name = str(uuid.uuid1().int)
#     return "unknown_name_" + file_name + file_name_extension


def run_benford_job(directory_name):
    print(directory_name)
    time.sleep(1)



# def get_text_job(page_url):
#     """
#         Request given page and extract text
#     """
#     directory_name = "AAAA"
#
#     response = requests.get(page_url).text
#     # create a new bs4 object from the html data loaded
#     soup = BeautifulSoup(response, 'html.parser')
#
#     # remove all javascript and stylesheet code
#     for script in soup(["script", "style"]):
#         script.extract()
#     # get text
#     text = soup.get_text()
#     # break into lines and remove leading and trailing space on each
#     lines = (line.strip() for line in text.splitlines())
#     # break multi-headlines into a line each
#     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#     # drop blank lines
#     text = '\n'.join(chunk for chunk in chunks if chunk)
#
#     if not os.path.exists(directory_name):
#         os.makedirs(directory_name)
#
#     save_path = os.path.join(f'{directory_name}/' + "text.txt")
#     with open(save_path, 'w', encoding="utf-8") as f:
#         f.write(text)
