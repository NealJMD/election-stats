import argparse
import re
import pdb

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

def read_text_from_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec="utf-8", laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    string = retstr.getvalue()
    retstr.close()
    return string

def read_text_from_file(path):
    fp = open(path, 'rb')
    text = fp.read()
    fp.close()
    return text

def count_districts_from_lines(lines):
    district_count = 0
    while re.search("district", lines[district_count]):
        district_count += 1
    return district_count

def parse_stats_from_string(pdf_string):
    state_strings = re.split("1st district", pdf_string)
    state_stats = []
    for state_string in state_strings:
        lines = state_string.split("\n")
        lines[0] = "1st district" + lines[0] # replace removed by regex
        try:
            state_stats += [parse_stats_from_lines(lines)]
        except Exception, e:
            print e
            print len(lines)
    return state_stats

def parse_votes_from_line(line):
    clean = re.sub("[,.]", "", line)
    if len(clean) < 1: return 0
    try:
        return int(clean)
    except Exception, e:
        print "input <%s>, cleaned to <%s> raised error" % (line, clean)
        return 0

def parse_stats_from_lines(lines):
    district_count = count_districts_from_lines(lines)
    republican_start = district_count + 1
    democrat_start = 2 * (district_count + 1)
    votes_by_district = []
    for ii in range(district_count):
        r = parse_votes_from_line(lines[republican_start+ii])
        d = parse_votes_from_line(lines[democrat_start+ii])
        votes_by_district +=  [{"R": r, "D": d}]
    return votes_by_district

def print_stats(stats):
    for ii, state in enumerate(stats):
        print "\n=== State %i ===" % (ii)
        for district_idx, votes in enumerate(state):
            print "  District %i: %i Republican, %i Democrat" % (district_idx+1, votes["R"], votes["D"])


def main(args):
    if len(args.pdf):
        text = read_text_from_pdf(args.pdf)
    else:
        text = read_text_from_file(args.txt)
    stats = parse_stats_from_string(text)
    # save_stats(stats)
    print_stats(stats)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse stats from US House election pdfs.')
    parser.add_argument('txt', metavar='txt', type=str,
                       help='the txt file to read from')
    parser.add_argument('--pdf', metavar='pdf', type=str, default="",
                       help='the pdf file to read from')
    parser.add_argument("--output", metavar='output', type=str, default='output.txt',
                       help='the destination to write the data to')

    args = parser.parse_args()
    main(args)

