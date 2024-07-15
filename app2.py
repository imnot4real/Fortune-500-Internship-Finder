import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class InternshipFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internship Finder")
        
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Import CSV File with URLs:")
        self.label.pack(pady=10)
        
        self.import_button = tk.Button(self.root, text="Import CSV", command=self.import_csv)
        self.import_button.pack(pady=5)
        
        self.entries_label = tk.Label(self.root, text="Number of Entries to Search Through:")
        self.entries_label.pack(pady=10)
        
        self.entries_entry = tk.Entry(self.root)
        self.entries_entry.pack(pady=5)
        
        self.search_button = tk.Button(self.root, text="Search Internships", command=self.search_internships)
        self.search_button.pack(pady=20)
        
        self.result_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=20)
        self.result_text.pack(pady=10)
        
    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_path = file_path
            messagebox.showinfo("Success", "CSV File Imported Successfully!")
        else:
            messagebox.showwarning("Warning", "No File Selected!")
    
    def search_internships(self):
        try:
            num_entries = int(self.entries_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of entries!")
            return
        
        if not hasattr(self, 'csv_path'):
            messagebox.showerror("Error", "Please import a CSV file first!")
            return
        
        df = pd.read_csv(self.csv_path)
        
        for idx, row in df.iterrows():
            if idx >= num_entries:
                break
            
            url = row[0]
            self.result_text.insert(tk.END, f"Searching internships on: {url}\n")
            self.root.update()
            
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find('form', {'action': '/en/search', 'method': 'get'})
                
                if not form:
                    self.result_text.insert(tk.END, "No form found.\n\n")
                    continue
                
                search_box = form.find('input', {'type': 'text', 'name': 'base_query'})
                if not search_box:
                    self.result_text.insert(tk.END, "No search box found.\n\n")
                    continue
                
                form_action = form.get('action')
                search_url = urljoin(url, form_action)
                form_data = {input_tag.get('name'): 'internships' if input_tag.get('name') == 'base_query' else input_tag.get('value', '') for input_tag in form.find_all('input')}
                
                form_method = form.get('method', 'get').lower()
                if form_method == 'post':
                    search_response = requests.post(search_url, data=form_data)
                else:
                    search_response = requests.get(search_url, params=form_data)
                
                search_soup = BeautifulSoup(search_response.text, 'html.parser')
                results = search_soup.find_all('a', href=True, text=True)[:2]
                if results:
                    for result in results:
                        self.result_text.insert(tk.END, f"Result: {result.text} - {urljoin(search_url, result['href'])}\n")
                else:
                    self.result_text.insert(tk.END, "No results found.\n\n")
                    
            except Exception as e:
                self.result_text.insert(tk.END, f"Error searching {url}: {e}\n\n")
            
        messagebox.showinfo("Completed", "Search completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = InternshipFinderApp(root)
    root.mainloop()
