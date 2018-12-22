FILE_SUFFIX = "MsgStatsAndAbortRep.txt"

import os
import sys


def generate_report(dir_path="./rep2", dest_path="./", report_name="report.txt"):
    """
    Extracts all fields from the files that end with suffix MsgStatsAndAbortRep.txt.
    """
    report_set = list()
    report_data = dict()
    for reports in os.listdir(dir_path):
        if str(reports).endswith(FILE_SUFFIX):
            report_set.append(str(dir_path) + '/' + str(reports))
    for iteration in report_set:
        filename, stat = extract_data(iteration)
        report_data[str(filename)] = stat
    report = ""
    for field in report_data[list(report_data.keys())[0]].keys():
        report += str(field) + "\t"
    for files in report_data.keys():
        filedata = str(files).strip(dir_path).strip(dest_path) + "\t"
        for field in report_data[files].keys():
            filedata += str(report_data[files][field]).strip("\n") + "\t"
            print(filedata)
        filedata += ("\n")
        report += filedata
    if dest_path.endswith("/"):
        dest_path += "/"
    with open(dest_path+report_name, 'w') as f:
        f.write(report)    


def extract_data(filename=None):
    """
    Searches for all lines that contain a field and it's corresponding value and returns a dictonary containing those fields
    """
    stat = dict()
    with open(filename, 'r') as f:
        data = f.readlines()
        for line in data:
            if len(str(line).split(": ")) == 2:
                stat[str(line).split(": ")[0]] = str(line).split(": ")[1]
    return filename, stat


if __name__ == "__main__":
    dir_path = sys.argv[1]
    dest_path = sys.argv[2]
    report_name = sys.argv[3]
    print(dir_path + " " + dest_path + " " + report_name)
    generate_report(dir_path, dest_path, report_name)