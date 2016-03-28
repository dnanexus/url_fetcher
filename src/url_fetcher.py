#!/usr/bin/env python
#
# Copyright (C) 2013 DNAnexus, Inc.
#
# This file is part of url_fetcher.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import os
import dxpy
import subprocess
import urlparse
import random
import time
import urllib

SAFETY_FACTOR = 0.9
B_TO_MB = 1024.0 * 1024.0
INSTANCE_SIZES = [('mem1_ssd1_x4', 75000), ('mem1_ssd1_x8', 155000),
                  ('mem3_ssd2_x4', 750000)]


def _get_free_space():
    st = os.statvfs('.')
    return st.f_bavail * st.f_frsize


@dxpy.entry_point('download_url')
def download_url(url, tags=None, properties=None, output_name=None):
    url_path = urlparse.urlparse(url).path
    file_name = os.path.basename(url_path)
    if file_name == '':
        file_name = url_path
    if file_name == '':
        file_name = url

    ariaCmd = ["aria2c", url, "-o", "fetched_from_url", "-x6", "-s6", "-j6", "--check-certificate=false", "--file-allocation=none"]

    print "Executing: ", " ".join(ariaCmd)


    p = subprocess.Popen(ariaCmd, stdout=subprocess.PIPE)

    exited = False

    report = ""
    report_file = p.stdout
    while(p.poll() == None):
        report_file.flush()
        line = report_file.readline()
        if line != "":
            print line.rstrip()
            report += line
        else:
            time.sleep(0.5)

    if p.returncode != 0:
        status = p.returncode

        print " ".join(["aria2c produced exit status", str(status), "with output:\n", report, "on URI", url])

        statusMessage = {
            2: "Timeout error",
            3: "Resource not found",
            6: "Network problem",
            8: "Resume not supported",
            9: "Ran out of disk space",
            19: "Name resolution failed",
            21: "FTP command failed",
            22: "Unexpected or corrupt HTTP response header",
            23: "Excessive redirection",
            24: "Authorization failure",
            25: "Parse failure on bencoded file"
            }.get(status, "")

        if statusMessage == "":
            if "No route to host" in report:
                statusMessage = "No route to host"
            elif "Failed to establish connection" in report:
                statusMessage = "Failed to establish connection"
            elif "Domain name not found" in report:
                statusMessage = "Domain name not found"
            else:
                statusMessage = "Failed to fetch file, please check URL validity"

        raise dxpy.AppError(statusMessage)

    print "Download of file completed successfully.  Uploading file into platform..."

    fh = dxpy.upload_local_file("fetched_from_url", keep_open=True)

    if output_name != None and output_name != "":
        fh.rename(output_name)
    else:
        fh.rename(file_name)

    if tags != None:
        fh.add_tags(tags)
    if properties != None:
        fh.set_properties(properties)

    fh.close()

    output = {}
    output["file"] = dxpy.dxlink(fh.get_id())

    return output


def _find_appropriate_instance_type(file_size):
    for instance, instance_size in INSTANCE_SIZES:
        if file_size < SAFETY_FACTOR * instance_size:
            return instance

    return None


@dxpy.entry_point('main')
def main(url, tags=None, properties=None, output_name=None):
    # Get the filesize
    file_size = int(urllib.urlopen(url).info().getheaders('Content-Length')[0])
    # Get the disk free space
    free_space = _get_free_space()

    # Now if the filesize is within 90% of the current free space, launch on
    # a larger instance.
    if file_size > free_space * SAFETY_FACTOR:
        file_size /= B_TO_MB
        instance_type = _find_appropriate_instance_type(file_size)
        if not instance_type:
            msg = 'This looks like a very big file - {0:0.1f} GB.  Try a larger instance.'
            msg = msg.format(file_size / 1024.0)
            raise dxpy.AppError(msg)

        job_input = {'url': url, 'tags': tags, 'properties': properties, 'output_name': output_name}
        job = dxpy.new_dxjob(job_input, 'download_url', instance_type=instance_type)

        output = {'file': job.get_output_ref('file')}
    else:
        output = download_url(url, tags, properties, output_name)

    return output

dxpy.run()
