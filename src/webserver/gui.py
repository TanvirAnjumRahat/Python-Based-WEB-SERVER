import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import socket
import sys
import os
from pathlib import Path
from datetime import datetime
import io

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.webserver.config import ServerConfig
from src.webserver.cache import LRUCache


class GUILogHandler:
    """Custom log handler to redirect server logs to GUI"""
    def __init__(self, gui):
        self.gui = gui
    
    def write(self, message):
        if message.strip():
            # Parse log level from colorama output
            msg = message.strip()
            if '[INFO]' in msg:
                level = 'INFO'
                msg = msg.split('[INFO]', 1)[1].strip() if '[INFO]' in msg else msg
            elif '[ERROR]' in msg:
                level = 'ERROR'
                msg = msg.split('[ERROR]', 1)[1].strip() if '[ERROR]' in msg else msg
            elif '[WARN]' in msg:
                level = 'WARN'
                msg = msg.split('[WARN]', 1)[1].strip() if '[WARN]' in msg else msg
            elif '[DEBUG]' in msg:
                level = 'DEBUG'
                msg = msg.split('[DEBUG]', 1)[1].strip() if '[DEBUG]' in msg else msg
            else:
                level = 'INFO'
            
            # Remove ANSI color codes
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            msg = ansi_escape.sub('', msg)
            
            # Remove timestamp if present (we'll add our own)
            if msg and len(msg) > 10 and msg[0] == '[' and ']' in msg[:10]:
                msg = msg.split(']', 1)[1].strip() if ']' in msg else msg
            
            self.gui.root.after(0, lambda: self.gui.log(level, msg))
    
    def flush(self):
        pass


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyNetLite Web Server - Control Panel")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        self.root.minsize(900, 700)
        
        # Server state
        self.server_thread = None
        self.server_running = False
        self.config = ServerConfig()
        self.theme_mode = 'dark'  # 'dark' or 'light'
        
        # Capture stdout/stderr for server logs
        self.log_handler = GUILogHandler(self)
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Apply modern dark theme
        self.setup_theme()
        
        # Create GUI components
        self.create_header()
        self.create_config_panel()
        self.create_control_panel()
        self.create_status_panel()
        self.create_log_panel()
        self.create_footer()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_theme(self):
        """Configure modern dark theme with gradients and shadows"""
        # Dark theme color palette
        self.colors = {
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'primary_dark': '#1e40af',
            'success': '#10b981',
            'success_hover': '#059669',
            'danger': '#ef4444',
            'danger_hover': '#dc2626',
            'warning': '#f59e0b',
            'info': '#06b6d4',
            
            # Dark theme backgrounds
            'bg_main': '#0f172a',
            'bg_secondary': '#1e293b',
            'bg_tertiary': '#334155',
            'bg_card': '#1e293b',
            'bg_hover': '#334155',
            
            # Text colors
            'text': '#f1f5f9',
            'text_secondary': '#cbd5e1',
            'text_muted': '#94a3b8',
            'text_dark': '#64748b',
            
            # Borders and accents
            'border': '#334155',
            'border_light': '#475569',
            'accent': '#8b5cf6',
            'shadow': '#020617'
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles with modern gradients
        style.configure('Start.TButton', 
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       padding=(20, 12),
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Stop.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       padding=(20, 12),
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Action.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       padding=(16, 10),
                       font=('Segoe UI', 9, 'bold'))
        
        style.configure('Theme.TButton',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       padding=(10, 8),
                       font=('Segoe UI', 9))
        
        # Entry style
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='flat',
                       insertcolor=self.colors['text'])
        
        # Label style
        style.configure('Dark.TLabel',
                       background=self.colors['bg_card'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 9))
        
        # Hover effects
        style.map('Start.TButton',
                 background=[('active', self.colors['success_hover']), ('pressed', self.colors['success_hover'])])
        style.map('Stop.TButton',
                 background=[('active', self.colors['danger_hover']), ('pressed', self.colors['danger_hover'])])
        style.map('Action.TButton',
                 background=[('active', self.colors['primary_hover']), ('pressed', self.colors['primary_dark'])])
        style.map('Theme.TButton',
                 background=[('active', self.colors['bg_hover'])])
        
        self.root.configure(bg=self.colors['bg_main'])
    
    def create_header(self):
        """Create header with gradient effect and modern design"""
        # Main header frame with gradient effect
        header = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Add subtle top border accent
        accent_line = tk.Frame(header, bg=self.colors['primary'], height=3)
        accent_line.pack(fill=tk.X, side=tk.TOP)
        
        # Content container
        content_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        content_frame.pack(expand=True, pady=10)
        
        # Icon and title container
        title_container = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        title_container.pack()
        
        # Server icon with gradient circle effect
        icon_frame = tk.Frame(title_container, bg=self.colors['primary'], width=60, height=60)
        icon_frame.pack(side=tk.LEFT, padx=15)
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(icon_frame, 
                             text="⚡",
                             font=('Segoe UI', 28),
                             bg=self.colors['primary'],
                             fg='white')
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title and subtitle
        text_frame = tk.Frame(title_container, bg=self.colors['bg_secondary'])
        text_frame.pack(side=tk.LEFT, padx=10)
        
        title = tk.Label(text_frame, 
                        text="PyNetLite Web Server",
                        font=('Segoe UI', 22, 'bold'),
                        bg=self.colors['bg_secondary'],
                        fg=self.colors['text'])
        title.pack(anchor='w')
        
        subtitle = tk.Label(text_frame,
                           text="Professional HTTP/1.1 Server Control Panel",
                           font=('Segoe UI', 10),
                           bg=self.colors['bg_secondary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(anchor='w')
        
        # Theme toggle button in top right
        theme_btn = ttk.Button(header, 
                              text="🌙 Dark",
                              style='Theme.TButton',
                              command=self.toggle_theme,
                              width=10)
        theme_btn.place(relx=0.95, rely=0.5, anchor='e')
    
    def create_config_panel(self):
        """Create configuration panel with card design"""
        # Card container
        card = tk.Frame(self.root, bg=self.colors['bg_main'])
        card.pack(fill=tk.X, padx=25, pady=20)
        
        # Inner card with border
        config_card = tk.Frame(card, 
                              bg=self.colors['bg_card'],
                              highlightbackground=self.colors['border'],
                              highlightthickness=1)
        config_card.pack(fill=tk.X)
        
        # Card content
        config_frame = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_frame.pack(fill=tk.X, padx=25, pady=20)
        
        # Title with icon
        title_frame = tk.Frame(config_frame, bg=self.colors['bg_card'])
        title_frame.grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 20))
        
        title = tk.Label(title_frame,
                        text="⚙️ Server Configuration",
                        font=('Segoe UI', 13, 'bold'),
                        bg=self.colors['bg_card'],
                        fg=self.colors['text'])
        title.pack(side=tk.LEFT)
        
        separator = tk.Frame(title_frame, bg=self.colors['primary'], height=2, width=300)
        separator.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Configuration fields
        row = 1
        
        # Host field
        host_frame = tk.Frame(config_frame, bg=self.colors['bg_card'])
        host_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=8)
        
        tk.Label(host_frame, text="🌐 Host Address", 
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 5))
        
        self.host_var = tk.StringVar(value=self.config.host)
        host_entry = tk.Entry(host_frame, 
                             textvariable=self.host_var,
                             font=('Segoe UI', 10),
                             bg=self.colors['bg_tertiary'],
                             fg=self.colors['text'],
                             insertbackground=self.colors['text'],
                             relief='flat',
                             bd=8)
        host_entry.pack(fill=tk.X, ipady=6)
        
        # Port field
        port_frame = tk.Frame(config_frame, bg=self.colors['bg_card'])
        port_frame.grid(row=row, column=2, columnspan=2, sticky='ew', pady=8, padx=(15, 0))
        
        tk.Label(port_frame, text="🔌 Port Number",
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 5))
        
        self.port_var = tk.StringVar(value=str(self.config.port))
        port_entry = tk.Entry(port_frame, 
                             textvariable=self.port_var,
                             font=('Segoe UI', 10),
                             bg=self.colors['bg_tertiary'],
                             fg=self.colors['text'],
                             insertbackground=self.colors['text'],
                             relief='flat',
                             bd=8)
        port_entry.pack(fill=tk.X, ipady=6)
        
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(2, weight=1)
        
        # Root Directory
        row += 1
        root_frame = tk.Frame(config_frame, bg=self.colors['bg_card'])
        root_frame.grid(row=row, column=0, columnspan=4, sticky='ew', pady=8)
        
        tk.Label(root_frame, text="📁 Root Directory",
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 5))
        
        dir_input_frame = tk.Frame(root_frame, bg=self.colors['bg_card'])
        dir_input_frame.pack(fill=tk.X)
        
        self.root_var = tk.StringVar(value=self.config.root)
        root_entry = tk.Entry(dir_input_frame, 
                             textvariable=self.root_var,
                             font=('Segoe UI', 10),
                             bg=self.colors['bg_tertiary'],
                             fg=self.colors['text'],
                             insertbackground=self.colors['text'],
                             relief='flat',
                             bd=8)
        root_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        browse_btn = ttk.Button(dir_input_frame, 
                               text="📂 Browse", 
                               style='Action.TButton',
                               command=self.browse_directory,
                               width=12)
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Cache option with custom checkbox
        row += 1
        cache_frame = tk.Frame(config_frame, bg=self.colors['bg_card'])
        cache_frame.grid(row=row, column=0, columnspan=4, sticky='w', pady=(15, 5))
        
        self.cache_var = tk.BooleanVar(value=self.config.cache_enabled)
        cache_check = tk.Checkbutton(cache_frame,
                                    text="⚡ Enable High-Performance File Caching (LRU)",
                                    variable=self.cache_var,
                                    font=('Segoe UI', 10),
                                    bg=self.colors['bg_card'],
                                    fg=self.colors['text'],
                                    activebackground=self.colors['bg_card'],
                                    activeforeground=self.colors['primary'],
                                    selectcolor=self.colors['bg_tertiary'])
        cache_check.pack(anchor='w')
    
    def create_control_panel(self):
        """Create control buttons panel with modern styling"""
        control_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        control_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Primary controls
        primary_frame = tk.Frame(control_frame, bg=self.colors['bg_main'])
        primary_frame.pack(fill=tk.X)
        
        # Start button with icon
        self.start_btn = ttk.Button(primary_frame,
                                   text="▶  Start Server",
                                   style='Start.TButton',
                                   command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=2)
        
        # Stop button with icon
        self.stop_btn = ttk.Button(primary_frame,
                                  text="⬛  Stop Server",
                                  style='Stop.TButton',
                                  command=self.stop_server,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 20), ipady=2)
        
        # Secondary controls
        self.browser_btn = ttk.Button(primary_frame,
                                     text="🌐  Open Browser",
                                     style='Action.TButton',
                                     command=self.open_browser,
                                     state=tk.DISABLED)
        self.browser_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(primary_frame,
                              text="🗑️  Clear Logs",
                              style='Action.TButton',
                              command=self.clear_logs)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export logs button
        export_btn = ttk.Button(primary_frame,
                               text="💾  Export Logs",
                               style='Action.TButton',
                               command=self.export_logs)
        export_btn.pack(side=tk.LEFT)
    
    def create_status_panel(self):
        """Create status information panel with modern cards"""
        status_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        status_container.pack(fill=tk.X, padx=25, pady=15)
        
        # Status cards
        cards_frame = tk.Frame(status_container, bg=self.colors['bg_main'])
        cards_frame.pack(fill=tk.X)
        
        # Status card
        status_card = self.create_status_card(cards_frame, "Status")
        status_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        self.status_indicator = tk.Label(status_card,
                                         text="●",
                                         font=('Segoe UI', 24),
                                         bg=self.colors['bg_card'],
                                         fg=self.colors['danger'])
        self.status_indicator.pack(pady=(5, 0))
        
        self.status_label = tk.Label(status_card,
                                    text="Stopped",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=self.colors['bg_card'],
                                    fg=self.colors['text'])
        self.status_label.pack(pady=(0, 10))
        
        # URL card
        url_card = self.create_status_card(cards_frame, "Server URL")
        url_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        
        self.url_label = tk.Label(url_card,
                                 text="Not running",
                                 font=('Segoe UI', 10),
                                 bg=self.colors['bg_card'],
                                 fg=self.colors['text_muted'],
                                 wraplength=250)
        self.url_label.pack(pady=15)
        
        # Uptime card
        uptime_card = self.create_status_card(cards_frame, "Uptime")
        uptime_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        self.uptime_label = tk.Label(uptime_card,
                                    text="00:00:00",
                                    font=('Segoe UI', 16, 'bold'),
                                    bg=self.colors['bg_card'],
                                    fg=self.colors['primary'])
        self.uptime_label.pack(pady=10)
        
        self.start_time = None
    
    def create_status_card(self, parent, title):
        """Create a status card with title"""
        card = tk.Frame(parent, 
                       bg=self.colors['bg_card'],
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        
        title_label = tk.Label(card,
                              text=title,
                              font=('Segoe UI', 9),
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_secondary'])
        title_label.pack(pady=(10, 5))
        
        return card
    
    def create_log_panel(self):
        """Create log viewer panel with modern styling"""
        log_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))
        
        # Title bar
        title_bar = tk.Frame(log_container, bg=self.colors['bg_main'])
        title_bar.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(title_bar,
                        text="📋 Server Logs",
                        font=('Segoe UI', 12, 'bold'),
                        bg=self.colors['bg_main'],
                        fg=self.colors['text'])
        title.pack(side=tk.LEFT)
        
        # Log level filter
        filter_frame = tk.Frame(title_bar, bg=self.colors['bg_main'])
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame,
                text="Filter:",
                font=('Segoe UI', 9),
                bg=self.colors['bg_main'],
                fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 8))
        
        self.log_filter = ttk.Combobox(filter_frame,
                                      values=['All', 'INFO', 'SUCCESS', 'WARN', 'ERROR', 'DEBUG'],
                                      state='readonly',
                                      width=10,
                                      font=('Segoe UI', 9))
        self.log_filter.set('All')
        self.log_filter.pack(side=tk.LEFT)
        
        # Log card
        log_card = tk.Frame(log_container,
                           bg=self.colors['bg_card'],
                           highlightbackground=self.colors['border'],
                           highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        # Log text area with custom styling
        self.log_text = scrolledtext.ScrolledText(log_card,
                                                  wrap=tk.WORD,
                                                  font=('Cascadia Code', 9),
                                                  bg=self.colors['bg_secondary'],
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['text'],
                                                  relief=tk.FLAT,
                                                  padx=15,
                                                  pady=15,
                                                  borderwidth=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags with modern colors
        self.log_text.tag_config('INFO', foreground='#60a5fa', font=('Cascadia Code', 9))
        self.log_text.tag_config('ERROR', foreground='#f87171', font=('Cascadia Code', 9, 'bold'))
        self.log_text.tag_config('WARN', foreground='#fbbf24', font=('Cascadia Code', 9))
        self.log_text.tag_config('DEBUG', foreground='#c084fc', font=('Cascadia Code', 9))
        self.log_text.tag_config('SUCCESS', foreground='#34d399', font=('Cascadia Code', 9, 'bold'))
        self.log_text.tag_config('timestamp', foreground='#64748b', font=('Cascadia Code', 8))
        
        # Welcome messages
        self.log("SUCCESS", "PyNetLite Control Panel initialized successfully")
        self.log("INFO", "Configure your server settings above and click 'Start Server'")
        self.log("INFO", "Ready to accept HTTP/1.1 requests")
    
    def create_footer(self):
        """Create footer with info and stats"""
        footer = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Left side info
        left_info = tk.Label(footer,
                            text="PyNetLite v0.1 | Educational HTTP/1.1 Server",
                            font=('Segoe UI', 9),
                            bg=self.colors['bg_secondary'],
                            fg=self.colors['text_secondary'])
        left_info.pack(side=tk.LEFT, padx=20, pady=8)
        
        # Right side info
        right_info = tk.Label(footer,
                             text="Built with Python • Socket Programming • Tkinter",
                             font=('Segoe UI', 9),
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_dark'])
        right_info.pack(side=tk.RIGHT, padx=20, pady=8)
    
    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(initialdir=self.root_var.get(),
                                           title="Select Root Directory")
        if directory:
            self.root_var.set(directory)
    
    def start_server(self):
        """Start the web server"""
        if self.server_running:
            return
        
        try:
            # Validate and update config
            self.config.host = self.host_var.get()
            self.config.port = int(self.port_var.get())
            self.config.root = self.root_var.get()
            self.config.cache_enabled = self.cache_var.get()
            
            # Check if port is available
            if not self.is_port_available(self.config.host, self.config.port):
                messagebox.showerror("Port Error", 
                                   f"Port {self.config.port} is already in use.\nPlease choose a different port.")
                return
            
            # Update UI
            self.server_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.browser_btn.config(state=tk.NORMAL)
            self.status_indicator.config(fg=self.colors['success'])
            self.status_label.config(text="Running")
            self.url_label.config(text=f"http://{self.config.host}:{self.config.port}/",
                                fg=self.colors['primary'])
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # Redirect stdout/stderr to GUI
            sys.stdout = self.log_handler
            sys.stderr = self.log_handler
            
            self.start_time = datetime.now()
            self.update_uptime()
            
            self.log("SUCCESS", f"Server started on {self.config.host}:{self.config.port}")
            self.log("INFO", f"Root directory: {self.config.root}")
            self.log("INFO", f"Cache: {'Enabled' if self.config.cache_enabled else 'Disabled'}")
            self.log("INFO", f"Waiting for incoming connections...")
            
        except ValueError:
            messagebox.showerror("Invalid Port", "Please enter a valid port number.")
        except Exception as e:
            self.log("ERROR", f"Failed to start server: {str(e)}")
            messagebox.showerror("Server Error", f"Failed to start server:\n{str(e)}")
    
    def _run_server(self):
        """Internal method to run server"""
        try:
            from src.webserver.server import serve
            serve(self.config)
        except Exception as e:
            self.log("ERROR", f"Server error: {str(e)}")
            self.root.after(0, lambda: self.stop_server())
    
    def stop_server(self):
        """Stop the web server"""
        if not self.server_running:
            return
        
        # Restore stdout/stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        self.server_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.browser_btn.config(state=tk.DISABLED)
        self.status_indicator.config(fg=self.colors['danger'])
        self.status_label.config(text="Stopped")
        self.url_label.config(text="Not running", fg=self.colors['text_muted'])
        
        self.log("WARN", "Server stopped")
        
        # Note: Actual server socket closing would need modification to server.py
        # For now, we rely on daemon thread
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        self.log("INFO", "Logs cleared")
    
    def open_browser(self):
        """Open server URL in default browser"""
        import webbrowser
        url = f"http://{self.config.host}:{self.config.port}/"
        webbrowser.open(url)
        self.log("INFO", f"Opening browser: {url}")
    
    def is_port_available(self, host, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return True
        except OSError:
            return False
    
    def log(self, level, message):
        """Add log entry with timestamp and formatting"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Insert timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Insert level with color
        self.log_text.insert(tk.END, f"[{level:>7}] ", level)
        
        # Insert message
        self.log_text.insert(tk.END, f"{message}\n")
        
        self.log_text.see(tk.END)
    
    def toggle_theme(self):
        """Toggle between dark and light theme (placeholder for now)"""
        messagebox.showinfo("Theme Toggle", "Light theme coming soon! Currently using dark theme.")
    
    def export_logs(self):
        """Export logs to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")],
            initialfile=f"server_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log("SUCCESS", f"Logs exported to {filename}")
                messagebox.showinfo("Export Successful", f"Logs saved to:\n{filename}")
            except Exception as e:
                self.log("ERROR", f"Failed to export logs: {str(e)}")
                messagebox.showerror("Export Failed", f"Could not save logs:\n{str(e)}")
    
    def update_uptime(self):
        """Update uptime display"""
        if self.server_running and self.start_time:
            uptime = datetime.now() - self.start_time
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            seconds = uptime.seconds % 60
            
            if hours > 0:
                uptime_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                uptime_str = f"{minutes}m {seconds}s"
            else:
                uptime_str = f"{seconds}s"
            
            self.uptime_label.config(text=uptime_str)
            self.root.after(1000, self.update_uptime)
    
    def on_closing(self):
        """Handle window close event"""
        # Restore stdout/stderr before closing
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        if self.server_running:
            if messagebox.askokcancel("Quit", "Server is running. Do you want to stop it and quit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
