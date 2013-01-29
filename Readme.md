This app will download a remote file using the aria2c utility and then upload it into the platform.  The job log will display progress of the transfer and any connection error will be reported.

Inputs
------

* **URL**:  A string containing the full URL of the file to be fetched into the system
* **Output Name**: The resulting file object in the platform will have this name.  This is optional.  If not specified the name will be derived from the URL.
* **Tags**: An array of strings to label the resulting object with.  Objects can be searched based on their tags.  One example of using tags would be to upload all files from a given patient tagged with their anonymized ID.
* **Properties**:  A hash of key-value pairs describing the file.  For instance "source":"blood".

Outputs
-------

* **File**:  A file object representing the newly uploaded file in the DNAnexus platform that has been tagged with given metadata.
