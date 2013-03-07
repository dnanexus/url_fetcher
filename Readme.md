This app fetches (and uploads) a file from a remote URL. It is suitable for retrieving datasets from public servers, or data from your own HTTP/FTP server.

Supported protocols are http, https, and ftp. Here are some example URLs:

    ENCODE gene annotations from the UCSC genome browser HTTP server:

      http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeGencodeV11/supplemental/gencode.v11.annotation.gtf.gz


    European population variant sites from the 1000 genomes FTP server:

      ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/pilot_data/paper_data_sets/a_map_of_human_variation/exon/snps/CEU.exon.2010_09.sites.vcf.gz


Inputs
------

* **URL**: The URL to fetch data from.
* **Output name**: The name of the resulting file (optional; if not provided, the file will be called after the last part of the URL).

Advanced Inputs
---------------

* **Tags**: A set of tags (string labels) that will be added to the resulting file object. (You can use tags and properties to better describe and organize your data).
* **Properties**: A set of properties (key/value pairs) that will be added to the resulting file object. (You can use tags and properties to better describe and organize your data).

Outputs
-------

* **File**: The resulting file fetched from the URL.
