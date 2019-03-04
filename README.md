# arxiv2remarkable.py

This script makes it as easy to get a PDF on your reMarkable from any of the 
following sources:

- an arXiv url (either ``arxiv.org/abs/...`` or ``arxiv.org/pdf/...``)
- a url to a PDF file
- a local file.

The script takes the source and:

1. Downloads it if necessary
2. Removes the arXiv timestamp
3. Crops the pdf to remove unnecessary borders
4. Shrinks the pdf file to reduce the filesize
5. Generates a nice filename based on author/title/year of the paper (arXiv 
   only)
6. Uploads it to your reMarkable using ``rMapi``.

Optionally, you can download a paper but not have it uploaded to the 
reMarkable using the ``-n`` switch. Also, the ``--filename`` parameter to the 
script can be used to provide an explicit filename for on the reMarkable.

Here's the full help of the script:

```bash
usage: arxiv2remarkable.py [-h] [-v] [-n] [-d] [--filename FILENAME]
                           [--rmapi RMAPI] [--pdfcrop PDFCROP] [--pdftk PDFTK]
                           [--gs GS]
                           input

positional arguments:
  input                url to an arxiv paper, url to pdf, or existing pdf file

optional arguments:
  -h, --help           show this help message and exit
  -v, --verbose        be verbose (default: False)
  -n, --no-upload      don't upload to the reMarkable, save the output in
                       current working dir (default: False)
  -d, --debug          debug mode, doesn't upload to reMarkable (default:
                       False)
  --filename FILENAME  Filename to use for the file on reMarkable (default:
                       None)
  --rmapi RMAPI        path to rmapi executable (default: rmapi)
  --pdfcrop PDFCROP    path to pdfcrop executable (default: pdfcrop)
  --pdftk PDFTK        path to pdftk executable (default: pdftk)
  --gs GS              path to gs executable (default: gs)
```

And here's an example with verbose mode enabled that shows everything the 
script does:
```bash
$ python arxiv2remarkable.py -v https://arxiv.org/abs/1811.11242
2019-02-03 18:11:41.816 | INFO     | __main__:download_url:106 - Downloading file at url: https://arxiv.org/pdf/1811.11242v1.pdf
2019-02-03 18:11:46.833 | INFO     | __main__:get_page_with_retry:92 - Downloading url: https://arxiv.org/pdf/1811.11242v1.pdf
2019-02-03 18:11:46.835 | INFO     | __main__:get_paper_info:194 - Getting paper info from arXiv
2019-02-03 18:11:47.496 | INFO     | __main__:get_page_with_retry:92 - Downloading url: https://arxiv.org/abs/1811.11242v1
2019-02-03 18:11:47.508 | INFO     | __main__:generate_filename:206 - Generating output filename
2019-02-03 18:11:47.508 | INFO     | __main__:dearxiv:114 - Removing arXiv timestamp
2019-02-03 18:11:49.221 | INFO     | __main__:crop_pdf:154 - Cropping pdf file
2019-02-03 18:11:53.247 | INFO     | __main__:shrink_pdf:172 - Shrinking pdf file
2019-02-03 18:11:54.802 | INFO     | __main__:upload_to_rm:218 - Starting upload to reMarkable
2019-02-03 18:11:57.767 | INFO     | __main__:upload_to_rm:223 - Upload successful.
```

## Dependencies

The script requires the following external programs to be available:

- [pdftk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
- [pdfcrop](https://ctan.org/pkg/pdfcrop?lang=en): usually included with a 
  LaTeX installation.
- [GhostScript](https://www.ghostscript.com/)
- [rMAPI](https://github.com/juruen/rmapi)

If these scripts are not available on the PATH variable, you can supply them 
with the relevant options to the script.

The script also needs the following Python packages:

- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [requests](https://pypi.org/project/requests/)
- [loguru](https://pypi.org/project/loguru/)
- [PyPDF2](https://github.com/mstamy2/PyPDF2)

You can use this line:

```bash
pip install --user bs4 requests loguru PyPDF2
```

# Notes

License: MIT

Author: G.J.J. van den Burg
