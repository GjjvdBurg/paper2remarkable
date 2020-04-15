# Changelog

## Version 0.6.2

* Print to log whether removing arXiv stamp was successful.
* Fix bug that failed to correctly detect the pdf tool 
  ([#42](https://github.com/GjjvdBurg/paper2remarkable/issues/42)).

## Version 0.6.1

* Bugfix that makes removing the arXiv stamp more robust.

## Version 0.6.0

* The Dockerfile has been updated to use a more recent version of Cairo
  ([#35](https://github.com/GjjvdBurg/paper2remarkable/issues/35)). Thanks to 
  @ClaytonJY.
* We've added support for optionally using qpdf instead of pdftk
  ([#36](https://github.com/GjjvdBurg/paper2remarkable/pull/36)). Thanks to 
  @delaere.
* Resolving redirects has been improved, which solves an issue for the 
  Springer provider 
  ([#38](https://github.com/GjjvdBurg/paper2remarkable/pull/38)) and an issue 
  with some arXiv urls 
  ([#39](https://github.com/GjjvdBurg/paper2remarkable/pull/39)).
* Unit tests were added for the provider selection.
* The code that removes the arXiv stamp has been improved 
  ([#40](https://github.com/GjjvdBurg/paper2remarkable/pull/40)).
* Tracebacks have been disabled outside of debug mode, showing clearer errors 
  ([#41](https://github.com/GjjvdBurg/paper2remarkable/pull/41)).

## Version 0.5.6

* Be more robust against missing pdftoppm executable.

## Version 0.5.5

* Fix bug for when the shrink operation returns bigger files 
  ([#33](https://github.com/GjjvdBurg/paper2remarkable/issues/33)).

## Version 0.5.4

* Add the option to not crop the file at all
  ([#28](https://github.com/GjjvdBurg/paper2remarkable/pull/30)).
* Add the option to right-align the file so the menu doesn't overlap
  ([#28](https://github.com/GjjvdBurg/paper2remarkable/pull/31)).
* Bugfix for validation for the JMLR provider

## Version 0.5.3

* Significantly speed up the program 
  ([#26](https://github.com/GjjvdBurg/paper2remarkable/issues/26))
* Add provider for JMLR 
  ([#28](https://github.com/GjjvdBurg/paper2remarkable/pull/28)).
* Bugfix for creating nested directories with ``-p`` option.

## Version 0.5.2

* Add provider for US National Bureau of Economic Research
  ([#27](https://github.com/GjjvdBurg/paper2remarkable/pull/27)).
* Automatically extract the filename from a pdf url where possible 
  ([#25](https://github.com/GjjvdBurg/paper2remarkable/issues/25)).
* Speed up centering of pdfs by removing unnecessary cropping operation.
* Improve robustness against missing metadata, remove spaces in author names, 
  and other minor improvements.

## Version 0.5.1

* Automatically detect when a HTML source is provided 
  ([#24](https://github.com/GjjvdBurg/paper2remarkable/pull/24))

## Version 0.5.0

* Add support for articles from the web using the ``--html`` flag 
  ([#23](https://github.com/GjjvdBurg/paper2remarkable/pull/23))
* Add ``--version`` command to command line interface
* Fix cropping bug that resulted in occassional rotated pages

## Version 0.4.6

* Add support for older arXiv URL scheme

## Version 0.4.5

* Add logging of long running crop/center operations
* Keep cookies during requests
* Add wait for CiteSeerX provider
* Make determining the provider more robust (issue 
  [#21](https://github.com/GjjvdBurg/paper2remarkable/issues/21))

## Version 0.4.4

* Bugfix for creating a directory on the reMarkable 
  ([#20](https://github.com/GjjvdBurg/paper2remarkable/issues/20))

## Version 0.4.3

* Add provider for CiteSeerX
* Update provider for ACM (website redesign)
* Properly use exceptions when errors occur

## Version 0.4.2

* Add provider for Proceedings of Machine Learning Research 
  ([#8](https://github.com/GjjvdBurg/paper2remarkable/issues/8))
* Add provider for NeurIPS papers 
  ([#12](https://github.com/GjjvdBurg/paper2remarkable/issues/12))

## Version 0.4.1

* Add support for alternative arXiv URLS
* Always run all redirects on specified urls before choosing provider

## Version 0.4.0

* Refactor code to make it a real Python package
* Rename to ``paper2remarkable``
