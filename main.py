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
    if file_name == '':
        file_name = url
    file_folder = dxpy.DXJob(job["id"]).describe()['folder']
    placeholder_dxfile = dxpy.new_dxfile(name = file_name,
                                         folder = file_folder,
                                         parents = True,
                                         project = dxpy.PROJECT_CONTEXT_ID)
    try:
        subprocess.check_call(["aria2c", url, "-o", "fetched_from_url", "-x6", "-s6", "-j6", "--check-certificate=false"])
        print "Uploading file into project " + dxpy.PROJECT_CONTEXT_ID + " (from dxpy.PROJECT_CONTEXT_ID)"
        new_file = dxpy.upload_local_file("fetched_from_url",
                                          keep_open=True,
                                          use_existing_dxfile = placeholder_dxfile)
        if 'additional_types' in job['input']:
            new_file.add_types([x.strip() for x in job['input']['additional_types'].split(",")])
        if 'output_name' in job['input']:
            if job['input']['output_name'] != '':
                new_file.rename(job['input']['output_name'])
        new_file.close(block=True)
    except:
        placeholder_dxfile.remove()
        raise
    job['output'] = {'file': {'$dnanexus_link': new_file.get_id()}}
