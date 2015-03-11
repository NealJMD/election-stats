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
    while re.search("district", lines[district_count]) and district_count < len(lines):
        district_count += 1
    print "counted <%i> districts, failing line <%s>" % (district_count, lines[district_count])
    return district_count

def parse_stats_from_string(pdf_string):
    state_strings = re.split("\n1st district", pdf_string)
    state_stats = []
    for ii, state_string in enumerate(state_strings):
        if ii == 0: continue
        lines = state_string.split("\n")
        lines[0] = "1st district" + lines[0] # replace removed by regex
        try:
            state_stats += [parse_stats_from_lines(lines)]
        except Exception, e:
            print e
            print len(lines)
    return state_stats

def parse_votes_from_line(line):
    """ returns -1 if not parseable """
    if re.match("\A[. ]+\Z", line): return 0
    clean = re.sub("[,.()]", "", line)
    try:
        return int(clean)
    except Exception, e:
        # print "input <%s>, cleaned to <%s> raised error" % (line, clean)
        return -1

def next_state(current_state):
    if current_state == "R":
        return "D"
    elif current_state == "D":
        return "finished"

def parse_stats_from_lines(lines):
    district_count = count_districts_from_lines(lines)
    votes_by_district = []
    state = "R"
    district, line = 0, district_count
    while state != "finished":
        votes = parse_votes_from_line(lines[line])
        print "     parsed <%s> to <%i>" % (lines[line], votes)
        if votes >= 0:
            if (district == 0 and
              parse_votes_from_line(lines[line-1]) == -1 and
              parse_votes_from_line(lines[line+1]) == -1):
                line += 1
                continue
            if len(votes_by_district) <= district: votes_by_district.append({})
            votes_by_district[district][state] = votes
            district += 1
            if district >= district_count:
                district = 0
                state = next_state(state)
        line += 1
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

