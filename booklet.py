#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""booklet — PDF imposition tool for signature booklet printing."""

import sys
import math
import argparse
import pymupdf as fitz


def print_help() -> None:
    print("""
  booklet — PDF imposition for signature booklet printing

  Rearranges PDF pages into folded signatures ready for duplex printing.
  Each signature contains up to N sheets (default 4), folded together.
  Output pages are landscape with two source pages side by side.
  Print duplex with long-edge flip (flip on left/right axis).

  Usage:
    booklet <input.pdf> <output.pdf> [options]

  Arguments:
    input.pdf     Source PDF file
    output.pdf    Output PDF file

  Options:
    -s, --sheets N    Sheets per signature (default: 4)
    -n, --number      Print page number at the bottom center of each page
    -h, --help        Show this help message

  Examples:
    booklet book.pdf booklet.pdf
    booklet book.pdf booklet.pdf --sheets 2
    booklet book.pdf booklet.pdf -s 6
""")


def signature_order(sig_start: int, n_sheets: int, n_src: int) -> list[tuple[int, int]]:
    """
    Returns (left, right) page index pairs for one signature.
    Indices >= n_src represent blank pages.

    For n_sheets sheets (n = 4*n_sheets pages):
      Sheet i front: [n-1 - 2*(i-1),  2*(i-1)      ]
      Sheet i back:  [    2*(i-1)+1,  n-2 - 2*(i-1) ]
    """
    n = n_sheets * 4
    pairs = []
    for i in range(1, n_sheets + 1):
        left_front  = sig_start + n - 1 - 2 * (i - 1)
        right_front = sig_start + 2 * (i - 1)
        left_back   = sig_start + 2 * (i - 1) + 1
        right_back  = sig_start + n - 2 - 2 * (i - 1)
        pairs.append((left_front, right_front))
        pairs.append((left_back,  right_back))
    return pairs


def compute_signatures(n_pages: int, max_sheets: int) -> list[tuple[int, int]]:
    """
    Returns list of (start_index, n_sheets) for each signature.
    Full signatures have max_sheets sheets; the last one may have fewer.
    """
    pages_per_sig = max_sheets * 4
    sigs = []
    pos = 0
    remaining = n_pages
    while remaining > 0:
        if remaining >= pages_per_sig:
            n_sheets = max_sheets
        else:
            n_sheets = math.ceil(remaining / 4)
        sigs.append((pos, n_sheets))
        pos += n_sheets * 4
        remaining -= n_sheets * 4
    return sigs


def add_page_number(page: fitz.Page, number: int, center_x: float, bottom_y: float) -> None:
    fontsize = 9
    margin = 14
    text = str(number)
    tw = fitz.get_text_length(text, fontname="helv", fontsize=fontsize)
    x = center_x - tw / 2
    y = bottom_y - margin
    page.insert_text((x, y), text, fontname="helv", fontsize=fontsize, color=(0.4, 0.4, 0.4))


def build_booklet(input_path: str, output_path: str, max_sheets: int = 4, number_pages: bool = False) -> None:
    src = fitz.open(input_path)
    n_src = len(src)

    sigs = compute_signatures(n_src, max_sheets)
    total_pages = sum(s * 4 for _, s in sigs)
    blanks = total_pages - n_src

    print(f"  Input pages  : {n_src}")
    print(f"  Signatures   : {len(sigs)}")
    for idx, (start, sheets) in enumerate(sigs, 1):
        real = min(n_src - start, sheets * 4)
        blank = sheets * 4 - real
        blank_str = f" + {blank} blank" if blank else ""
        print(f"    #{idx}  {sheets} sheet(s)  —  {real} pages{blank_str}")
    if blanks:
        print(f"  Blank pages added: {blanks}")

    ref = src[0]
    pw, ph = ref.rect.width, ref.rect.height
    out_w, out_h = pw * 2, ph

    out = fitz.open()

    for sig_start, n_sheets in sigs:
        pairs = signature_order(sig_start, n_sheets, n_src)
        for left_idx, right_idx in pairs:
            page = out.new_page(width=out_w, height=out_h)
            if left_idx < n_src:
                page.show_pdf_page(fitz.Rect(0, 0, pw, ph), src, left_idx)
                if number_pages:
                    add_page_number(page, left_idx + 1, pw / 2, ph)
            if right_idx < n_src:
                page.show_pdf_page(fitz.Rect(pw, 0, out_w, ph), src, right_idx)
                if number_pages:
                    add_page_number(page, right_idx + 1, pw + pw / 2, ph)

    out.save(output_path, garbage=4, deflate=True)
    out.close()
    src.close()

    total_output = sum(s * 2 for _, s in sigs)
    print(f"\n  Saved to     : {output_path}")
    print(f"  Output pages : {total_output}  (print duplex, long-edge flip)\n")


if __name__ == "__main__":
    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("-s", "--sheets", type=int, default=4, metavar="N")
    parser.add_argument("-n", "--number", action="store_true")
    args = parser.parse_args()

    if args.sheets < 1:
        print("  Error: --sheets must be at least 1.")
        sys.exit(1)

    build_booklet(args.input, args.output, max_sheets=args.sheets, number_pages=args.number)
