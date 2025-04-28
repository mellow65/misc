import sys
import tkinter as tk
from tkinter import messagebox

def check_tkinter():
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter is not available in this environment.")
        sys.exit(1)

check_tkinter()

def validate_paths(source, destination):
    if source.endswith('/'):
        messagebox.showwarning("Warning", "Source should not have a trailing '/'. It has been removed.")
        source = source.rstrip('/')
    if destination.endswith('/'):
        messagebox.showwarning("Warning", "Destination should not have a trailing '/'. It has been removed.")
        destination = destination.rstrip('/')
    return source, destination

def generate_rsync_script():
    source = source_entry.get().strip()
    destination = destination_entry.get().strip()
    
    if not source or not destination:
        messagebox.showerror("Error", "Both source and destination are required.")
        return
    
    source, destination = validate_paths(source, destination)
    
    link_dest = f"{destination}/last"
    destination_with_date = f"{destination}/$(date +%Y-%m-%d)"
    
    options = ["-a", "-v", "--delete"]
    if compress_var.get():
        options.append("-z")
    if progress_var.get():
        options.append("-P")
    
    options.append(f"--link-dest={link_dest}")
    
    exclude_text = exclude_entry.get().strip()
    if exclude_text:
        for pattern in exclude_text.split(','):
            options.append(f"--exclude='{pattern.strip()}'")
    
    rsync_command = f"rsync {' '.join(options)} {source} {destination_with_date}"
    
    # Pruning settings
    daily = daily_var.get()
    weekly = weekly_var.get()
    monthly = monthly_var.get()
    
    prune_script = f"""
    find "$dest" -maxdepth 1 -name "20*" -type d | sort | while read -r backup; do
        backup_date=$(basename "$backup")
        backup_ts=$(date -d "$backup_date" +%s)
        now_ts=$(date +%s)


        # Calculate age in days
        age_days=$(( (now_ts - backup_ts) / 86400 ))
    
        # 1. Delete backups older than 180 days
        if (( age_days > 180 )); then
            #echo "Deleting backup older than 180 days: $backup"
            rm -rf "$backup"

        # 2. Delete backups between 30-180 days that are NOT the 1st of the month
        elif (( age_days > 30 && age_days <= 180 )); then
            if (( $(date -d "$backup_date" +%e) != 1 )); then
                #echo "Deleting backup (not first of the month) in 30-180 day range: $backup"
                rm -rf "$backup"
            fi

        # 3. Delete backups between 7-30 days that are NOT Sundays or the 1st of the month
        elif (( age_days > 7 && age_days <= 30 )); then
            day_of_week=$(date -d "$backup_date" +%u)  # 1=Monday, 7=Sunday
            day_of_month=$(date -d "$backup_date" +%e) # No zero-padding

            if (( day_of_week != 7 && day_of_month != 1 )); then
                #echo "Deleting backup (not Sunday or 1st of the month) in 7-30 day range: $backup"
                rm -rf "$backup"
            fi
        #else echo "Done"
    
        fi
done
"""

    
    full_script = f"""
    #!/bin/bash
    
    src="{source}"
    dest="{destination}"
    new_backup="{destination_with_date}"
    last_backup="{link_dest}"
    
    {rsync_command}
    
    rm -f $last_backup
    ln -s $new_backup $last_backup
    
    {prune_script}
    """
    
    output_text.set(full_script.strip())

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get())
    root.update()
    messagebox.showinfo("Copied", "Script copied to clipboard!")

def show_help(message):
    messagebox.showinfo("Option Help", message)

root = tk.Tk()
root.title("Rsync Backup Script Generator")

tk.Label(root, text="Source Directory:").grid(row=0, column=0, sticky='w')
source_entry = tk.Entry(root, width=50)
source_entry.grid(row=0, column=1)

tk.Label(root, text="Destination Directory:").grid(row=1, column=0, sticky='w')
destination_entry = tk.Entry(root, width=50)
destination_entry.grid(row=1, column=1)

# Exclusion Patterns
tk.Label(root, text="Exclude Patterns (comma-separated):").grid(row=2, column=0, sticky='w')
exclude_entry = tk.Entry(root, width=50)
exclude_entry.grid(row=2, column=1)

# Rsync Options
compress_var = tk.BooleanVar()
progress_var = tk.BooleanVar()

tk.Checkbutton(root, text="Compress (-z)", variable=compress_var).grid(row=3, column=0, sticky='w')
tk.Checkbutton(root, text="Progress (-P)", variable=progress_var).grid(row=3, column=1, sticky='w')

# Retention Settings
tk.Label(root, text="Retention Settings:").grid(row=4, column=0, sticky='w')
daily_var = tk.IntVar(value=7)
weekly_var = tk.IntVar(value=30)
monthly_var = tk.IntVar(value=180)

tk.Label(root, text="Daily Backups:").grid(row=5, column=0, sticky='w')
daily_entry = tk.Entry(root, textvariable=daily_var, width=5)
daily_entry.grid(row=5, column=1, sticky='w')

tk.Label(root, text="Weekly Backups:").grid(row=6, column=0, sticky='w')
weekly_entry = tk.Entry(root, textvariable=weekly_var, width=5)
weekly_entry.grid(row=6, column=1, sticky='w')

tk.Label(root, text="Monthly Backups:").grid(row=7, column=0, sticky='w')
monthly_entry = tk.Entry(root, textvariable=monthly_var, width=5)
monthly_entry.grid(row=7, column=1, sticky='w')

# Generate Button
generate_button = tk.Button(root, text="Generate Script", command=generate_rsync_script)
generate_button.grid(row=8, column=0, columnspan=2, pady=10)

# Output Field
output_text = tk.StringVar()
output_entry = tk.Entry(root, textvariable=output_text, width=70, state='readonly')
output_entry.grid(row=9, column=0, columnspan=2)

# Copy to Clipboard Button
copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.grid(row=10, column=0, columnspan=2, pady=5)

root.mainloop()
