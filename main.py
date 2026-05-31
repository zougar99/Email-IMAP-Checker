#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email IMAP Checker Pro v3.5
Main Launcher with Mode Selection
"""

import sys
import os

# Check Python version
if sys.version_info < (3, 6):
    print("=" * 60)
    print("ERROR: Python 3.6+ is required!")
    print(f"Current version: {sys.version}")
    print("Please install Python 3.6 or higher.")
    print("=" * 60)
    sys.exit(1)

def print_banner():
    banner = """
\033[96m╔══════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   ███████╗███╗   ███╗ █████╗ ██╗██╗          ██████╗██╗  ██╗      ║
║   ██╔════╝████╗ ████║██╔══██╗██║██║         ██╔════╝██║ ██╔╝      ║
║   █████╗  ██╔████╔██║███████║██║██║         ██║     █████╔╝       ║
║   ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ██║     ██╔═██╗       ║
║   ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ╚██████╗██║  ██╗      ║
║   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝      ║
║                                                                    ║
║                  \033[93m⚡ PRO VERSION 3.5 ⚡\033[96m                          ║
║                                                                    ║
║   \033[92m✓ 1,833 Global Email Providers\033[96m                              ║
║   \033[92m✓ 100+ Countries Supported\033[96m                                  ║
║   \033[92m✓ Multi-threaded IMAP Validation\033[96m                            ║
║   \033[92m✓ Professional Modern GUI\033[96m                                   ║
║   \033[92m✓ Real-time Statistics\033[96m                                      ║
║   \033[92m✓ ISP/Boite Sorting\033[96m                                         ║
║                                                                    ║
║                      Telegram: @werlist99                          ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════╝\033[0m
"""
    print(banner)

def print_menu():
    menu = """
\033[97m╔════════════════════════════════════════════════════════╗
║                   \033[93mSELECT MODE\033[97m                          ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║   \033[96m[1]\033[0m  🖥️  \033[97mGUI Mode\033[0m         - Professional Interface    ║
║   \033[96m[2]\033[0m  💻  \033[97mCLI Mode\033[0m         - Command Line Interface    ║
║   \033[96m[3]\033[0m  🤖  \033[97mAuto Monitor\033[0m     - Watch & Process Files     ║
║   \033[96m[4]\033[0m  📊  \033[97mStatistics\033[0m       - View Results & Stats      ║
║   \033[96m[5]\033[0m  📖  \033[97mHelp\033[0m             - Show Documentation        ║
║   \033[96m[6]\033[0m  🚪  \033[97mExit\033[0m             - Quit Application          ║
║                                                        ║
╚════════════════════════════════════════════════════════╝\033[0m
"""
    print(menu)

def show_help():
    help_text = """
\033[96m╔════════════════════════════════════════════════════════════════╗
║                        DOCUMENTATION                            ║
╠════════════════════════════════════════════════════════════════╣\033[0m

\033[93m📁 FILE STRUCTURE:\033[0m
   • input.txt       - Email:Password list to check
   • hoster.dat      - IMAP server configurations (1,833 providers)
   • matchers.dat    - Email search patterns for grabbing

\033[93m📤 OUTPUT FOLDERS:\033[0m
   • M-P-V-I/        - Main output directory
     └── YYYY-MM-DD_HH-MM-SS/
         ├── mail_pass_valid.txt      - Valid emails only
         ├── mail_pass_invalid.txt    - Invalid emails
         └── valid_with_passwords/    - Valid with passwords
   • isp+boite/      - Emails sorted by domain/provider

\033[93m⚙️ CLI OPTIONS:\033[0m
   -i, --input       Input file (default: mail_pass.txt)
   -t, --threads     Number of concurrent threads (default: 1000)
   -to, --timeout    Connection timeout in seconds (default: 5)
   -uh               Check unknown hosts (default: True)
   -iu               Save invalid emails (default: True)
   -g                Grab email contents (default: False)

\033[93m💡 TIPS:\033[0m
   • Use 500-1000 threads for optimal performance
   • Set timeout to 5-10 seconds for reliable results
   • Enable "Grab Emails" to search inbox contents

\033[96m╚════════════════════════════════════════════════════════════════╝\033[0m

Press Enter to continue..."""
    print(help_text)
    input()

def run_gui():
    print("\n\033[92m[*] Launching GUI Mode...\033[0m\n")
    try:
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"\033[91m[ERROR] Failed to import GUI: {e}\033[0m")
        print("\033[93m[*] Make sure tkinter is installed.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] {e}\033[0m")

def run_cli():
    print("\n\033[92m[*] Launching CLI Mode...\033[0m")
    print("\033[97m" + "=" * 60 + "\033[0m")
    
    input_file = input("\033[96m[?] Input file (default: input.txt): \033[0m").strip()
    if not input_file:
        input_file = "input.txt"
        
    threads = input("\033[96m[?] Threads (default: 500): \033[0m").strip()
    if not threads:
        threads = "500"
        
    timeout = input("\033[96m[?] Timeout in seconds (default: 5): \033[0m").strip()
    if not timeout:
        timeout = "5"
        
    print("\n\033[97m" + "=" * 60 + "\033[0m")
    print("\033[92m[*] Starting checker...\033[0m\n")
    
    import subprocess
    subprocess.run([
        sys.executable, "atr3.py",
        "-i", input_file,
        "-t", threads,
        "-to", timeout
    ])

def run_auto_monitor():
    print("\n\033[92m[*] Launching Auto Monitor Mode...\033[0m")
    print("\033[93m[*] Watching for changes in input.txt...\033[0m")
    print("\033[93m[*] Press Ctrl+C to stop.\033[0m\n")
    
    import subprocess
    try:
        subprocess.run([sys.executable, "auto_checker.py"])
    except KeyboardInterrupt:
        print("\n\033[92m[*] Monitor stopped.\033[0m")

def show_statistics():
    print("\n\033[92m[*] Loading Statistics...\033[0m\n")
    
    try:
        # Try to import and run stats module
        import subprocess
        subprocess.run([sys.executable, "stats.py"])
    except:
        # Manual stats display
        print("\033[96m╔════════════════════════════════════════════════════════╗")
        print("║                   STATISTICS SUMMARY                    ║")
        print("╠════════════════════════════════════════════════════════╣\033[0m")
        
        # Count hoster.dat
        try:
            with open("hoster.dat", "r", encoding='utf-8', errors='ignore') as f:
                providers = sum(1 for line in f if line.strip() and not line.startswith('#') and ':' in line)
            print(f"\033[97m║  Email Providers:    {providers:>30} ║\033[0m")
        except:
            print("\033[97m║  Email Providers:    Unable to read                     ║\033[0m")
            
        # Check output folders
        if os.path.exists("M-P-V-I"):
            folders = os.listdir("M-P-V-I")
            print(f"\033[97m║  Result Folders:     {len(folders):>30} ║\033[0m")
        else:
            print("\033[97m║  Result Folders:     0                                  ║\033[0m")
            
        # Check ISP folders
        if os.path.exists("isp+boite"):
            isp_files = [f for f in os.listdir("isp+boite") if f.endswith('.txt')]
            total_emails = 0
            for f in isp_files:
                try:
                    with open(os.path.join("isp+boite", f), 'r', encoding='utf-8') as file:
                        total_emails += sum(1 for _ in file)
                except:
                    pass
            print(f"\033[97m║  ISP/Boite Files:    {len(isp_files):>30} ║\033[0m")
            print(f"\033[97m║  Sorted Emails:      {total_emails:>30} ║\033[0m")
        else:
            print("\033[97m║  ISP/Boite Files:    0                                  ║\033[0m")
            
        print("\033[96m╚════════════════════════════════════════════════════════╝\033[0m\n")
        
    input("Press Enter to continue...")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        print_banner()
        print_menu()
        
        choice = input("\033[93m[?] Enter your choice (1-6): \033[0m").strip()
        
        if choice == "1":
            run_gui()
            break
        elif choice == "2":
            run_cli()
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
        elif choice == "3":
            run_auto_monitor()
            os.system('cls' if os.name == 'nt' else 'clear')
        elif choice == "4":
            show_statistics()
            os.system('cls' if os.name == 'nt' else 'clear')
        elif choice == "5":
            os.system('cls' if os.name == 'nt' else 'clear')
            show_help()
            os.system('cls' if os.name == 'nt' else 'clear')
        elif choice == "6":
            print("\n\033[92m[*] Goodbye!\033[0m\n")
            break
        else:
            print("\n\033[91m[!] Invalid choice. Please try again.\033[0m")
            input("Press Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
