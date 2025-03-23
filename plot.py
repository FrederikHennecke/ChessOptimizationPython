import os
import ast
import re

import matplotlib
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

    ax1.set_yscale('log')

    ax1.set_title("Engine Performance Comparison")

    fig.legend(loc='upper right')
    plt.show()


if __name__ == "__main__":
    FONT_SIZE = 16
    matplotlib.rcParams.update({'font.size': FONT_SIZE})

    folder_path = "./logs"  # Change this to your actual log directory
    data = read_log_files(folder_path)
    if data:
        plot_data(data)
    else:
        print("No log data found.")


def parse_log_file(filename):
    matchups = []
    elo_differences = []
    results = {}

    with open(filename, 'r') as file:
        content = file.read()

    matches = re.findall(r'Score of (\w+) vs (\w+): (\d+) - (\d+) - (\d+)  \[0.\d+\] \d+\n.*\n.*\n.*\nElo difference: ([\d.-]+) \+/- ([\d.]+).*\n.*\n\nPlayer', content)

    for (engine1, engine2, win, loss, draw, elo_diff, _) in matches:
        total_games = int(win) + int(loss) + int(draw)
        win_rate = int(win) / total_games * 100
        loss_rate = int(loss) / total_games * 100
        draw_rate = int(draw) / total_games * 100

        matchup = f"{engine1} vs {engine2}"
        matchups.append(matchup)
        elo_differences.append(float(elo_diff))
        results[matchup] = (win_rate, loss_rate, draw_rate)

    return matchups, results, elo_differences


def plot_results(matchups, results, elo_differences):
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))

    # Plot Win/Loss/Draw rates
    bar_width = 0.25
    x = np.arange(len(matchups))
    win_rates = [results[m][0] for m in matchups]
    loss_rates = [results[m][1] for m in matchups]
    draw_rates = [results[m][2] for m in matchups]

    axs[0].bar(x - bar_width, win_rates, bar_width, label='Win Rate', color='green')
    axs[0].bar(x, draw_rates, bar_width, label='Draw Rate', color='gray')
    axs[0].bar(x + bar_width, loss_rates, bar_width, label='Loss Rate', color='red')
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(matchups, rotation=45, ha='right')
    axs[0].set_ylabel("Percentage (%)")
    axs[0].set_title("Win/Loss/Draw Rates per Matchup")
    axs[0].legend()

    # Plot Elo differences
    axs[1].bar(x, elo_differences, color='blue', alpha=0.7)
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(matchups, rotation=45, ha='right')
    axs[1].set_ylabel("Elo Difference")
    axs[1].set_title("Elo Differences per Matchup")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    filename = "logss2.txt"  # Change this to your log file
    matchups, results, elo_differences = parse_log_file(filename)
    print(matchups)
    plot_results(matchups, results, elo_differences)