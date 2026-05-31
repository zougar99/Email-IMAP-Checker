#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email IMAP Checker - Statistics Analyzer
Comprehensive results analysis and reporting
"""

import os
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def colorize(text, color):
    """Add ANSI color codes"""
    colors = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'gray': '\033[90m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def print_header():
    header = f"""
{colorize('╔══════════════════════════════════════════════════════════════════╗', 'cyan')}
{colorize('║', 'cyan')}       {colorize('📊 EMAIL IMAP CHECKER - STATISTICS ANALYZER 📊', 'yellow')}        {colorize('║', 'cyan')}
{colorize('╚══════════════════════════════════════════════════════════════════╝', 'cyan')}
"""
    print(header)

def count_lines(filepath):
    """Count lines in a file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for line in f if line.strip())
    except:
        return 0

def analyze_providers():
    """Analyze hoster.dat providers"""
    print(colorize('\n┌─────────────────────────────────────────────────────────────┐', 'cyan'))
    print(colorize('│              📡 EMAIL PROVIDERS DATABASE                    │', 'cyan'))
    print(colorize('└─────────────────────────────────────────────────────────────┘', 'cyan'))
    
    if not os.path.exists('hoster.dat'):
        print(colorize('  ⚠ hoster.dat not found!', 'yellow'))
        return
        
    regions = defaultdict(int)
    total_providers = 0
    
    try:
        with open('hoster.dat', 'r', encoding='utf-8', errors='ignore') as f:
            current_region = "Global"
            for line in f:
                line = line.strip()
                if line.startswith('# ') and '(' in line:
                    # Extract region name
                    current_region = line[2:].split('(')[0].strip()
                    if current_region.startswith('EXTENDED '):
                        current_region = current_region[9:]
                elif line and not line.startswith('#') and ':' in line:
                    total_providers += 1
                    regions[current_region] += 1
                    
        print(f"\n  {colorize('Total Providers:', 'white')} {colorize(str(total_providers), 'green')}")
        print(f"  {colorize('Total Regions:', 'white')} {colorize(str(len(regions)), 'green')}\n")
        
        # Top regions
        print(colorize('  Top Regions:', 'yellow'))
        sorted_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:15]
        for region, count in sorted_regions:
            bar_length = int(count / max(r[1] for r in sorted_regions) * 30)
            bar = colorize('█' * bar_length, 'cyan')
            print(f"    {region:30} {bar} {colorize(str(count), 'green')}")
            
    except Exception as e:
        print(colorize(f'  Error reading hoster.dat: {e}', 'red'))

def analyze_results():
    """Analyze checking results"""
    print(colorize('\n┌─────────────────────────────────────────────────────────────┐', 'cyan'))
    print(colorize('│              📈 CHECKING RESULTS                            │', 'cyan'))
    print(colorize('└─────────────────────────────────────────────────────────────┘', 'cyan'))
    
    output_dir = Path('M-P-V-I')
    
    if not output_dir.exists():
        print(colorize('  ⚠ No results found (M-P-V-I folder not found)', 'yellow'))
        return
        
    # Get all result folders
    result_folders = sorted(output_dir.iterdir(), key=os.path.getmtime, reverse=True)
    
    if not result_folders:
        print(colorize('  ⚠ No result folders found', 'yellow'))
        return
        
    total_valid = 0
    total_invalid = 0
    
    print(f"\n  {colorize('Result Sessions:', 'white')} {colorize(str(len(result_folders)), 'green')}\n")
    
    # Analyze each folder
    print(colorize('  Recent Sessions:', 'yellow'))
    for i, folder in enumerate(result_folders[:10]):  # Last 10 sessions
        valid_file = folder / 'mail_pass_valid.txt'
        invalid_file = folder / 'mail_pass_invalid.txt'
        
        valid = count_lines(valid_file)
        invalid = count_lines(invalid_file)
        total = valid + invalid
        
        total_valid += valid
        total_invalid += invalid
        
        folder_name = folder.name
        success_rate = (valid / total * 100) if total > 0 else 0
        
        # Color based on success rate
        rate_color = 'green' if success_rate >= 50 else 'yellow' if success_rate >= 20 else 'red'
        
        print(f"    {colorize(folder_name, 'gray')} │ ", end='')
        print(f"Valid: {colorize(str(valid).rjust(6), 'green')} │ ", end='')
        print(f"Invalid: {colorize(str(invalid).rjust(6), 'red')} │ ", end='')
        print(f"Rate: {colorize(f'{success_rate:.1f}%'.rjust(6), rate_color)}")
        
    # Summary
    total = total_valid + total_invalid
    overall_rate = (total_valid / total * 100) if total > 0 else 0
    
    print(f"\n  {colorize('═' * 55, 'cyan')}")
    print(f"  {colorize('TOTAL', 'bold')} │ Valid: {colorize(str(total_valid).rjust(6), 'green')} │ Invalid: {colorize(str(total_invalid).rjust(6), 'red')} │ Rate: {colorize(f'{overall_rate:.1f}%'.rjust(6), 'yellow')}")

def analyze_isp_distribution():
    """Analyze ISP/Boite distribution"""
    print(colorize('\n┌─────────────────────────────────────────────────────────────┐', 'cyan'))
    print(colorize('│              🌐 ISP/BOITE DISTRIBUTION                      │', 'cyan'))
    print(colorize('└─────────────────────────────────────────────────────────────┘', 'cyan'))
    
    isp_dir = Path('isp+boite')
    
    if not isp_dir.exists():
        print(colorize('  ⚠ No ISP data found (isp+boite folder not found)', 'yellow'))
        return
        
    isp_counts = []
    
    for file in isp_dir.glob('mail_*.txt'):
        count = count_lines(file)
        if count > 0:
            isp_name = file.stem[5:]  # Remove "mail_" prefix
            isp_counts.append((isp_name, count))
            
    if not isp_counts:
        print(colorize('  ⚠ No ISP files found', 'yellow'))
        return
        
    # Sort by count
    isp_counts.sort(key=lambda x: x[1], reverse=True)
    
    total_emails = sum(c for _, c in isp_counts)
    
    print(f"\n  {colorize('Total ISPs:', 'white')} {colorize(str(len(isp_counts)), 'green')}")
    print(f"  {colorize('Total Emails:', 'white')} {colorize(str(total_emails), 'green')}\n")
    
    print(colorize('  Top ISPs/Boites:', 'yellow'))
    max_count = isp_counts[0][1] if isp_counts else 1
    
    for isp, count in isp_counts[:20]:
        bar_length = int(count / max_count * 25)
        bar = colorize('█' * bar_length, 'cyan')
        percentage = (count / total_emails * 100)
        print(f"    {isp:30} {bar} {colorize(str(count).rjust(6), 'green')} ({colorize(f'{percentage:.1f}%', 'yellow')})")
        
    if len(isp_counts) > 20:
        remaining = len(isp_counts) - 20
        remaining_count = sum(c for _, c in isp_counts[20:])
        print(colorize(f"\n    ... and {remaining} more ISPs with {remaining_count} emails", 'gray'))

def analyze_matchers():
    """Analyze matchers configuration"""
    print(colorize('\n┌─────────────────────────────────────────────────────────────┐', 'cyan'))
    print(colorize('│              🔍 EMAIL SEARCH MATCHERS                       │', 'cyan'))
    print(colorize('└─────────────────────────────────────────────────────────────┘', 'cyan'))
    
    if not os.path.exists('matchers.dat'):
        print(colorize('  ⚠ matchers.dat not found!', 'yellow'))
        return
        
    try:
        with open('matchers.dat', 'r', encoding='utf-8', errors='ignore') as f:
            matchers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        print(f"\n  {colorize('Total Matchers:', 'white')} {colorize(str(len(matchers)), 'green')}\n")
        
        if matchers:
            print(colorize('  Configured Patterns:', 'yellow'))
            for matcher in matchers[:10]:
                parts = matcher.split('|')
                if len(parts) >= 3:
                    print(f"    • {colorize(parts[2].strip(), 'cyan')}: {colorize(parts[1].strip(), 'gray')}")
                    
    except Exception as e:
        print(colorize(f'  Error reading matchers.dat: {e}', 'red'))

def show_summary():
    """Show final summary"""
    print(colorize('\n╔══════════════════════════════════════════════════════════════════╗', 'cyan'))
    print(colorize('║                      📋 QUICK SUMMARY                           ║', 'cyan'))
    print(colorize('╚══════════════════════════════════════════════════════════════════╝', 'cyan'))
    
    # Providers
    providers = 0
    if os.path.exists('hoster.dat'):
        with open('hoster.dat', 'r', encoding='utf-8', errors='ignore') as f:
            providers = sum(1 for line in f if line.strip() and not line.startswith('#') and ':' in line)
            
    # Results
    valid_total = 0
    invalid_total = 0
    if os.path.exists('M-P-V-I'):
        for folder in Path('M-P-V-I').iterdir():
            valid_total += count_lines(folder / 'mail_pass_valid.txt')
            invalid_total += count_lines(folder / 'mail_pass_invalid.txt')
            
    # ISPs
    isp_count = 0
    if os.path.exists('isp+boite'):
        isp_count = len(list(Path('isp+boite').glob('mail_*.txt')))
        
    print(f"""
  ┌────────────────────────────────┬──────────────┐
  │ {colorize('Email Providers', 'white')}               │ {colorize(str(providers).rjust(12), 'cyan')} │
  ├────────────────────────────────┼──────────────┤
  │ {colorize('Valid Emails (Total)', 'white')}          │ {colorize(str(valid_total).rjust(12), 'green')} │
  ├────────────────────────────────┼──────────────┤
  │ {colorize('Invalid Emails (Total)', 'white')}        │ {colorize(str(invalid_total).rjust(12), 'red')} │
  ├────────────────────────────────┼──────────────┤
  │ {colorize('ISP/Boite Categories', 'white')}          │ {colorize(str(isp_count).rjust(12), 'yellow')} │
  └────────────────────────────────┴──────────────┘
""")

def main():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_header()
    
    # Run all analyses
    analyze_providers()
    analyze_results()
    analyze_isp_distribution()
    analyze_matchers()
    show_summary()
    
    print(colorize('\n  Press Enter to exit...', 'gray'))
    input()

if __name__ == "__main__":
    main()
