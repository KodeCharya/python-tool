import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import webbrowser
import requests
from io import BytesIO
from PIL import Image, ImageTk

class BrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Browser")
        self.root.geometry("1200x800")

        self.dark_theme = False

        # Top bar
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.back_button = tk.Button(self.top_frame, text="<<", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.forward_button = tk.Button(self.top_frame, text=">>", command=self.go_forward)
        self.forward_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reload_button = tk.Button(self.top_frame, text="Reload", command=self.reload_page)
        self.reload_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.url_entry = tk.Entry(self.top_frame, width=80)
        self.url_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.url_entry.bind("<Return>", self.load_page)

        self.go_button = tk.Button(self.top_frame, text="Go", command=self.load_page)
        self.go_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bookmark_button = tk.Button(self.top_frame, text="Bookmark", command=self.add_bookmark)
        self.bookmark_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.theme_button = tk.Button(self.top_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.download_button = tk.Button(self.top_frame, text="Download", command=self.download_content)
        self.download_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Web view frame
        self.web_frame = tk.Frame(self.root)
        self.web_frame.pack(fill=tk.BOTH, expand=True)

        self.web_view = tk.Text(self.web_frame, wrap="word", state=tk.DISABLED)
        self.web_view.pack(fill=tk.BOTH, expand=True)

        # Bookmarks
        self.bookmarks = []

        # Navigation history
        self.history = []
        self.current_index = -1

        # Load default page
        self.load_default_page()

    def load_default_page(self):
        self.load_url("https://www.google.com")

    def load_url(self, url):
        try:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)

            response = requests.get(url)
            self.update_web_view(response.text)

            # Update navigation history
            if self.current_index == -1 or (self.history and self.history[self.current_index] != url):
                self.history = self.history[:self.current_index + 1]
                self.history.append(url)
                self.current_index += 1

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page: {e}")

    def update_web_view(self, content):
        self.web_view.config(state=tk.NORMAL)
        self.web_view.delete(1.0, tk.END)
        self.web_view.insert(tk.END, content)
        self.web_view.config(state=tk.DISABLED)

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_url(self.history[self.current_index])

    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.load_url(self.history[self.current_index])

    def reload_page(self):
        if self.history:
            self.load_url(self.history[self.current_index])

    def load_page(self, event=None):
        url = self.url_entry.get()
        if not url.startswith("http"):
            url = "http://" + url
        self.load_url(url)

    def add_bookmark(self):
        url = self.url_entry.get()
        if url and url not in self.bookmarks:
            self.bookmarks.append(url)
            messagebox.showinfo("Bookmark Added", f"Added {url} to bookmarks")

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        bg_color = "black" if self.dark_theme else "white"
        fg_color = "white" if self.dark_theme else "black"

        self.root.config(bg=bg_color)
        self.top_frame.config(bg=bg_color)

        for widget in self.top_frame.winfo_children():
            widget.config(bg=bg_color, fg=fg_color)

        self.web_view.config(bg=bg_color, fg=fg_color)

    def download_content(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "No URL to download")
            return

        try:
            response = requests.get(url, stream=True)
            file_name = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html"), ("All files", "*.*")])
            if file_name:
                with open(file_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                messagebox.showinfo("Download Complete", f"File saved to {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download content: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BrowserApp(root)
    root.mainloop()
