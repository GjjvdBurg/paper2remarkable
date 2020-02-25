# paper2remarkable

[![PyPI 
version](https://badge.fury.io/py/paper2remarkable.svg)](https://pypi.org/project/paper2remarkable)

``paper2remarkable`` is a command line program for quickly and easily 
transferring an academic paper to your [reMarkable](https://remarkable.com/):

```
$ p2r https://arxiv.org/abs/1811.11242
```

There is also support for transferring an article from a website:

```
$ p2r https://hbr.org/2019/11/getting-your-team-to-do-more-than-meet-deadlines
```

The script can be run through the ``p2r`` command line program or via Docker
(see below). If you're using MacOS, you might be interested in the [Alfred
workflow](#alfred).

``paper2remarkable`` makes it as easy as possible to get a PDF on your 
reMarkable from any of the following sources:

* [arXiv](https://arxiv.org/)
* [ACM Digital Library](https://dl.acm.org/dl.cfm)
* [CiteSeerX](http://citeseerx.ist.psu.edu/index)
* [JMLR](http://jmlr.org)
* [NBER](https://www.nber.org)
* [NeurIPS](https://papers.nips.cc/)
* [OpenReview](https://openreview.net/)
* [PMLR](http://proceedings.mlr.press/)
* [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/)
* [SpringerLink](https://link.springer.com/)
* A generic URL to a PDF file
* A local PDF file
* Any article on a website

The program aims to be flexible to the exact source URL, so for many of the 
academic sources you can either provide a URL to the abstract page or to the 
PDF file. If you have an source that you would like to see added to the list, 
let me know!

``paper2remarkable`` takes the source URL and:

1. Downloads the pdf if necessary
2. Removes the arXiv timestamp (for arXiv sources)
3. Crops the pdf to remove unnecessary borders
4. Shrinks the pdf file to reduce the filesize
5. Generates a nice filename based on author/title/year of the paper
6. Uploads it to your reMarkable using 
   [rMapi](https://github.com/juruen/rmapi).

Optionally, you can:

- Download a paper but not upload to the reMarkable using the ``-n`` switch.
- Insert a blank page after each page using the ``-b`` switch (useful for note 
  taking!)
- Center the pdf on the reMarkable (default is left-aligned)
- Provide an explicit filename using the ``--filename`` parameter
- Specify the location on the reMarkable to place the file (default ``/``)

Here's the full help of the script:

```text
usage: p2r [-h] [-b] [-c] [-d] [-n] [-p REMARKABLE_DIR] [-r] [-k] [-v] [-V]
           [--filename FILENAME] [--gs GS] [--pdftoppm PDFTOPPM]
           [--pdftk PDFTK] [--rmapi RMAPI]
           input

Paper2reMarkable version 0.5.4

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
  -r, --right           Right align so the menu doesn't cover it
  -k, --no-crop         Don't crop the pdf file
  -v, --verbose         be verbose
  -V, --version         Show version and exit
  --filename FILENAME   Filename to use for the file on reMarkable
  --gs GS               path to gs executable (default: gs)
  --pdftoppm PDFTOPPM   path to pdftoppm executable (default: pdftoppm)
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
- [GhostScript](https://www.ghostscript.com/)
- [rMAPI](https://github.com/juruen/rmapi)
- [pdftoppm](https://linux.die.net/man/1/pdftoppm) Optional, but recommended 
  for speed. Usually part of a [Poppler](https://poppler.freedesktop.org/) 
  installation.

If these scripts are not available on the ``PATH`` variable, you can supply 
them with the relevant options to the script. Then, you can install 
``paper2remarkable`` from PyPI:

```
pip install paper2remarkable
```

This installs the ``p2r`` command line program.

## Alfred

Install the [Alfred workflow][workflow], which is [a launcher for
MacOS](https://www.alfredapp.com/).

Once installed, you can use `rm` command and `rmb` (for the `--blank` pages to
insert blank pages between pages for notes) with a URL passed. The global
shortcut `Alt-P` will send the current selection to `p2r`. Note that by default
`--right` is passed and `p2r` is executed in your `bash` environment. You can
edit the Workflow in Alfred if this doesn't work for your setup.

![Alfred Screenshot](https://raw.githubusercontent.com/GjjvdBurg/paper2remarkable/master/.github/alfred.png)

[workflow]: https://github.com/GjjvdBurg/paper2remarkable/blob/master/Remarkable.alfredworkflow?raw=true 

## Docker

You can also use the Dockerfile to avoid installing dependencies on your 
machine. You will need `git` and `docker` installed.

First clone this repository with `git clone` and `cd` inside of it, then build 
the container:

```bash
docker build -t p2r .
```

### Authorization

If you already have a `~/.rmapi` file, you can skip this section. Otherwise 
we'll use `rmapi` to create it.

```bash
touch ${HOME}/.rmapi
docker run --rm -i -t -v "${HOME}/.rmapi:/home/user/.rmapi:rw" --entrypoint=rmapi p2r version
```

which should end with output like

```bash
ReMarkable Cloud API Shell
rmapi version: 0.0.5
```

### Usage

Use the container by replacing `p2r` with `docker run --rm -v 
"${HOME}/.rmapi:/home/user/.rmapi:rw" p2r`, e.g.

```
# print help and exit
docker run --rm -v "${HOME}/.rmapi:/home/user/.rmapi:rw" p2r --help

# equivalent to above usage
docker run --rm -v "${HOME}/.rmapi:/home/user/.rmapi:rw" p2r -v https://arxiv.org/abs/1811.11242
```

You can also create an [alias](http://tldp.org/LDP/abs/html/aliases.html) in 
your ``~/.bashrc`` file to abstract away the Docker commands:

```bash
# in ~/.bashrc

alias p2r="docker run --rm -v \"${HOME}/.rmapi:/home/user/.rmapi:rw\" p2r"
```

Then you can use ``paper2remarkable`` from the command line as ``p2r``!

# Notes

License: MIT

If you find a problem or want to suggest a feature, please let us know! You're 
helping to make this project better!
