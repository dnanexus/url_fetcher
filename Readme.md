This app fetches (and uploads) a file from a remote URL. It is
suitable for retrieving datasets from public servers, or data from
your own HTTP/FTP server.

Supported protocols are http, https, and ftp. Here are some example
URLs:

    ENCODE gene annotations from the UCSC genome browser HTTP server:

      http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeGencodeV11/supplemental/gencode.v11.annotation.gtf.gz

    European population variant sites from the 1000 genomes FTP server:

      ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/pilot_data/paper_data_sets/a_map_of_human_variation/exon/snps/CEU.exon.2010_09.sites.vcf.gz

Note that by default, this app will make use of SSD-backed instances.  For very large file transfers (greater than 30 GB), you may find that HDD backed instances provide a slightly more economical, although longer, transfer.
