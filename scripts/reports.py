REPORT_FILE_SUFFIX = "MsgStatsAndAbortRep.txt"
FIELDS = ['latency_avg', 'delivery_prob', 'overhead_ratio', 'delivered']
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
import copy
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def generate_layer_report(dir_path="./rep2", dest_path="./", report_name="report.txt", run_count=None):
    """
    Goes through all LAYER_FILE_SUFFIX file endings and generate each iteration's layer stats.
    """
    report_set = list()
    summary = dict()
    rep_name = report_name.replace(".txt", "_layer_.txt")
    for reports in os.listdir(dir_path):
        if str(reports).endswith(LAYER_FILE_SUFFIX) and not str(reports).startswith('._'):
            report_set.append( str(dir_path) + '/' + str(reports))
    for report in report_set:
        # try:
        current_iteration = str(report).strip(dir_path).strip('/').split("_")[4]
        _, report_summary = extract_layer_data(report)
        report_summary = [round(float(i)/5, 3) for i in report_summary]
        sub_report_name = str(report).strip(dir_path).strip("/" + "\t").replace("_" + current_iteration, "")
        if summary.keys().__contains__(sub_report_name):
            for i in range(len(summary[sub_report_name])):
                summary[sub_report_name][i] += report_summary[i]
        else:
            summary[sub_report_name] = report_summary
        # except Exception as e:
        #     print(e)
    file_summary = "Summary_Filename\taI\tmD\t0,1,2,3,4,5,6,7,8,9\n"
    for report in summary.keys():
        file_summary += report + "\t" + report.split("_")[6].strip("aI") + "\t" + report.split("_")[7].strip("mD") + "\t"
        for layer in summary[report]:
            file_summary += str(layer) + ","
        file_summary += "\n"
    print(file_summary)
    with open(dest_path + rep_name.replace(".txt", "_summary.txt"), 'w') as f:
        f.write(file_summary)


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
    report = "StatsFilename" + "\t"
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
    with open(dest_path+report_name, 'w') as f:
        f.write(report) 
    print(report)
    generate_layer_report(dir_path, dest_path, report_name, run_count)      
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
    layers_delivered_burst_id = dict()
    with open(filename, 'r', encoding='ISO-8859-1') as f:
        data = f.readlines()
        for line in data[1:]:
            burst_id, current_layer = line.split(" ")[1].split("_L")
            if layers_delivered_burst_id.keys().__contains__(burst_id):
                layers_delivered_burst_id[burst_id].append(int(current_layer))
                layers_delivered_burst_id[burst_id] = sorted(layers_delivered_burst_id[burst_id])
            else:
                layers_delivered_burst_id[burst_id] = [int(current_layer)]
    remove_id = []
    for id in layers_delivered_burst_id.keys():
        if layers_delivered_burst_id[id][0] == 0:
            test = str()
            test += str(layers_delivered_burst_id[id])
            delivered_list = layers_delivered_burst_id[id]
            i = 0
            while i < len(delivered_list) - 1:
                if delivered_list[i+1] == delivered_list[i] + 1:
                    i += 1
                else:
                    break   
            delivered_list.clear()
            delivered_list = list(range(0, i+1))
            print(test,delivered_list, sep='  ')
            layers_delivered_burst_id[id] = delivered_list
        else:
            remove_id.append(id)
    for i in remove_id:
        try:
            layers_delivered_burst_id.pop(i)
        except:
            pass
    summary = [0,0,0,0,0,0,0,0,0,0]
    for id in layers_delivered_burst_id.keys():
        for layers in layers_delivered_burst_id[id]:
            summary[layers] += 1
        layers_delivered_burst_id[id] = summary
    return str(filename), summary
                
def plot_report_data(report_path=None, all=True):
    """
    Plots relevant additive, multiplicative data against existing fields
    """
    if not all:
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
    else:
        with open(report_path, 'r') as f:
            report = f.readlines()
            addData = list()
            multData = list()
            delivery_prob_data = list()
            latency_avg_data = list()
            for line in report[1:]:
                data = line.split("\t")
                ack = data[0][1]
                if not ack == 'o':
                    addIncr = data[0].split("_")[6]
                    multDecr = data[0].split("_")[7]
                    delivery_prob_data.append(data[1])
                    latency_avg_data.append(data[2])
                    addData.append(float(addIncr.strip("aI")))
                    multData.append(float(multDecr.strip("mD")))
            plot_data("Delivery probability vs AddIncr vs MultDecr", "AddIncr", "MultDecr", addData, multData, None, z_data=delivery_prob_data, z_label="Delivery probability")
            plot_data("Latency vs AddIncr vs MultDecr", "AddIncr", "MultDecr", addData, multData, None, z_data=latency_avg_data, z_label="Latency")
        with open(report_path.replace(".txt", "_summary.txt"), 'r') as f:
            report = f.readlines()
            addData = list()
            multData = list()
            # TODO Add delivered 3D plot code
                    


def plot_data(graph_title=None, x_label=None, y_label=None, x_data=None, y_data=None, y_data_labels=None, all=True, z_data=None, z_label=None):
    """
    General method to plot given arguments. Only for multiple y-data
    """
    if not all:
        y_data_labels = list(y_data_labels)
        # if str(graph_title).__contains__("Latency"):
        #     plt.gca().set_ylim([0.1, 1000]) # Set's the Y limits. gca - get current axes
        # else:
        #     plt.gca().set_ylim([0.40, 0.55])
        for Y in y_data:
            x, y = zip(*sorted(zip(x_data, Y), key=lambda x: x[0]))
            plt.plot(x, y, color=COLOURS[y_data.index(Y)], label="Ack" + str(y_data_labels[y_data.index(Y)]), marker=".")
        #if graph_title.__contains__("Latency"):
        plt.xscale('log', basex=10)
        #plt.gca().set_xlim([0, 0.03]) # Set's the Y limits. gca - get current axes
        plt.title(graph_title, fontsize=16, fontweight='bold')
        plt.legend(loc="best")        
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        y_data_labels = list(y_data_labels)
        plt.savefig(graph_title + ".png")
        plt.clf()
    else:
        x_data = [float(i) for i in x_data]
        y_data = [float(i) for i in y_data]
        z_data = [float(i) for i in z_data]
        x, y, z = zip(*sorted(zip(x_data, y_data, z_data), key=lambda x: x[1]))
        plt.title(graph_title, fontsize=16, fontweight='bold')
        plt.legend(loc="best")
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot3D(x, y, z, COLOURS[0])
        ax.set_xlabel = x_label
        ax.set_ylabel = y_label
        ax.set_zlabel = z_label
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
