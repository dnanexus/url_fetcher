import dxpy
import subprocess
import logging
import urlparse
import os

logging.basicConfig(level=logging.DEBUG)

# Program to download the contents of a URL and upload them into the
# platform as a file object.

def main():
    url = job['input']['url']
    url_path = urlparse.urlparse(url).path
    file_name = os.path.basename(url_path)
    if file_name == '':
        file_name = url_path
    subprocess.check_call(["curl", url, "-o", "fetched_from_url"])
    print "Uploading file into project " + dxpy.PROJECT_CONTEXT_ID + " (from dxpy.PROJECT_CONTEXT_ID)"
    new_file = dxpy.upload_local_file("fetched_from_url", project = dxpy.PROJECT_CONTEXT_ID)
    new_file.rename(file_name)
    job['output'] = {'file': {'$dnanexus_link': new_file.get_id()}}
