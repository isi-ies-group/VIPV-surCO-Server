#!python3
"""
Plots session file sizes for different beacon counts and frequencies.

It calculates the size of CSV files generated by beacons transmitting data at
specified frequencies over a given session time.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def binary_size_formatter(x, pos):
    if x < 1e3:
        return f"{x:.1f} B"
    elif x < 1e6:
        return f"{x / 1e3:.1f} kB"
    elif x < 1e9:
        return f"{x / 1e6:.1f} MB"
    else:
        return f"{x / 1e9:.1f} GB"


def calculate_file_size(
    num_beacons, packet_size, frequency, session_time_hours, header_size=1024
):
    """
    Calculate CSV file size in bytes.

    Args:
        num_beacons: Number of beacons (n)
        packet_size: Size of each packet/line in characters
        frequency: Packet frequency (Hz)
        session_time_hours: Session duration in hours
        header_size: Fixed header size in bytes (default: 1KB)

    Returns:
        File size in bytes
    """
    session_time_seconds = session_time_hours * 3600
    total_packets = num_beacons * frequency * session_time_seconds

    # Each line has: packet + newline character (1 byte)
    line_size_bytes = packet_size + 1

    # Total size = header + (packets * line_size)
    total_size = header_size + (total_packets * line_size_bytes)

    return total_size


# Parameters
packet_size = 52  # characters per packet/line + newline character
header_size = 1024  # 1KB fixed header
beacon_counts = [3, 4, 5, 6]
frequencies = [1, 3, 10, 30]  # Hz
max_time_hours = 2

# Generate time points
time_points = np.linspace(0, max_time_hours, 25)

# Create plots
plt.figure(figsize=(15, 10))

for n in beacon_counts:
    for freq in frequencies:
        # Calculate file sizes for all time points
        file_sizes = calculate_file_size(n, packet_size, freq, time_points, header_size)

        # Plot
        plt.plot(
            time_points,
            file_sizes,
            label=f"{n} beacons, {freq}Hz",
            linewidth=2,
            marker="o" if freq == 1 else "",
            linestyle="-" if freq == 1 else "--",
        )

# Formatting
plt.title(f"CSV File Size vs Session Time\n(Packet Size: {packet_size} B, Header: {header_size} B)", fontsize=16)
plt.suptitle(
    "File Size Analysis for Different Beacon Counts and Frequencies", fontsize=20, y=1.02
)
plt.xlabel("Session Time (hours)")
plt.ylabel("File Size")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.xticks(np.arange(0, max_time_hours + 0.5, 0.5))
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(binary_size_formatter))
plt.tight_layout()

# Save and show
plt.savefig("csv_file_size_analysis.png", dpi=300, bbox_inches="tight")
plt.show()
