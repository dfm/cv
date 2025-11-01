#!/usr/bin/env python3
"""
Extract citation count and h-index from git history and plot over time.
"""

import subprocess
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patheffects as path_effects

def get_commit_history():
    """Get list of commits that modified pubs_summary.tex with timestamps."""
    cmd = ['git', 'log', '--all', '--format=%H %ai', '--', 'tex/pubs_summary.tex']
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split()
            commit_hash = parts[0]
            # Date format: YYYY-MM-DD HH:MM:SS +ZZZZ
            date_str = ' '.join(parts[1:4])
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
            commits.append((commit_hash, date))

    return commits

def extract_data_from_commit(commit_hash):
    """Extract citations and h-index from a specific commit."""
    cmd = ['git', 'show', f'{commit_hash}:tex/pubs_summary.tex']
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return None, None

    content = result.stdout

    # Parse the format: refereed: 110 / first author: 9 / citations: 28,054 / h-index: 51 (2025-11-01)
    citations_match = re.search(r'citations:\s*([\d,]+)', content)
    h_index_match = re.search(r'h-index:\s*(\d+)', content)

    citations = None
    h_index = None

    if citations_match:
        # Remove commas from citations number
        citations = int(citations_match.group(1).replace(',', ''))

    if h_index_match:
        h_index = int(h_index_match.group(1))

    return citations, h_index

def main():
    print("Extracting commit history...")
    all_commits = get_commit_history()
    print(f"Found {len(all_commits)} commits")

    # Sample every 10th commit to reduce processing time
    # But always include the first and last commits
    sample_rate = 10
    commits = []
    for i in range(0, len(all_commits), sample_rate):
        commits.append(all_commits[i])

    # Ensure we include the last commit if not already included
    if all_commits[-1] not in commits:
        commits.append(all_commits[-1])

    print(f"Sampling every {sample_rate}th commit, processing {len(commits)} commits...")

    # Extract data from each commit
    dates = []
    citations = []
    h_indices = []

    print("Extracting data from each commit...")
    for i, (commit_hash, date) in enumerate(commits):
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(commits)} commits...")

        cites, h_idx = extract_data_from_commit(commit_hash)

        if cites is not None and h_idx is not None:
            dates.append(date)
            citations.append(cites)
            h_indices.append(h_idx)

    print(f"Successfully extracted data from {len(dates)} commits")

    if len(dates) == 0:
        print("Error: No data extracted!")
        return

    # Sort by date (oldest to newest)
    sorted_data = sorted(zip(dates, citations, h_indices))
    dates, citations, h_indices = zip(*sorted_data)

    # Filter out single-day outliers
    # An outlier is a point where the value jumps significantly from the previous point
    # and then returns close to the trend the next day
    print("\nFiltering out single-day outliers...")
    filtered_data = []
    outliers_removed = 0

    for i in range(len(dates)):
        is_outlier = False

        # Check if this is a single-day spike/drop
        if 0 < i < len(dates) - 1:
            prev_cites = citations[i-1]
            curr_cites = citations[i]
            next_cites = citations[i+1]

            # Calculate changes
            jump_in = curr_cites - prev_cites
            jump_out = next_cites - curr_cites

            # If we jump far away and then jump back, it's likely an outlier
            # Use 5000 citations as threshold for "far"
            threshold = 5000

            # Detect spike: large increase then large decrease
            if jump_in > threshold and jump_out < -threshold:
                is_outlier = True
                print(f"  Removed spike at {dates[i].strftime('%Y-%m-%d')}: {curr_cites:,} citations")

            # Detect drop: large decrease then large increase
            elif jump_in < -threshold and jump_out > threshold:
                is_outlier = True
                print(f"  Removed drop at {dates[i].strftime('%Y-%m-%d')}: {curr_cites:,} citations")

        if not is_outlier:
            filtered_data.append((dates[i], citations[i], h_indices[i]))
        else:
            outliers_removed += 1

    print(f"Removed {outliers_removed} outlier(s)")

    if len(filtered_data) == 0:
        print("Error: No data after filtering!")
        return

    # Unpack filtered data
    dates, citations, h_indices = zip(*filtered_data)

    # Set style for beautiful plots
    plt.style.use('seaborn-v0_8-darkgrid')

    # Create the plot with better styling
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 11), sharex=True, facecolor='white')
    fig.patch.set_facecolor('white')

    # Calculate appropriate y-axis limits
    cit_min, cit_max = min(citations), max(citations)
    cit_range = cit_max - cit_min
    cit_padding = cit_range * 0.1 if cit_range > 0 else 100

    h_min, h_max = min(h_indices), max(h_indices)
    h_range = h_max - h_min
    h_padding = max(1, h_range * 0.2) if h_range > 0 else 1

    # Convert dates to numpy array for easier manipulation
    dates_array = np.array([d.timestamp() for d in dates])
    citations_array = np.array(citations)
    h_indices_array = np.array(h_indices)

    # ============== CITATIONS PLOT ==============
    # Plot line with gradient effect
    line1 = ax1.plot(dates, citations, linewidth=3, color='#2E86AB',
                     marker='o', markersize=4, markerfacecolor='#2E86AB',
                     markeredgecolor='white', markeredgewidth=1.5,
                     label='Citations', zorder=3)

    # Add shadow effect to the line
    line1[0].set_path_effects([path_effects.SimpleLineShadow(offset=(1, -1), alpha=0.3),
                                path_effects.Normal()])

    # Fill area under the curve with gradient
    ax1.fill_between(dates, citations, cit_min - cit_padding,
                     alpha=0.3, color='#2E86AB', zorder=1)

    # Styling
    ax1.set_ylabel('Citations', fontsize=18, fontweight='bold', color='#2E86AB')
    title_suffix = f' (outliers removed)' if outliers_removed > 0 else ''
    ax1.set_title(f'Academic Impact Over Time{title_suffix}',
                  fontsize=18, fontweight='bold', pad=20, color='#1a1a1a')
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax1.set_ylim(cit_min - cit_padding, cit_max + cit_padding)
    ax1.set_facecolor('#f9f9f9')
    ax1.tick_params(colors='#333333', labelsize=13)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#2E86AB')
    ax1.spines['left'].set_linewidth(2)
    ax1.spines['bottom'].set_color('#cccccc')

    # Add annotation for total growth
    growth_text = f'+{citations[-1] - citations[0]:,} citations'
    ax1.annotate(growth_text, xy=(dates[-1], citations[-1]),
                xytext=(-80, -25), textcoords='offset points',
                fontsize=11, fontweight='bold', color='#2E86AB',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                         edgecolor='#2E86AB', linewidth=2, alpha=0.9),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3',
                               color='#2E86AB', lw=2))

    # ============== H-INDEX PLOT ==============
    # Plot line with step effect
    line2 = ax2.plot(dates, h_indices, linewidth=3, color='#A23B72',
                     marker='o', markersize=4, markerfacecolor='#A23B72',
                     markeredgecolor='white', markeredgewidth=1.5,
                     label='h-index', zorder=3)

    # Add shadow effect
    line2[0].set_path_effects([path_effects.SimpleLineShadow(offset=(1, -1), alpha=0.3),
                                path_effects.Normal()])

    # Fill area under the curve
    ax2.fill_between(dates, h_indices, h_min - h_padding,
                     alpha=0.3, color='#A23B72', zorder=1)

    # Styling
    ax2.set_ylabel('h-index', fontsize=18, fontweight='bold', color='#A23B72')
    ax2.set_xlabel('Date', fontsize=18, fontweight='bold', color='#333333')
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax2.set_ylim(h_min - h_padding, h_max + h_padding)
    ax2.set_facecolor('#f9f9f9')
    ax2.tick_params(colors='#333333', labelsize=13)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#A23B72')
    ax2.spines['left'].set_linewidth(2)
    ax2.spines['bottom'].set_color('#333333')
    ax2.spines['bottom'].set_linewidth(2)

    # Add annotation for h-index growth
    h_growth_text = f'+{h_indices[-1] - h_indices[0]} points'
    ax2.annotate(h_growth_text, xy=(dates[-1], h_indices[-1]),
                xytext=(-80, 15), textcoords='offset points',
                fontsize=11, fontweight='bold', color='#A23B72',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                         edgecolor='#A23B72', linewidth=2, alpha=0.9),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3',
                               color='#A23B72', lw=2))

    # Format x-axis with better date formatting
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0, ha='center', fontsize=11)

    plt.tight_layout()

    # Save the plot
    output_file = 'citations_plot.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to {output_file}")

    # Print some statistics
    print(f"\nStatistics:")
    print(f"  Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
    print(f"  Citations: {citations[0]:,} → {citations[-1]:,} (Δ = {citations[-1] - citations[0]:,})")
    print(f"  h-index: {h_indices[0]} → {h_indices[-1]} (Δ = {h_indices[-1] - h_indices[0]})")

    # Calculate growth rates
    days_elapsed = (dates[-1] - dates[0]).days
    if days_elapsed > 0:
        citations_per_day = (citations[-1] - citations[0]) / days_elapsed
        print(f"  Average citations per day: {citations_per_day:.2f}")

if __name__ == '__main__':
    main()
