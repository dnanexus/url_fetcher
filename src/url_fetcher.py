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
import urllib
import glob

import dx_utils

SAFETY_FACTOR = 0.9
B_IN_MB = 1024.0 * 1024.0
INSTANCE_SIZES = {'aws': [('mem1_ssd1_x4', 75000), ('mem1_ssd1_x8', 155000),
                          ('mem1_ssd2_x4', 318000)],
                  'azure': [('azure:mem2_ssd1_x2', 14000), ('azure:mem2_ssd1_x16', 114000),
                            ('azure:mem3_ssd1_x16', 229000)]}


class NoPasswdPromptURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        raise RuntimeError('This url is prompting for a username and password.')


def _get_free_space():
    st = os.statvfs('.')
    return st.f_bavail * st.f_frsize


@dxpy.entry_point('download_url')
def download_url(url, tags=None, properties=None, output_name=None):
    url = url.strip() # assume no URL has end/start whitespaces
    with dx_utils.cd():
        ariaCmd = ["aria2c", url, "--user-agent", "Mozilla/5.0", "-x6", "-j6", "--check-certificate=false", "--file-allocation=none"]
        ariaCmd_str = " ",join(ariaCmd)
        print "Executing:\n{0}".format(ariaCmd_str)
        p = subprocess.Popen(
            ariaCmd,
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE
        )

        stdout, stderr = p.communicate()

        if p.returncode != 0:
            status = p.returncode

            print " ".join([
                "aria2c produced exit status", str(status),
                "with output:\n", stdout,
                "on URI", url])

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
                if "No route to host" in stdout:
                    statusMessage = "No route to host"
                elif "Failed to establish connection" in stdout:
                    statusMessage = "Failed to establish connection"
                elif "Domain name not found" in stdout:
                    statusMessage = "Domain name not found"
                else:
                    statusMessage = "Failed to fetch file, please check URL validity"

            raise dxpy.AppError(statusMessage)

        print "Download of file completed successfully.  Uploading file into platform..."

        fl = glob.glob("*")
        if len(fl) != 1:
            raise dxpy.AppError("Expected exactly one file to be downloaded.  Saw {0}.\n{1}".format(len(fl), "\n".join(fl)))

        file_name = fl[0]

        fh = dxpy.upload_local_file(file_name, keep_open=True)

        if output_name is not None and output_name != "":
            fh.rename(output_name)

        if tags is not None:
            fh.add_tags(tags)
        if properties is not None:
            fh.set_properties(properties)

        fh.close()

    output = {}
    output["file"] = dxpy.dxlink(fh.get_id())

    return output


def _get_platform(instance_type):
    if instance_type.find('azure') >= 0:
        platform = 'azure'
    else:
        platform = 'aws'

    return platform


def _find_appropriate_instance_type(file_size, instance_type):
    platform = _get_platform(instance_type)

    for instance, instance_size in INSTANCE_SIZES[platform]:
        if file_size < SAFETY_FACTOR * instance_size:
            return instance

    return None


@dxpy.entry_point('main')
def main(url, tags=None, properties=None, output_name=None):
    current_instance_type = dxpy.describe(dxpy.JOB_ID)['instanceType']
    # Get the disk free space
    free_space = _get_free_space() / B_IN_MB
    # Get the filesize
    try:
        url_opener = NoPasswdPromptURLopener()
        url_info = url_opener.open(url).info()

        file_size = int(url_info.getheaders('Content-Length')[0])        
        file_size /= B_IN_MB
    except IndexError:
        # If we are not able to determine the size from the Content-Length
        # header, just assume it is the largest supported size.
        print "Could not determine file of size to fetch, so assuming it's very big!"
        file_size = INSTANCE_SIZES[_get_platform(current_instance_type)][-1][1] * SAFETY_FACTOR - 1

    # Now if the filesize is within 90% of the current free space, launch on
    # a larger instance.
    if file_size > free_space * SAFETY_FACTOR:
        instance_type = _find_appropriate_instance_type(file_size, current_instance_type)
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
