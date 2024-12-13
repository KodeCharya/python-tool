import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")
        self.history = []
        self.current_dir = os.getcwd()

        # Directory Display
        self.dir_label = tk.Label(self.root, text=self.current_dir, anchor="w")
        self.dir_label.pack(fill=tk.X, padx=5, pady=5)

        # File List
        self.file_list = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_list.bind("<Double-Button-1>", self.open_item)
        self.populate_file_list()

        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Buttons
        tk.Button(button_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Sort by Name", command=lambda: self.sort_items("name")).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Sort by Date", command=lambda: self.sort_items("date")).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Create File", command=self.create_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Create Folder", command=self.create_folder).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Rename", command=self.rename_item).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Copy", command=self.copy_item).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Move", command=self.move_item).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Change Directory", command=self.change_directory).pack(side=tk.LEFT, padx=2)

    def populate_file_list(self):
        """Populate the listbox with files and folders."""
        self.file_list.delete(0, tk.END)
        try:
            items = os.listdir(self.current_dir)
            for item in items:
                self.file_list.insert(tk.END, item)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_item(self, event):
        """Open the selected item if it's a folder or display its contents if it's a file."""
        selected = self.file_list.get(self.file_list.curselection())
        path = os.path.join(self.current_dir, selected)
        if os.path.isdir(path):
            self.history.append(self.current_dir)
            self.current_dir = path
            self.dir_label.config(text=self.current_dir)
            self.populate_file_list()
        else:
            try:
                with open(path, "r") as file:
                    content = file.read()
                messagebox.showinfo("File Content", content)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def go_back(self):
        """Navigate to the parent directory."""
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:  # Prevent navigating beyond the root directory
            self.current_dir = parent_dir
            self.dir_label.config(text=self.current_dir)
            self.populate_file_list()


    def sort_items(self, criterion):
        """Sort items by name or modification date."""
        self.file_list.delete(0, tk.END)
        try:
            items = os.listdir(self.current_dir)
            if criterion == "name":
                items.sort()
            elif criterion == "date":
                items.sort(key=lambda item: os.path.getmtime(os.path.join(self.current_dir, item)))
            for item in items:
                self.file_list.insert(tk.END, item)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_file(self):
        """Create a new file."""
        filename = simpledialog.askstring("Create File", "Enter file name:")
        if filename:
            path = os.path.join(self.current_dir, filename)
            try:
                with open(path, "w") as file:
                    file.write("")
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_folder(self):
        """Create a new folder."""
        foldername = simpledialog.askstring("Create Folder", "Enter folder name:")
        if foldername:
            path = os.path.join(self.current_dir, foldername)
            try:
                os.mkdir(path)
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_item(self):
        """Delete the selected file or folder."""
        selected = self.file_list.get(self.file_list.curselection())
        path = os.path.join(self.current_dir, selected)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.populate_file_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def rename_item(self):
        """Rename the selected file or folder."""
        selected = self.file_list.get(self.file_list.curselection())
        path = os.path.join(self.current_dir, selected)
        new_name = simpledialog.askstring("Rename", "Enter new name:")
        if new_name:
            new_path = os.path.join(self.current_dir, new_name)
            try:
                os.rename(path, new_path)
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def copy_item(self):
        """Copy the selected file or folder to a new location."""
        selected = self.file_list.get(self.file_list.curselection())
        path = os.path.join(self.current_dir, selected)
        dest = filedialog.askdirectory(title="Select Destination")
        if dest:
            try:
                if os.path.isdir(path):
                    shutil.copytree(path, os.path.join(dest, selected))
                else:
                    shutil.copy(path, dest)
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def move_item(self):
        """Move the selected file or folder to a new location."""
        selected = self.file_list.get(self.file_list.curselection())
        path = os.path.join(self.current_dir, selected)
        dest = filedialog.askdirectory(title="Select Destination")
        if dest:
            try:
                shutil.move(path, dest)
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def change_directory(self):
        """Change the current working directory."""
        new_dir = filedialog.askdirectory(title="Select Directory")
        if new_dir:
            self.history.append(self.current_dir)
            self.current_dir = new_dir
            self.dir_label.config(text=self.current_dir)
            self.populate_file_list()

if __name__ == "__main__":
    root = tk.Tk()
    FileManager(root)
    root.mainloop()
