# paper2remarkable

*Note: ``paper2remarkable`` is the new name for the ``arxiv2remarkable`` 
script. The name was changed because it better captures what the program 
does.*

``paper2remarkable`` is a command line program for quickly and easily 
transferring an academic paper to your reMarkable:

```
$ p2r https://arxiv.org/abs/1811.11242
```

The script can be run through the ``p2r`` command line program or via Docker 
(see below).

paper2remarkable makes it as easy as possible to get a PDF on your reMarkable 
from any of the following sources:

- an arXiv url (either ``arxiv.org/abs/...`` or ``arxiv.org/pdf/...``)
- a PubMed Central url (either to the HTML or the PDF)
- an ACM citation page url (``https://dl.acm.org/citation.cfm?id=...``)
- an OpenReview paper (either ``openreview.net/forum?id=...`` or 
  ``openreview.net/pdf?id=...``)
- a Springer paper url (either to the HTML or the PDF)
- a url to a PDF file
- a local file.

When called, the paper2remarkable takes the source and:

1. Downloads the pdf if necessary
2. Removes the arXiv timestamp (for arXiv sources)
3. Crops the pdf to remove unnecessary borders
4. Shrinks the pdf file to reduce the filesize
5. Generates a nice filename based on author/title/year of the paper
6. Uploads it to your reMarkable using ``rMapi``.

Optionally, you can:

- Download a paper but not upload to the reMarkable using the ``-n`` switch.
- Insert a blank page after each page using the ``-b`` switch (useful for note 
  taking!)
- Center the pdf on the reMarkable (default is left-aligned)
- Provide an explicit filename using the ``--filename`` parameter
- Specify the location on the reMarkable to place the file (default ``/``)

Here's the full help of the script:

```text
usage: p2r [-h] [-b] [-c] [-d] [-n] [-p REMARKABLE_DIR] [-v]
           [--filename FILENAME] [--gs GS] [--pdfcrop PDFCROP] [--pdftk PDFTK]
           [--rmapi RMAPI]
           input

Paper2reMarkable version 0.4.0

positional arguments:
  input                 URL to a paper or the path of a local PDF file

optional arguments:
  -h, --help            show this help message and exit
  -b, --blank           Add a blank page after every page of the PDF
  -c, --center          Center the PDF on the page, instead of left align
  -d, --debug           debug mode, doesn't upload to reMarkable
  -n, --no-upload       don't upload to the reMarkable, save the output in
                        current working dir
  -p REMARKABLE_DIR, --remarkable-path REMARKABLE_DIR
                        directory on reMarkable to put the file (created if
                        missing, default: /)
  -v, --verbose         be verbose
  --filename FILENAME   Filename to use for the file on reMarkable
  --gs GS               path to gs executable (default: gs)
  --pdfcrop PDFCROP     path to pdfcrop executable (default: pdfcrop)
  --pdftk PDFTK         path to pdftk executable (default: pdftk)
  --rmapi RMAPI         path to rmapi executable (default: rmapi)
```

And here's an example with verbose mode enabled that shows everything the 
script does by default:

```
$ p2r -v https://arxiv.org/abs/1811.11242
2019-05-30 00:38:27 - INFO - Starting ArxivProvider
2019-05-30 00:38:27 - INFO - Getting paper info from arXiv
2019-05-30 00:38:27 - INFO - Downloading url: https://arxiv.org/abs/1811.11242
2019-05-30 00:38:27 - INFO - Generating output filename
2019-05-30 00:38:27 - INFO - Created filename: Burg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2018.pdf
2019-05-30 00:38:27 - INFO - Downloading file at url: https://arxiv.org/pdf/1811.11242.pdf
2019-05-30 00:38:32 - INFO - Downloading url: https://arxiv.org/pdf/1811.11242.pdf
2019-05-30 00:38:32 - INFO - Removing arXiv timestamp
2019-05-30 00:38:34 - INFO - Cropping pdf file
2019-05-30 00:38:37 - INFO - Shrinking pdf file
2019-05-30 00:38:38 - INFO - Starting upload to reMarkable
2019-05-30 00:38:42 - INFO - Upload successful.
```

## Installation

The script requires the following external programs to be available:

- [pdftk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
- [pdfcrop](https://ctan.org/pkg/pdfcrop?lang=en): usually included with a 
  LaTeX installation.
- [GhostScript](https://www.ghostscript.com/)
- [rMAPI](https://github.com/juruen/rmapi)

If these scripts are not available on the ``PATH`` variable, you can supply 
them with the relevant options to the script. Then, you can install 
paper2remarkable from PyPI:

```
pip install paper2remarkable
```

This installs the ``p2r`` command line program.

## Docker

You can also use our Dockerfile to avoid installing dependencies on your 
machine. You will need `git` and `docker` installed.

First clone this repository with `git clone` and `cd` inside of it, then build 
the container:

```bash
docker build -t paper2remarkable .
```

### Authorization

If you already have a `~/.rmapi` file, you can skip this section. Otherwise 
we'll use `rmapi` to create it.

```bash
touch ${HOME}/.rmapi
docker run --rm --it -v "${HOME}/.rmapi:/root/.rmapi:rw" --entrypoint=rmapi paper2remarkable version
```

which should end with output like

```bash
ReMarkable Cloud API Shell
rmapi version: 0.0.5
```

### Usage

Use the container by replacing `p2r` with `docker run --rm -v 
"${HOME}/.rmapi:/root/.rmapi:rw" paper2remarkable`, e.g.

```
# print help and exit
docker run --rm -v "${HOME}/.rmapi:/root/.rmapi:rw" paper2remarkable --help

# equivalent to above usage via `python`
docker run --rm -v "${HOME}/.rmapi:/root/.rmapi:rw" paper2remarkable -v https://arxiv.org/abs/1811.11242
```

# Notes

License: MIT

Author: G.J.J. van den Burg
