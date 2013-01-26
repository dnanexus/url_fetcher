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

@dxpy.entry_point('main')
def main(url, tags=None, properties=None, output_name=None):

    url_path = urlparse.urlparse(url).path
    file_name = os.path.basename(url_path)
    if file_name == '':
        file_name = url_path
    if file_name == '':
        file_name = url

    ariaCmd = " ".join(["aria2c", url, "-o", "fetched_from_url", "-x6", "-s6", "-j6", "--check-certificate=false"])

    print "executing: ", ariaCmd


    p = subprocess.Popen(ariaCmd, shell=True, stdout=subprocess.PIPE)

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
            2: "time out error",
            3: "resource not found",
            6: "network problem",
            8: "resume not supported",
            9: "ran out of disk space",
            19: "name resolution failed",
            21: "FTP command failed",
            22: "unexpected or corrupt HTTP response header",
            23: "excessive redirection",
            24: "authorization failure",
            25: "parse failure on bencoded file"
            }.get(status, "")

        if statusMessage == "":
            if "No route to host" in report:
                statusMessage = "No route to host"
            elif "Failed to establish connection" in report:
                statusMessage = "failed to eastablish connection"
            elif "Domain name not found" in report:
                statusMessage = "domain name not found"
            else:
                statusMessage = "failed to fetch file, please check URL validity"

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

dxpy.run()
