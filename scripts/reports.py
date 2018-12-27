REPORT_FILE_SUFFIX = "MsgStatsAndAbortRep.txt"
FIELDS = ['latency_avg', 'delivery_prob']
LAYER_FILE_SUFFIX = "DeliveredMessagesReport.txt"
LAYERS = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9']
COLOURS = ["#FFA500", "#0000FF", "#00FF00"]

"""Gives the best delivered layer in a given burst"""
BEST_LAYER = 0 
"""Gives all layers in a given burst"""
ALL_LAYERS = 1 

"""
Run pip3 install -r requirements.txt before running this script.
"""

import os
import sys
import matplotlib.pyplot as plt


def generate_layer_report(dir_path="./rep2", dest_path="./", report_name="report.txt", run_count=None):
    """
    Goes through all LAYER_FILE_SUFFIX file endings and generate each iteration's layer stats.
    """
    report_set = list()
    report_data = dict()
    report_name = report_name.replace(".txt", "_layer_.txt")
    for reports in os.listdir(dir_path):
        if str(reports).endswith(LAYER_FILE_SUFFIX) and not str(reports).startswith('._'):
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
        if str(reports).endswith(REPORT_FILE_SUFFIX) and not str(reports).startswith('._'):
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
    report += '\n'
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
    plot_report_data(dest_path+report_name)


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
                
def plot_report_data(report_path=None):
    """
    Plot's relevant additive, multiplicative data against existing fields
    """
    with open(report_path, 'r') as f:
        report = f.readlines()
        seg_data = dict()
        for line in report[1:]:
            data = line.split("\t")
            ack = data[0][1]
            if not ack == 'o':
                addIncr = data[0].split("_")[6]
                multDecr = data[0].split("_")[7]
                delivery_prob, latency_avg = data[1], data[2]
                addIncr = float(addIncr.strip("aI"))
                multDecr = float(multDecr.strip("mD"))
                if seg_data.keys().__contains__(ack):
                    seg_data[ack][0].append(addIncr)
                    seg_data[ack][1].append(multDecr)
                    seg_data[ack][2].append(delivery_prob)
                    seg_data[ack][3].append(latency_avg)
                else:
                    seg_data[ack] = [[addIncr], [multDecr], [delivery_prob], [latency_avg]]
        const_add = 0.004
        const_mult = 0.08
        const_add_mult_data = list()
        const_mult_add_data = list()
        const_add_delivery_data = list()
        const_mult_delivery_data = list()
        const_add_latency_data = list()
        const_mult_latency_data = list()
        for ackNum in seg_data.keys():
            ack_add_delivery_data = list()
            ack_add_latency_data = list()
            for a in range(len(seg_data[ackNum][0])):
                if seg_data[ackNum][0][a] ==  const_add:
                    "Add equal"
                    if ackNum == '1':
                        const_add_mult_data.append(seg_data[ackNum][1][a])
                    ack_add_delivery_data.append(round(float(seg_data[ackNum][2][a]), 6))
                    ack_add_latency_data.append(round(float(seg_data[ackNum][3][a]), 6))
            const_add_delivery_data.append(ack_add_delivery_data)
            const_add_latency_data.append(ack_add_latency_data)
            ack_mult_delivery_data = list()
            ack_mult_latency_data = list()
            for m in range(len(seg_data[ackNum][1])):
                if seg_data[ackNum][1][m] ==  const_mult:
                    if ackNum == '1':
                        const_mult_add_data.append(seg_data[ackNum][0][m])
                    ack_mult_delivery_data.append(round(float(seg_data[ackNum][2][m]), 6))
                    ack_mult_latency_data.append(round(float(seg_data[ackNum][3][m]), 6))
            const_mult_delivery_data.append(ack_mult_delivery_data)
            const_mult_latency_data.append(ack_mult_latency_data)
        print(const_mult_add_data)
        print(const_add_mult_data)
        print(const_add_latency_data)
        print(const_add_delivery_data)
        print(const_mult_delivery_data)
        print(const_mult_latency_data)
        plot_data("Additive Increase vs Latency", "Additive Increase", "Latency", const_mult_add_data, const_mult_latency_data, seg_data.keys())
        plot_data("Additive Increase vs Delivery payloads", "Additive Increase", "Delivery payloads", const_mult_add_data, const_mult_delivery_data, seg_data.keys())
        plot_data("Multiplicative Decrease vs Latency", "Multiplicative decrease", "Latency", const_add_mult_data, const_add_latency_data, seg_data.keys())
        plot_data("Multiplicative Decrease vs Delivery Payload", "Multiplicative decrease", "Delivery payload", const_add_mult_data, const_add_delivery_data, seg_data.keys())


def plot_data(graph_title=None, x_label=None, y_label=None, x_data=None, y_data=None, y_data_labels=None):
    """
    General method to plot given arguments. Only for multiple y-data
    """
    y_data_labels = list(y_data_labels)
    # if str(graph_title).__contains__("Latency"):
    #     plt.gca().set_ylim([4000, 5000]) # Set's the Y limits. gca - get current axes
    # else:
    #     plt.gca().set_ylim([0.40, 0.55])
    for Y in y_data:
        x, y = zip(*sorted(zip(x_data, Y), key=lambda x: x[0]))
        plt.plot(x, y, color=COLOURS[y_data.index(Y)], label="Ack" + str(y_data_labels[y_data.index(Y)]), marker=".")
    plt.title(graph_title, fontsize=16, fontweight='bold')
    plt.xlabel = x_label
    plt.ylabel = y_label
    plt.legend(loc="best")        
    y_data_labels = list(y_data_labels)
    plt.savefig(graph_title + ".png")
    plt.clf()
                


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