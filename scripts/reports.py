REPORT_FILE_SUFFIX = "MsgStatsAndAbortRep.txt"
FIELDS = ['latency_avg', 'delivery_prob']
LAYER_FILE_SUFFIX = "DeliveredMessagesReport.txt"
LAYERS = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9']

"""Gives the best delivered layer in a given burst"""
BEST_LAYER = 0 
"""Gives all layers in a given burst"""
ALL_LAYERS = 1 


import os
import sys


def generate_layer_report(dir_path="./rep2", dest_path="./", report_name="report.txt", run_count=None):
    """
    Goes through all LAYER_FILE_SUFFIX file endings and generate each iteration's layer stats.
    """
    report_set = list()
    report_data = dict()
    report_name = report_name.replace(".txt", "_layer_.txt")
    for reports in os.listdir(dir_path):
        if str(reports).endswith(LAYER_FILE_SUFFIX):
            report_set.append( str(dir_path) + '/' + str(reports))
    for report in report_set:
        try:
            current_iteration = int(str(report).split("_")[4])
        except:
            pass
        _, current_run_data = extract_layer_data(report)
        current_data = str(report).replace(dir_path, "").strip("/" + "\t")
        for field in current_run_data.keys():
            current_data = str(current_data) + str(current_run_data[field]) + "\t"
        if report_data.__contains__(current_iteration):
            report_data[current_iteration] += current_data + "\n"
        else:
            report_data[current_iteration] = str(current_data)
    for iteration in report_data.keys():
        with open(dest_path + report_name.replace(".txt", str(iteration) + ".txt"), 'w') as f:
            f.write(report_data[iteration])


def generate_report(dir_path="./rep2", dest_path="./", report_name="report.txt"):
    """
    Extracts all fields from the files that end with suffix MsgStatsAndAbortRep.txt.
    """
    report_set = list()
    report_data = dict()
    seg_list = dict()
    
    run_count = 0
    for reports in os.listdir(dir_path):
        if str(reports).endswith(REPORT_FILE_SUFFIX):
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
    generate_layer_report(dir_path, dest_path, report_name, run_count)
    with open(dest_path+report_name, 'w') as f:
        f.write(report)    


def extract_data(filename=None, run_count=None):
    """
    Searches for all lines that contain a field and it's corresponding value and returns a dictonary containing those fields.
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


def extract_layer_data(filename=None, run_count=None):
    """
    Extracts layer data for each burst in each iteration.
    """
    layer_report = dict()
    with open(filename, 'r', encoding='ISO-8859-1') as f:
        data = f.readlines()
        for line in data[1:]:
            burst_id, current_layer = line.split(" ")[1].split("_L")
            if layer_report.keys().__contains__(burst_id):
                if layer_report[burst_id] + 1 == int(current_layer):
                    layer_report[burst_id] = int(current_layer)
            else:
                layer_report[burst_id] = int(current_layer)
    return str(filename), layer_report
                



if __name__ == "__main__":
    """
    Arguments:
    1. Existing reports directory path 
    2. Generated report destination path
    3. Report's name
    """
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
        dest_path = sys.argv[2]
        report_name = sys.argv[3]
        generate_report(dir_path, dest_path, report_name)
    else:
        generate_report()