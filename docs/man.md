# paper2remarkable

## SYNOPSIS

```
p2r [OPTION]... [INPUT]...
```

## DESCRIPTION

Fetch an academic paper, local pdf file, or any web article and send it to the 
reMarkable tablet. The input to the script can be a URL to a PDF file or 
article on a website, or a local file. For supported scientific outlets, the 
program will collect the metadata for the paper and create a nice filename 
(unless ``--filename`` is specified). See [SUPPORTED 
SOURCES](#supported-sources) for an overview of supported scientific paper 
sources.

By default, paper2remarkable crops the unnecessary whitespace from a PDF file 
to make the paper fit better on the reMarkable. The default setting yields a 
left-aligned document on the reMarkable which can be useful for taking margin 
notes. Alternatively, the program supports the ``--center``, ``--right``, and 
``--no-crop`` options to change this crop setting.

## OPTIONS

Basic options:

-b, --blank
      Add a blank page after every page of the PDF document. This can be 
      useful for taking notes on papers.

-C, --config=FILENAME
      Read options from a configuration file. A YAML file is supported, see 
      [CONFIGURATION FILE](#configuration) for further details. By default the 
      file at ``~/.paper2remarkable.yml`` is used if it exists.

-e, --experimental
      Enable the experimental features of paper2remarkable. See below under 
      [EXPERIMENTAL FEATURES](#experimental-features) for an overview.

-f, --filename=FILENAME
      Filename to use for the file on reMarkable. If you specify multiple 
      ``INPUT`` files and want to use a specific filename for each, you can 
      specify ``--filename`` for each ``INPUT`` source by repeating it.

-h, --help
      Show help message and exit.

-v, --verbose
      Enable verbose mode of paper2remarkable. By default the program prints 
      no output.

-V, --version
      Show the version and exit.

Crop options:

-c, --center
      Center the PDF on the page.

-k, --no-crop
      Don't crop the document at all.

-r, --right
      Right-align the document on the reMarkable so the menu doesn't cover it.

reMarkable options:

-n, --no-upload
      Don't upload the document to the reMarkable, save the output in the 
      current working directory.

-p, --remarkable-path=DIR
      The directory on the reMarkable where the document will be uploaded to. 
      If the target directory does not exist it will be created. If not 
      specified, the root directory will be used.

Output customization:

--css=FILENAME
      Path to a CSS file with custom styling for the HTML output. This option 
      is ignored for any of the other providers. The code for the HTML 
      provider contains the default CSS style, which can be used as a starting 
      point.

--font-urls=FILENAME
      Path to a file with font urls (one per line) for the HTML output. This 
      will generally be used in combination with the ``--css`` option.

System settings:

You'll only need to specify these options if the programs are not available on 
the PATH variable.

--gs=GS
      Path to the GhostScript executable.

--pdftoppm=PDFTOPPM
      Path to pdftoppm executable (default: pdftoppm). Note that pdftoppm is 
      optional.

--pdftk=PDFTK
      Path to PDFtk executable (default: pdftk). Either pdftk or qpdf is 
      needed.

--qpdf=QPDF
      Path to qpdf executable (default: qpdf). Either pdftk or qpdf is needed.

--rmapi=RMAPI
      Path to rmapi executable (default: rmapi).

Developer options:

-d, --debug
      Debug mode, when used the program doesn't upload the document to the 
      reMarkable by default and leaves the temporary directory with 
      intermediate files.

## SUPPORTED SOURCES

The following scientific sources are currently supported and paper2remarkable 
will create a filename based on the authors, title, and publication year of 
the work. For the sources below the program is generally flexible with regards 
to whether a URL to the PDF or to the abstract page is provided.

- arXiv
- ACL Web
- ACM Digital Library
- CVF
- ECCC
- IACR
- JMLR
- Nature
- NBER
- NeurIPS
- OpenReview
- PMLR
- PubMed Central
- SemanticScholar
- SpringerLink

paper2remarkable also supports a generic URL to a PDF file or a local file, in 
which case no "nice" filename will be generated.

- A generic URL to a PDF file. This can be considered a fallback option for 
  when a PDF source is not supported (yet).
- A local PDF file.

Finally, paper2remarkable supports extracting articles from websites. In this 
case an effort is done to detect the main content of the article and clean up 
the HTML before sending the file to the reMarkable.

## CONFIGURATION FILE

To avoid having to provide frequently-used command line flags, a configuration 
file can be created for paper2remarkable. By default it is a YAML file located 
at ``~/.paper2remarkable.yml``, but an alternative location can be provided 
with the ``--config`` option to the script.

The configuration file consists of three sections: ``core``, ``system``, and 
``html``. In the ``core`` section options for cropping, verbosity, and blank 
pages can be added, among others. The ``system`` section allows setting paths 
to executables such as ``rmapi``, ``pdftk``, etc.  Finally, the ``html`` 
section allows you to provide custom CSS and font urls for formatting the 
output of web articles.

Options provided on the command line overwrite those in the configuration 
file. So, for instance, if the configuration file has the setting ``crop: 
'left'`` in the ``core`` section and the command line flag ``-c`` is provided, 
the PDF will be centered.

An example file is provided in the repository on 
[GitHub](https://www.github.com/GjjvdBurg/paper2remarkable), which also 
contains more information on the available options and their values.

## EXPERIMENTAL FEATURES

Occassionally, experimental (beta) features will be included in 
paper2remarkable and they will be listed here. You can enable the experimental 
features by using the ``-e`` flag to paper2remarkable.

- The HTML provider currently has an experimental feature to handle lazy 
  loading of images. Certain websites use a small placeholder image and load 
  the main image using Javascript, with the actual image source stored in a 
  ``data-src`` attribute in the ``img`` tag. The experimental feature uses the 
  ``data-src`` attribute as the image source instead of that in the ``src`` 
  attribute.

## BUGS

Please report bugs to:

https://www.github.com/GjjvdBurg/paper2remarkable
