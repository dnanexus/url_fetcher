import dxpy
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

# Program to download the contents of a URL and upload them into the
# platform as a file object.

def main():
    subprocess.check_call("sudo apt-get install curl --yes --force-yes", shell=True)
    url = job['input']['url']
    subprocess.check_call(["curl", url, "-o", "fetched_from_url"])
    new_file = dxpy.upload_local_file("fetched_from_url")
    job['output'] = {'file': {'$dnanexus_link': new_file.get_id()}}
