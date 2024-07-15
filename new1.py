import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from googlesearch import search
import threading
import webbrowser
import csv
import os

class CareerPageFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Company Career Page Finder")
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # File selection
        file_frame = ttk.Frame(self.root, padding="10")
        file_frame.pack(fill=tk.X)

        ttk.Label(file_frame, text="Select CSV file:").pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)

        # Number of entries input
        entries_frame = ttk.Frame(self.root, padding="10")
        entries_frame.pack(fill=tk.X)

        ttk.Label(entries_frame, text="Number of companies to search:").pack(side=tk.LEFT)
        self.entries_var = tk.StringVar(value="10")
        self.entries_entry = ttk.Entry(entries_frame, textvariable=self.entries_var, width=10)
        self.entries_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Start button
        ttk.Button(self.root, text="Start Search", command=self.start_search).pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)

        # Results treeview
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("Company", "Career Page URL"), show="headings")
        self.tree.heading("Company", text="Company")
        self.tree.heading("Career Page URL", text="Career Page URL")
        self.tree.column("Company", width=200)
        self.tree.column("Career Page URL", width=600)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Vertical scrollbar for treeview
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar for treeview
        hsb = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscroll=hsb.set)
        hsb.pack(fill=tk.X)

        # Bind click event to treeview
        self.tree.bind("<Double-1>", self.on_tree_double_click)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def start_search(self):
        csv_file = self.file_entry.get()
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file.")
            return

        try:
            num_entries = int(self.entries_var.get())
            if num_entries <= 0:
                raise ValueError("Number of entries must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for companies to search.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Start searching in a separate thread
        threading.Thread(target=self.search_career_pages, args=(csv_file, num_entries), daemon=True).start()

    def search_career_pages(self, csv_file, num_entries):
        try:
            company_list = self.read_company_list(csv_file)[:num_entries]
            total_companies = len(company_list)
            results = []

            for i, company in enumerate(company_list, 1):
                career_page = self.get_company_career_page(company)
                if career_page:
                    self.tree.insert("", tk.END, values=(company, career_page))
                    results.append((company, career_page))
                
                # Update progress
                progress = (i / total_companies) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            # Save results to CSV
            output_file = self.save_results_to_csv(results)
            messagebox.showinfo("Search Complete", f"Career page search has finished. Results saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def read_company_list(self, csv_file):
        df = pd.read_csv(csv_file)
        return df['company'].tolist()

    def get_company_career_page(self, company_name):
        query = f"{company_name} careers"
        try:
            for url in search(query, num=1, stop=1):
                return url
        except Exception as e:
            print(f"Error searching for {company_name}: {str(e)}")
            return None

    def save_results_to_csv(self, results):
        output_file = "career_pages_results.csv"
        base_name = "career_pages_results"
        counter = 1

        while os.path.exists(output_file):
            output_file = f"{base_name}_{counter}.csv"
            counter += 1

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Company", "Career Page URL"])
            writer.writerows(results)

        return output_file

    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        url = self.tree.item(item, "values")[1]
        webbrowser.open_new(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = CareerPageFinderApp(root)
    root.mainloop()