# booklet

PDF imposition tool for signature booklet printing.

Rearranges the pages of any PDF into folded signatures, producing a new PDF with two source pages side by side on each landscape sheet — ready to print, fold, and bind.

## How it works

Pages are grouped into **signatures** (a stack of folded sheets). Each signature holds up to N sheets (default: 4), which equals 4×N pages. The last signature uses only as many sheets as needed, padded with blank pages to the nearest multiple of 4.

For a 4-sheet signature the imposition order looks like this:

```
Sheet 1 front:  16 | 1
Sheet 1 back:    2 | 15
Sheet 2 front:  14 | 3
Sheet 2 back:    4 | 13
Sheet 3 front:  12 | 5
Sheet 3 back:    6 | 11
Sheet 4 front:  10 | 7
Sheet 4 back:    8 | 9
```

## Installation

Requires Python 3 and [PyMuPDF](https://pymupdf.readthedocs.io/):

```bash
pip install pymupdf
```

To install the `booklet` command globally:

```bash
chmod +x booklet.py
ln -s "$(pwd)/booklet.py" ~/.local/bin/booklet
```

## Usage

```
booklet <input.pdf> <output.pdf> [options]

Options:
  -s, --sheets N    Sheets per signature (default: 4)
  -n, --number      Print page number at the bottom center of each page
  -h, --help        Show help
```

## Examples

```bash
# Default: signatures of 4 sheets (16 pages each)
booklet book.pdf booklet.pdf

# Smaller signatures (e.g. for thinner paper or stapling)
booklet book.pdf booklet.pdf --sheets 2

# Single-sheet signatures (4 pages each)
booklet book.pdf booklet.pdf -s 1

# Add page numbers at the bottom center of each page
booklet book.pdf booklet.pdf --number
booklet book.pdf booklet.pdf -s 2 -n
```

## Printing

Print the output PDF **duplex** with **long-edge flip** (flip on the left/right axis — like turning pages of a book). This is the default duplex setting on most printers when the page is landscape.

After printing, fold each signature group and nest the sheets together, then bind or stitch the spines.
