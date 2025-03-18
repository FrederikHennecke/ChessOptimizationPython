import os
import ast
import matplotlib.pyplot as plt
import numpy as np


def read_log_files(folder_path):
    data = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Adjust the extension if needed
            with open(os.path.join(folder_path, filename), "r") as file:
                for line in file:
                    if line.startswith("Final stats:"):
                        stats = ast.literal_eval(line[len("Final stats: "):].strip())
                        engine = stats["engine"]
                        nodes = stats["nodes"]
                        time = stats["time"]

                        if engine not in data:
                            data[engine] = {"nodes": [], "time": []}

                        data[engine]["nodes"].append(nodes)
                        data[engine]["time"].append(time)

    return data


def plot_data(data):
    engines = list(data.keys())
    avg_nodes = [np.mean(stats["nodes"]) for stats in data.values()]
    print(avg_nodes)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.bar(engines, avg_nodes, color='b', alpha=0.6, label='Avg Nodes Processed')

    ax1.set_xlabel("Engine")
    ax1.set_ylabel("Avg Nodes Processed", color='b')

    ax1.set_title("Engine Performance Comparison")

    fig.legend(loc='upper right')
    plt.show()


if __name__ == "__main__":
    folder_path = "./logs"  # Change this to your actual log directory
    data = read_log_files(folder_path)
    if data:
        plot_data(data)
    else:
        print("No log data found.")