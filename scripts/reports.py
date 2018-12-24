FILE_SUFFIX = "MsgStatsAndAbortRep.txt"
FIELDS = ['latency_avg', 'delivery_prob']

import os
import sys


def generate_report(dir_path="./rep2", dest_path="./", report_name="report.txt"):
    """
    Extracts all fields from the files that end with suffix MsgStatsAndAbortRep.txt.
    """
    report_set = list()
    report_data = dict()
    seg_list = dict()
    
    run_count = 0
    for reports in os.listdir(dir_path):
        if str(reports).endswith(FILE_SUFFIX):
            report_set.append(str(dir_path) + '/' + str(reports))
            try:
                if int(str(reports).split("_")[4]) - 1000 > run_count:
                    run_count = int(str(reports).split("_")[4]) - 1000
            except:
                pass
    for iteration in report_set:
        filename, stat = extract_data(iteration, run_count)
        filename = filename.replace(dir_path + "/", "")
        if report_data.keys().__contains__(str(filename).replace("_" + filename.split("_")[4], "")):
            for k in report_data[str(filename).replace("_" + filename.split("_")[4], "")].keys():
                report_data[str(filename).replace("_" + filename.split("_")[4], "")][k] += stat[k]
        else: 
            report_data[str(filename).replace("_" + filename.split("_")[4], "")] = stat
    report = "filename" + "\t"
    for field in report_data[list(report_data.keys())[0]].keys():
        report += str(field) + "\t"
    for files in report_data.keys():
        filedata = str(files).strip(dir_path).strip(dest_path) + "\t"
        for field in report_data[files].keys():
            filedata += str(report_data[files][field]).strip("\n") + "\t"
        filedata += ("\n")
        report += filedata
    if dest_path.endswith("/"):
        dest_path += "/"
    with open(dest_path+report_name, 'w') as f:
        f.write(report)    


def extract_data(filename=None, run_count=None):
    """
    Searches for all lines that contain a field and it's corresponding value and returns a dictonary containing those fields
    """
    stat = dict()
    with open(filename, 'r', encoding='ISO-8859-1') as f:
        data = f.readlines()
        for line in data:
            if len(str(line).split(": ")) == 2:
                try:
                    if FIELDS.__contains__(str(line).split(": ")[0]):
                        stat[str(line).split(": ")[0]] = float(str(line).split(": ")[1]) / run_count
                except Exception as e:
                    pass
    return filename, stat


if __name__ == "__main__":
    """
    Arguments:
    1. Report directory path 
    2. Report destination path
    3. Report name
    """
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
        dest_path = sys.argv[2]
        report_name = sys.argv[3]
        generate_report(dir_path, dest_path, report_name)
    else:
        generate_report()