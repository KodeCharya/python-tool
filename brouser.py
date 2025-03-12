import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu, scrolledtext
import threading
import json
import os
import re
from urllib.parse import urlparse, quote_plus
import webbrowser
import time
from datetime import datetime

# Try to import optional packages with fallbacks
try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
    BS4_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    BS4_AVAILABLE = False
    print("requests or BeautifulSoup4 not installed. Limited functionality available.")

try:
    from tkhtmlview import HTMLLabel, HTMLScrolledText
    HTML_VIEW_AVAILABLE = True
except ImportError:
    HTML_VIEW_AVAILABLE = False
    print("tkhtmlview not installed. Using basic display.")

class EnhancedBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Python Browser")
        self.root.geometry("1000x700")
        
        # Set theme
        self.current_theme = "light"
        self.theme_colors = {
            "light": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "button_bg": "#e0e0e0",
                "entry_bg": "#ffffff",
                "tab_bg": "#e0e0e0",
                "status_bg": "#e0e0e0"
            },
            "dark": {
                "bg": "#2e2e2e",
                "fg": "#ffffff",
                "button_bg": "#3e3e3e",
                "entry_bg": "#4e4e4e",
                "tab_bg": "#3e3e3e",
                "status_bg": "#3e3e3e"
            }
        }
        
        # User settings
        self.settings = {
            "default_search_engine": "Google",
            "homepage": "https://www.google.com",
            "enable_javascript": True,
            "block_popups": True,
            "save_history": True,
            "theme": "light",
            "font_size": 10,
            "download_dir": os.path.join(os.path.expanduser("~"), "Downloads")
        }
        
        # Load settings if they exist
        self.settings_file = "browser_settings.json"
        self.load_settings()
        
        # History
        self.history = []
        self.current_position = -1
        self.bookmarks = []
        self.load_bookmarks()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu
        self.create_menu()
        
        # Create navigation bar
        self.create_navigation_bar()
        
        # Create tabbed interface
        self.create_tabs()
        
        # Create status bar
        self.create_status_bar()
        
        # Apply theme
        self.apply_theme(self.settings["theme"])
        
        # Try to navigate to homepage
        self.url_var.set(self.settings["homepage"])
        self.navigate()

        # Create popup menu
        self.create_popup_menu()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_bookmarks(self):
        try:
            if os.path.exists("browser_bookmarks.json"):
                with open("browser_bookmarks.json", 'r') as f:
                    self.bookmarks = json.load(f)
        except Exception as e:
            print(f"Error loading bookmarks: {e}")

    def save_bookmarks(self):
        try:
            with open("browser_bookmarks.json", 'w') as f:
                json.dump(self.bookmarks, f, indent=4)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def apply_theme(self, theme_name):
        if theme_name not in self.theme_colors:
            theme_name = "light"
        
        self.current_theme = theme_name
        self.settings["theme"] = theme_name
        colors = self.theme_colors[theme_name]
        
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("TButton", background=colors["button_bg"], foreground=colors["fg"])
        style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["fg"])
        style.configure("TNotebook", background=colors["bg"])
        style.configure("TNotebook.Tab", background=colors["tab_bg"], foreground=colors["fg"])
        
        # Update the text widget colors if it's not an HTMLLabel
        if not HTML_VIEW_AVAILABLE:
            for tab_name, tab_content in self.tab_contents.items():
                content_display = tab_content["content"]
                content_display.config(bg=colors["entry_bg"], fg=colors["fg"])

    def create_menu(self):
        menubar = Menu(self.root)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Tab", command=self.new_tab)
        file_menu.add_command(label="Open File", command=self.open_local_file)
        file_menu.add_command(label="Save Page As", command=self.save_page)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_page)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.edit_cut)
        edit_menu.add_command(label="Copy", command=self.edit_copy)
        edit_menu.add_command(label="Paste", command=self.edit_paste)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = Menu(view_menu, tearoff=0)
        theme_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        view_menu.add_command(label="View Source", command=self.view_source)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # History menu
        history_menu = Menu(menubar, tearoff=0)
        history_menu.add_command(label="Show History", command=self.show_history)
        history_menu.add_command(label="Clear History", command=self.clear_history)
        menubar.add_cascade(label="History", menu=history_menu)
        
        # Bookmarks menu
        bookmarks_menu = Menu(menubar, tearoff=0)
        bookmarks_menu.add_command(label="Add Bookmark", command=self.add_bookmark)
        bookmarks_menu.add_command(label="Show Bookmarks", command=self.show_bookmarks)
        menubar.add_cascade(label="Bookmarks", menu=bookmarks_menu)
        
        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Developer Tools", command=self.show_dev_tools)
        tools_menu.add_command(label="Network Monitor", command=self.show_network_monitor)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings", command=self.show_settings)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_navigation_bar(self):
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Back button
        self.back_button = ttk.Button(
            nav_frame, text="←", width=3, command=self.go_back
        )
        self.back_button.pack(side=tk.LEFT, padx=2)
        
        # Forward button
        self.forward_button = ttk.Button(
            nav_frame, text="→", width=3, command=self.go_forward
        )
        self.forward_button.pack(side=tk.LEFT, padx=2)
        
        # Refresh button
        self.refresh_button = ttk.Button(
            nav_frame, text="↻", width=3, command=self.refresh
        )
        self.refresh_button.pack(side=tk.LEFT, padx=2)
        
        # Home button
        self.home_button = ttk.Button(
            nav_frame, text="🏠", width=3, command=self.go_home
        )
        self.home_button.pack(side=tk.LEFT, padx=2)
        
        # URL/Search bar
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(nav_frame, textvariable=self.url_var)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.bind("<Return>", self.navigate)
        
        # Search engine dropdown
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        }
        
        self.search_engine_var = tk.StringVar(value=self.settings["default_search_engine"])
        self.search_engine_menu = ttk.OptionMenu(
            nav_frame, 
            self.search_engine_var,
            self.settings["default_search_engine"],
            *self.search_engines.keys()
        )
        self.search_engine_menu.pack(side=tk.LEFT, padx=2)
        
        # Go button
        self.go_button = ttk.Button(
            nav_frame, text="Go", command=self.navigate
        )
        self.go_button.pack(side=tk.LEFT, padx=2)
        
        # Bookmark button
        self.bookmark_button = ttk.Button(
            nav_frame, text="★", width=3, command=self.add_bookmark
        )
        self.bookmark_button.pack(side=tk.LEFT, padx=2)
    
    def create_tabs(self):
        # Create notebook for tabs
        self.tab_notebook = ttk.Notebook(self.main_frame)
        self.tab_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Enable tab closing
        self.tab_notebook.enable_traversal()
        
        # Dictionary to store tab contents
        self.tab_contents = {}
        self.current_tab_id = 0
        
        # Create the first tab
        self.new_tab()
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-t>", self.new_tab)
        self.root.bind("<Control-w>", self.close_current_tab)
        self.root.bind("<Control-r>", self.refresh)
        self.root.bind("<Control-l>", lambda e: self.url_entry.focus())

        # Add tab bindings
        self.tab_notebook.bind("<Button-2>", self.close_tab_middle_click)  # Middle click to close
        self.tab_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            status_frame, textvariable=self.status_var, anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # Progress bar for loading
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def new_tab(self, event=None, url=None):
        # Create a new tab frame
        tab_id = f"tab_{self.current_tab_id}"
        tab_frame = ttk.Frame(self.tab_notebook)
        
        # Create close button for tab
        def close_tab():
            self.close_tab(tab_id)
        
        close_button = ttk.Button(tab_frame, text="×", width=2, command=close_tab)
        close_button.pack(side=tk.RIGHT, padx=2)
        
        # Create content display
        if HTML_VIEW_AVAILABLE:
            content_display = HTMLScrolledText(tab_frame)
            content_display.set_html("<h1>Welcome to Enhanced Browser</h1>")
            # Enable basic text operations
            content_display.bind("<Control-c>", lambda e: self.edit_copy())
            content_display.bind("<Control-a>", lambda e: self.select_all())
        else:
            content_display = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD)
            content_display.insert(tk.END, "Welcome to Enhanced Browser\n\nNote: Install tkhtmlview for better browsing experience.")
            content_display.bind("<Control-c>", lambda e: self.edit_copy())
            content_display.bind("<Control-a>", lambda e: self.select_all())
        
        content_display.pack(fill=tk.BOTH, expand=True)
        
        # Add right-click menu
        content_display.bind("<Button-3>", self.show_popup_menu)
        
        # Add the tab
        tab_name = "New Tab"
        self.tab_notebook.add(tab_frame, text=tab_name)
        self.tab_notebook.select(tab_frame)
        
        # Store tab info
        self.tab_contents[tab_id] = {
            "frame": tab_frame,
            "content": content_display,
            "url": url or "",
            "title": tab_name,
            "history": [],
            "position": -1,
            "close_button": close_button
        }
        
        self.current_tab = tab_id
        self.current_tab_id += 1
        
        if url:
            self.url_var.set(url)
            self.navigate()
        
        return tab_id
    
    def get_current_tab_content(self):
        if not self.tab_contents:
            return None
        
        # Get the selected tab
        selected_tab = self.tab_notebook.select()
        
        # Find which tab_id this corresponds to
        for tab_id, content in self.tab_contents.items():
            if content["frame"] == self.tab_notebook.nametowidget(selected_tab):
                self.current_tab = tab_id
                return content
        
        return None
    
    def navigate(self, event=None):
        user_input = self.url_var.get().strip()
        
        # Check if it's a URL or a search query
        if not user_input:
            return
        
        if self.is_valid_url(user_input):
            url = user_input
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
        else:
            # Treat as a search query
            search_engine = self.search_engine_var.get()
            search_url_template = self.search_engines.get(search_engine, self.search_engines["Google"])
            url = search_url_template.format(quote_plus(user_input))
        
        # Get current tab content
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        
        # Update status
        self.status_var.set(f"Navigating to {url}...")
        self.progress["value"] = 20
        self.root.update()
        
        # Update tab history
        if tab_content["position"] >= -1:
            # Remove any forward history
            tab_content["history"] = tab_content["history"][:tab_content["position"] + 1]
            
        tab_content["history"].append(url)
        tab_content["position"] = len(tab_content["history"]) - 1
        tab_content["url"] = url
        
        # Add to global history if enabled
        if self.settings["save_history"]:
            self.history.append({
                "url": url,
                "title": tab_content["title"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Update URL entry
        self.url_var.set(url)
        
        # Load the page
        self.load_url(url)
    
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            # Return True if both scheme and netloc exist
            if result.scheme and netloc:
                return True
            # Otherwise try a regex match on a domain-like string
            if re.match(r'^[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b', url):
                return True
            return False
        except:
            return False
    
    def load_url(self, url):
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        
        def fetch_content():
            try:
                self.root.after(0, lambda: self.progress.config(value=40))
                if not REQUESTS_AVAILABLE:
                    webbrowser.open(url)
                    self.root.after(0, lambda: self.status_var.set(f"Opened {url} in external browser"))
                    self.root.after(0, lambda: self.progress.config(value=100))
                    time.sleep(1)
                    self.root.after(0, lambda: self.progress.config(value=0))
                    return
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=15)
                self.root.after(0, lambda: self.progress.config(value=70))
                if response.status_code == 200:
                    content = response.text
                    page_title = "New Tab"
                    if BS4_AVAILABLE:
                        try:
                            soup = BeautifulSoup(content, 'html.parser')
                            title_tag = soup.find('title')
                            if title_tag:
                                page_title = title_tag.text.strip()
                        except:
                            pass
                    self.root.after(0, lambda: self.update_content(content))
                    self.root.after(0, lambda: self.update_tab_title(page_title))
                    self.root.after(0, lambda: self.status_var.set(f"Loaded: {url}"))
                    self.root.after(0, lambda: self.progress.config(value=100))
                    time.sleep(0.5)
                    self.root.after(0, lambda: self.progress.config(value=0))
                else:
                    self.root.after(0, lambda: self.status_var.set(f"Error: HTTP {response.status_code}"))
                    self.root.after(0, lambda: self.progress.config(value=0))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: self.progress.config(value=0))
        thread = threading.Thread(target=fetch_content)
        thread.daemon = True
        thread.start()
    
    def update_content(self, content):
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        try:
            if HTML_VIEW_AVAILABLE:
                # Construct a full HTML doc with essential metadata and styling
                full_html = f"""
                <!DOCTYPE html>
                <html>
                  <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <base target="_blank">
                    <style>
                      body {{ font-family: sans-serif; line-height: 1.5; margin: 10px; }}
                      img {{ max-width: 100%; height: auto; }}
                    </style>
                  </head>
                  <body>
                    {content}
                  </body>
                </html>
                """
                tab_content["content"].set_html(full_html)
                # Bind selection shortcuts
                tab_content["content"].bind("<Control-a>", self.select_all)
                tab_content["content"].bind("<Control-c>", lambda e: self.edit_copy())
            else:
                if BS4_AVAILABLE:
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text(separator='\n', strip=True)
                else:
                    text = content
                tab_content["content"].config(state=tk.NORMAL)
                tab_content["content"].delete(1.0, tk.END)
                tab_content["content"].insert(tk.END, text)
                # Keep widget editable so selection is possible
                tab_content["content"].config(state=tk.NORMAL)
                tab_content["content"].bind("<Control-a>", self.select_all)
                tab_content["content"].bind("<Control-c>", lambda e: self.edit_copy())
        except Exception as e:
            error_msg = f"Error displaying content: {str(e)}"
            tab_content["content"].config(state=tk.NORMAL)
            tab_content["content"].delete(1.0, tk.END)
            tab_content["content"].insert(tk.END, error_msg)
    
    def update_tab_title(self, title):
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        
        # Truncate long titles
        display_title = title[:20] + "..." if len(title) > 20 else title
        
        # Find the tab index
        for i, tab_id in enumerate(self.tab_notebook.tabs()):
            if tab_id == str(tab_content["frame"]):
                self.tab_notebook.tab(i, text=display_title)
                tab_content["title"] = title
                break
    
    def go_back(self):
        tab_content = self.get_current_tab_content()
        if not tab_content or tab_content["position"] <= 0:
            return
        
        tab_content["position"] -= 1
        url = tab_content["history"][tab_content["position"]]
        self.url_var.set(url)
        self.load_url(url)
    
    def go_forward(self):
        tab_content = self.get_current_tab_content()
        if not tab_content or tab_content["position"] >= len(tab_content["history"]) - 1:
            return
        
        tab_content["position"] += 1
        url = tab_content["history"][tab_content["position"]]
        self.url_var.set(url)
        self.load_url(url)
    
    def refresh(self):
        tab_content = self.get_current_tab_content()
        if not tab_content or tab_content["position"] < 0:
            return
        
        url = tab_content["history"][tab_content["position"]]
        self.load_url(url)
    
    def go_home(self):
        self.url_var.set(self.settings["homepage"])
        self.navigate()
    
    def open_local_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.update_content(content)
                
                # Update URL to file path
                file_url = f"file://{file_path}"
                self.url_var.set(file_url)
                
                # Update tab title
                filename = os.path.basename(file_path)
                self.update_tab_title(filename)
                
                # Update history
                tab_content = self.get_current_tab_content()
                if tab_content:
                    tab_content["history"].append(file_url)
                    tab_content["position"] = len(tab_content["history"]) - 1
                    tab_content["url"] = file_url
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_page(self):
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if HTML_VIEW_AVAILABLE:
                    content = tab_content["content"].html
                else:
                    content = tab_content["content"].get(1.0, tk.END)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.status_var.set(f"Page saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def print_page(self):
        messagebox.showinfo("Print", "Printing functionality not implemented yet.")
    
    def edit_cut(self):
        tab_content = self.get_current_tab_content()
        if not tab_content or HTML_VIEW_AVAILABLE:
            return
        
        # Cut only works for text widgets
        try:
            tab_content["content"].event_generate("<<Cut>>")
        except:
            pass
    
    def edit_copy(self):
        try:
            tab_content = self.get_current_tab_content()
            if not tab_content:
                return
            content = tab_content["content"]
            if HTML_VIEW_AVAILABLE:
                try:
                    sel = content.selection_get()
                    self.root.clipboard_clear()
                    self.root.clipboard_append(sel)
                except tk.TclError:
                    pass
            else:
                if content.tag_ranges(tk.SEL):
                    sel = content.get(tk.SEL_FIRST, tk.SEL_LAST)
                    self.root.clipboard_clear()
                    self.root.clipboard_append(sel)
        except Exception as e:
            print(f"Error copying: {e}")
    
    def edit_paste(self):
        tab_content = self.get_current_tab_content()
        if not tab_content or HTML_VIEW_AVAILABLE:
            return
        
        try:
            content = tab_content["content"]
            content.config(state=tk.NORMAL)
            content.insert(tk.INSERT, self.root.clipboard_get())
            content.config(state=tk.DISABLED)
        except:
            pass
    
    def zoom_in(self):
        self.settings["font_size"] += 1
        self.status_var.set(f"Zoom level: {self.settings['font_size']}")
        self.apply_font_size()
    
    def zoom_out(self):
        if self.settings["font_size"] > 7:
            self.settings["font_size"] -= 1
            self.status_var.set(f"Zoom level: {self.settings['font_size']}")
            self.apply_font_size()
    
    def apply_font_size(self):
        # This only works for non-HTML displays
        if not HTML_VIEW_AVAILABLE:
            for tab_id, tab_content in self.tab_contents.items():
                tab_content["content"].config(font=("TkDefaultFont", self.settings["font_size"]))
    
    def change_theme(self, theme):
        self.apply_theme(theme)
        self.save_settings()
    
    def view_source(self):
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        
        # Create source view window
        source_window = tk.Toplevel(self.root)
        source_window.title(f"Source: {tab_content['title']}")
        source_window.geometry("800x600")
        
        # Add source text widget
        source_text = scrolledtext.ScrolledText(source_window, wrap=tk.NONE)
        source_text.pack(fill=tk.BOTH, expand=True)
        
        # Get the content
        if HTML_VIEW_AVAILABLE:
            source_text.insert(tk.END, tab_content["content"].html)
        else:
            source_text.insert(tk.END, tab_content["content"].get(1.0, tk.END))
        
        source_text.config(state=tk.DISABLED)
    
    def show_history(self):
        # Create history window
        history_window = tk.Toplevel(self.root)
        history_window.title("Browsing History")
        history_window.geometry("600x400")
        
        # Add history list
        history_frame = ttk.Frame(history_window)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create columns
        columns = ("title", "url", "timestamp")
        history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        # Define headings
        history_tree.heading("title", text="Page Title")
        history_tree.heading("url", text="URL")
        history_tree.heading("timestamp", text="Date/Time")
        
        # Set column widths
        history_tree.column("title", width=200)
        history_tree.column("url", width=250)
        history_tree.column("timestamp", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=history_tree.yview)
        history_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate with history items (in reverse order, newest first)
        for i, item in enumerate(reversed(self.history)):
            date_str = item.get("timestamp", "").split("T")[0]
            history_tree.insert("", tk.END, values=(
                item.get("title", "Untitled"),
                item.get("url", ""),
                date_str
            ))
        
        # Double click to open URL
        def on_item_double_click(event):
            selected_item = history_tree.selection()[0]
            url = history_tree.item(selected_item, "values")[1]
            self.url_var.set(url)
            self.navigate()
            history_window.destroy()
        
        history_tree.bind("<Double-1>", on_item_double_click)
    
    def clear_history(self):
        confirm = messagebox.askyesno("Clear History", "Are you sure you want to clear all browsing history?")
        if confirm:
            self.history = []
            self.status_var.set("Browsing history cleared")
    
    def add_bookmark(self):
        tab_content = self.get_current_tab_content()
        if not tab_content or not tab_content.get("url"):
            return
        
        bookmark = {
            "title": tab_content.get("title", "Untitled"),
            "url": tab_content.get("url", ""),
            "added": datetime.now().isoformat()
        }
        
        # Check if already bookmarked
        for existing in self.bookmarks:
            if existing.get("url") == bookmark["url"]:
                self.status_var.set("This page is already bookmarked")
                return
        
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        self.status_var.set(f"Bookmarked: {bookmark['title']}")
    
    def show_bookmarks(self):
        # Create bookmarks window
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Bookmarks")
        bookmarks_window.geometry("600x400")
        
        # Add bookmarks list
        bookmarks_frame = ttk.Frame(bookmarks_window)
        bookmarks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create columns
        columns = ("title", "url", "added")
        bookmarks_tree = ttk.Treeview(bookmarks_frame, columns=columns, show="headings")
        
        # Define headings
        bookmarks_tree.heading("title", text="Page Title")
        bookmarks_tree.heading("url", text="URL")
        bookmarks_tree.heading("added", text="Date Added")
        
        # Set column widths
        bookmarks_tree.column("title", width=200)
        bookmarks_tree.column("url", width=250)
        bookmarks_tree.column("added", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(bookmarks_frame, orient=tk.VERTICAL, command=bookmarks_tree.yview)
        bookmarks_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        bookmarks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate with bookmarks
        for i, item in enumerate(self.bookmarks):
            date_str = item.get("added", "").split("T")[0]
            bookmarks_tree.insert("", tk.END, values=(
                item.get("title", "Untitled"),
                item.get("url", ""),
                date_str
            ))
        
        # Buttons frame
        button_frame = ttk.Frame(bookmarks_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Open button
        open_button = ttk.Button(button_frame, text="Open", 
                               command=lambda: self.open_bookmark(bookmarks_tree))
        open_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_button = ttk.Button(button_frame, text="Delete", 
                                 command=lambda: self.delete_bookmark(bookmarks_tree))
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Double click to open URL
        def on_item_double_click(event):
            self.open_bookmark(bookmarks_tree)
        
        bookmarks_tree.bind("<Double-1>", on_item_double_click)

    def open_bookmark(self, tree):
        selection = tree.selection()
        if not selection:
            return
            
        selected_item = selection[0]
        url = tree.item(selected_item, "values")[1]
        self.url_var.set(url)
        self.navigate()

    def delete_bookmark(self, tree):
        selection = tree.selection()
        if not selection:
            return
            
        selected_item = selection[0]
        url = tree.item(selected_item, "values")[1]
        
        # Find and remove the bookmark
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.get("url") == url:
                del self.bookmarks[i]
                break
        
        # Update display
        tree.delete(selected_item)
        self.save_bookmarks()
        self.status_var.set("Bookmark deleted")

    def show_dev_tools(self):
        tab_content = self.get_current_tab_content()
        if not tab_content:
            return
        
        # Create dev tools window
        dev_window = tk.Toplevel(self.root)
        dev_window.title(f"Developer Tools: {tab_content['title']}")
        dev_window.geometry("800x600")
        
        # Create notebook for different tools
        tools_notebook = ttk.Notebook(dev_window)
        tools_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Elements tab
        elements_frame = ttk.Frame(tools_notebook)
        tools_notebook.add(elements_frame, text="Elements")
        
        if BS4_AVAILABLE and HTML_VIEW_AVAILABLE:
            try:
                # Parse the HTML
                html_content = tab_content["content"].html
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Create a treeview to display the DOM
                tree_columns = ("tag", "attributes")
                elements_tree = ttk.Treeview(elements_frame, columns=tree_columns, show="tree headings")
                elements_tree.heading("tag", text="Tag")
                elements_tree.heading("attributes", text="Attributes")
                elements_tree.column("tag", width=200)
                elements_tree.column("attributes", width=400)
                
                # Add scrollbars
                y_scrollbar = ttk.Scrollbar(elements_frame, orient=tk.VERTICAL, command=elements_tree.yview)
                elements_tree.configure(yscroll=y_scrollbar.set)
                
                y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                elements_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                # Recursive function to add elements to the tree
                def add_element_to_tree(element, parent=""):
                    if element.name:
                        # Get attributes as string
                        attrs = ", ".join([f"{k}=\"{v}\"" for k, v in element.attrs.items()])
                        
                        # Insert into tree
                        node_id = elements_tree.insert(parent, tk.END, text=element.name, 
                                                     values=(element.name, attrs))
                        
                        # Process children
                        for child in element.children:
                            if child.name:  # Skip text nodes
                                add_element_to_tree(child, node_id)
                
                # Start building the tree from the HTML tag
                if soup.html:
                    add_element_to_tree(soup.html)
                
            except Exception as e:
                error_label = ttk.Label(elements_frame, text=f"Error parsing HTML: {str(e)}")
                error_label.pack(padx=10, pady=10)
        else:
            missing_label = ttk.Label(elements_frame, 
                                    text="BeautifulSoup4 and/or tkhtmlview packages are required for this feature.")
            missing_label.pack(padx=10, pady=10)
        
        # Console tab
        console_frame = ttk.Frame(tools_notebook)
        tools_notebook.add(console_frame, text="Console")
        
        console_output = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD)
        console_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        console_output.insert(tk.END, "Console output will appear here.\n")
        
        console_input = ttk.Entry(console_frame)
        console_input.pack(fill=tk.X, padx=5, pady=5)
        
        def execute_console():
            command = console_input.get()
            console_output.insert(tk.END, f"> {command}\n")
            console_input.delete(0, tk.END)
            console_output.insert(tk.END, "Command execution not implemented.\n\n")
        
        console_input.bind("<Return>", lambda e: execute_console())
        
        # Network tab
        network_frame = ttk.Frame(tools_notebook)
        tools_notebook.add(network_frame, text="Network")
        
        network_label = ttk.Label(network_frame, 
                                text="Network monitoring functionality not implemented.")
        network_label.pack(padx=10, pady=10)

    def show_network_monitor(self):
        # Create network monitor window
        network_window = tk.Toplevel(self.root)
        network_window.title("Network Monitor")
        network_window.geometry("800x600")
        
        # Create a simple display
        info_frame = ttk.Frame(network_window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_label = ttk.Label(info_frame, 
                             text="Network monitoring functionality is not fully implemented.")
        info_label.pack(padx=10, pady=10)
        
        # Placeholder for network requests list
        columns = ("url", "method", "status", "type", "size", "time")
        network_tree = ttk.Treeview(info_frame, columns=columns, show="headings")
        
        for col in columns:
            network_tree.heading(col, text=col.capitalize())
            network_tree.column(col, width=100)
        
        network_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add some placeholder data
        network_tree.insert("", tk.END, values=(
            self.url_var.get(),
            "GET",
            "200",
            "html",
            "10.2 KB",
            "1.2s"
        ))

    def show_settings(self):
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Browser Settings")
        settings_window.geometry("500x600")
        
        # Create a notebook for different setting categories
        settings_notebook = ttk.Notebook(settings_window)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings tab
        general_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(general_frame, text="General")
        
        # Organize settings in a grid
        row = 0
        
        # Homepage
        ttk.Label(general_frame, text="Homepage:").grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        homepage_var = tk.StringVar(value=self.settings["homepage"])
        homepage_entry = ttk.Entry(general_frame, textvariable=homepage_var, width=40)
        homepage_entry.grid(row=row, column=1, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # Default search engine
        ttk.Label(general_frame, text="Default Search Engine:").grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        search_engine_var = tk.StringVar(value=self.settings["default_search_engine"])
        search_engine_combo = ttk.Combobox(general_frame, textvariable=search_engine_var, 
                                         values=list(self.search_engines.keys()),
                                         state="readonly")
        search_engine_combo.grid(row=row, column=1, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # Theme
        ttk.Label(general_frame, text="Theme:").grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        theme_var = tk.StringVar(value=self.settings["theme"])
        theme_combo = ttk.Combobox(general_frame, textvariable=theme_var, 
                                 values=["light", "dark"],
                                 state="readonly")
        theme_combo.grid(row=row, column=1, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # Font size
        ttk.Label(general_frame, text="Font Size:").grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        font_size_var = tk.IntVar(value=self.settings["font_size"])
        font_size_spinbox = tk.Spinbox(general_frame, from_=8, to=24, textvariable=font_size_var, width=5)
        font_size_spinbox.grid(row=row, column=1, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # Download directory
        ttk.Label(general_frame, text="Download Directory:").grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        download_dir_var = tk.StringVar(value=self.settings["download_dir"])
        download_dir_frame = ttk.Frame(general_frame)
        download_dir_frame.grid(row=row, column=1, padx=10, pady=10, sticky=tk.W)
        
        download_dir_entry = ttk.Entry(download_dir_frame, textvariable=download_dir_var, width=30)
        download_dir_entry.pack(side=tk.LEFT)
        
        def browse_download_dir():
            directory = filedialog.askdirectory()
            if directory:
                download_dir_var.set(directory)
        
        browse_button = ttk.Button(download_dir_frame, text="Browse", command=browse_download_dir)
        browse_button.pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Privacy settings tab
        privacy_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(privacy_frame, text="Privacy")
        
        # Privacy settings
        row = 0
        
        # Save history
        save_history_var = tk.BooleanVar(value=self.settings["save_history"])
        save_history_check = ttk.Checkbutton(privacy_frame, text="Save browsing history", 
                                           variable=save_history_var)
        save_history_check.grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # Block popups
        block_popups_var = tk.BooleanVar(value=self.settings["block_popups"])
        block_popups_check = ttk.Checkbutton(privacy_frame, text="Block popup windows", 
                                           variable=block_popups_var)
        block_popups_check.grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # JavaScript
        javascript_var = tk.BooleanVar(value=self.settings["enable_javascript"])
        javascript_check = ttk.Checkbutton(privacy_frame, text="Enable JavaScript", 
                                         variable=javascript_var)
        javascript_check.grid(row=row, column=0, padx=10, pady=10, sticky=tk.W)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings_changes():
            # Update settings
            self.settings["homepage"] = homepage_var.get()
            self.settings["default_search_engine"] = search_engine_var.get()
            self.settings["theme"] = theme_var.get()
            self.settings["font_size"] = font_size_var.get()
            self.settings["download_dir"] = download_dir_var.get()
            self.settings["save_history"] = save_history_var.get()
            self.settings["block_popups"] = block_popups_var.get()
            self.settings["enable_javascript"] = javascript_var.get()
            
            # Save to file
            self.save_settings()
            
            # Apply changes
            self.apply_theme(self.settings["theme"])
            self.apply_font_size()
            
            # Update search engine dropdown
            self.search_engine_var.set(self.settings["default_search_engine"])
            
            # Close settings window
            settings_window.destroy()
            
            # Show confirmation
            self.status_var.set("Settings saved")
        
        save_button = ttk.Button(button_frame, text="Save", command=save_settings_changes)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=settings_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)

    def show_help(self):
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Browser Help")
        help_window.geometry("600x500")
        
        # Create scrollable text area
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add help content
        help_content = """
Enhanced Python Browser Help

Navigation:
- Address Bar: Enter URLs or search terms
- Back/Forward: Navigate through page history
- Refresh: Reload the current page
- Home: Go to your homepage

Tabs:
- Create new tabs with File > New Tab or Ctrl+T
- Close tabs with the X on the tab

Bookmarks:
- Add a bookmark with the star button
- View and manage bookmarks in Bookmarks > Show Bookmarks

History:
- View your browsing history in History > Show History
- Clear your history in History > Clear History

Settings:
- Change your homepage, search engine, and theme
- Adjust privacy settings

File Operations:
- Open local HTML files with File > Open File
- Save pages with File > Save Page As

Requirements:
- For full functionality, install the following Python packages:
  - requests
  - beautifulsoup4
  - tkhtmlview

Keyboard Shortcuts:
- Ctrl+T: New Tab
- Ctrl+W: Close Tab
- Ctrl+R: Refresh
- Ctrl+H: History
- Ctrl+B: Bookmarks
- F1: Help
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

    def show_about(self):
        messagebox.showinfo(
            "About Enhanced Browser",
            "Enhanced Python Browser\n\n"
            "Version 1.0\n\n"
            "A simple web browser written in Python using Tkinter.\n\n"
            "This browser demonstrates basic web browsing capabilities\n"
            "including tabs, bookmarks, and history management.\n\n"
            "For best experience, install requests, beautifulsoup4,\n"
            "and tkhtmlview packages."
        )

    def on_closing(self):
        # Save settings and bookmarks before closing
        self.save_settings()
        self.save_bookmarks()
        self.root.destroy()

    def create_popup_menu(self):
        self.popup_menu = Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Cut", command=self.edit_cut)
        self.popup_menu.add_command(label="Copy", command=self.edit_copy)
        self.popup_menu.add_command(label="Paste", command=self.edit_paste)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Select All", command=self.select_all)

    def show_popup_menu(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def select_all(self, event=None):
        try:
            tab_content = self.get_current_tab_content()
            if not tab_content:
                return
            content = tab_content["content"]
            content.focus_set()
            content.tag_add(tk.SEL, "1.0", tk.END)
        except Exception as e:
            print(f"Error selecting all: {e}")

    def close_tab(self, tab_id):
        if tab_id in self.tab_contents:
            tab_frame = self.tab_contents[tab_id]["frame"]
            self.tab_notebook.forget(tab_frame)
            del self.tab_contents[tab_id]
            
            # Create new tab if last one was closed
            if not self.tab_contents:
                self.new_tab()

    def close_current_tab(self, event=None):
        tab_content = self.get_current_tab_content()
        if tab_content:
            self.close_tab(self.current_tab)

    def close_tab_middle_click(self, event):
        clicked_tab = self.tab_notebook.identify(event.x, event.y)
        if clicked_tab:
            tab_id = None
            for tid, content in self.tab_contents.items():
                if str(content["frame"]) == clicked_tab:
                    tab_id = tid
                    break
            if tab_id:
                self.close_tab(tab_id)

    def on_tab_changed(self, event):
        tab_content = self.get_current_tab_content()
        if tab_content:
            self.url_var.set(tab_content["url"])

# Main function to run the browser
def main():
    root = tk.Tk()
    browser = EnhancedBrowser(root)
    root.protocol("WM_DELETE_WINDOW", browser.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
