import os
import ast
import matplotlib.pyplot as plt
import numpy as np


def decode_bytes(data):
    return {k.decode('utf-8') if isinstance(k, bytes) else k:
                v.decode('utf-8') if isinstance(v, bytes) else v
            for k, v in data.items()}


def read_log_files(folder_path):
    data = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Adjust the extension if needed
            with open(os.path.join(folder_path, filename), "rb") as file:  # Open in binary mode
                for line in file:
                    if line.startswith(b"Final stats:"):  # Note the byte prefix
                        # Decode line and remove 'Final stats: '
                        line_str = line[len(b"Final stats: "):].strip()

                        # Evaluate the dictionary safely
                        try:
                            stats = ast.literal_eval(line_str.decode('utf-8'))
                            stats = decode_bytes(stats)  # Decode byte strings in the dictionary
                        except Exception as e:
                            print(f"Error processing line: {e}")
                            continue  # Skip lines that can't be processed

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