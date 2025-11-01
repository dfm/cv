#!/usr/bin/env python3
"""
Investigate the citation count spike in the data.
"""

import subprocess
import re
from datetime import datetime

def get_commit_history():
    """Get list of commits that modified pubs_summary.tex with timestamps."""
    cmd = ['git', 'log', '--all', '--format=%H %ai', '--', 'tex/pubs_summary.tex']
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split()
            commit_hash = parts[0]
            date_str = ' '.join(parts[1:4])
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
            commits.append((commit_hash, date))

    return commits

def extract_data_from_commit(commit_hash):
    """Extract citations and h-index from a specific commit."""
    cmd = ['git', 'show', f'{commit_hash}:tex/pubs_summary.tex']
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return None, None, None

    content = result.stdout

    # Parse the format
    citations_match = re.search(r'citations:\s*([\d,]+)', content)
    h_index_match = re.search(r'h-index:\s*(\d+)', content)

    citations = None
    h_index = None

    if citations_match:
        citations = int(citations_match.group(1).replace(',', ''))

    if h_index_match:
        h_index = int(h_index_match.group(1))

    return citations, h_index, content

def main():
    print("Extracting commit history...")
    commits = get_commit_history()
    print(f"Found {len(commits)} commits")

    # Extract all data to find the spike
    data = []
    print("Extracting data from each commit...")
    for i, (commit_hash, date) in enumerate(commits):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(commits)} commits...")

        cites, h_idx, content = extract_data_from_commit(commit_hash)

        if cites is not None:
            data.append((date, cites, h_idx, commit_hash, content))

    # Sort by date
    data.sort(key=lambda x: x[0])

    # Find large jumps in citations
    print("\nLooking for large citation jumps...")
    threshold = 5000  # Look for jumps larger than 5000 citations

    for i in range(1, len(data)):
        prev_date, prev_cites, prev_h, prev_hash, _ = data[i-1]
        curr_date, curr_cites, curr_h, curr_hash, curr_content = data[i]

        jump = curr_cites - prev_cites

        if abs(jump) > threshold:
            print(f"\n{'='*80}")
            print(f"Large jump found: {jump:+,} citations")
            print(f"{'='*80}")
            print(f"\nPrevious commit:")
            print(f"  Date: {prev_date}")
            print(f"  Hash: {prev_hash[:8]}")
            print(f"  Citations: {prev_cites:,}")
            print(f"  h-index: {prev_h}")

            print(f"\nCurrent commit:")
            print(f"  Date: {curr_date}")
            print(f"  Hash: {curr_hash[:8]}")
            print(f"  Citations: {curr_cites:,}")
            print(f"  h-index: {curr_h}")

            # Show the commit message
            cmd = ['git', 'log', '-1', '--format=%s', curr_hash]
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"  Commit message: {result.stdout.strip()}")

            # Show the content
            print(f"\nFile content at this commit:")
            print(f"  {curr_content.strip()}")

    # Find the maximum citation count
    max_cites = max(data, key=lambda x: x[1])
    print(f"\n{'='*80}")
    print(f"Maximum citation count in history: {max_cites[1]:,}")
    print(f"  Date: {max_cites[0]}")
    print(f"  Hash: {max_cites[3][:8]}")
    print(f"  Content: {max_cites[4].strip()}")

if __name__ == '__main__':
    main()
