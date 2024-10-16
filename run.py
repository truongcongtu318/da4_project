import tkinter as tk
from tkinter import messagebox, ttk
import threading
import logging
import psutil
from app import create_app
from werkzeug.serving import make_server
import ipaddress  # Thêm thư viện để kiểm tra địa chỉ IP

class TextHandler(logging.Handler):
    def __init__(self, treeview):
        logging.Handler.__init__(self)
        self.treeview = treeview

    def emit(self, record):
        msg = self.format(record)
        time = self.formatTime(record)  # Lấy thời gian từ bản ghi
        level = record.levelname
        # Lấy thông tin từ thông điệp log
        message = record.msg

        # Xác định màu sắc dựa trên mức độ log
        if level == "INFO":
            color = "black"
        elif level == "ERROR":
            color = "red"
        else:
            color = "black"

        # Thêm log vào treeview với màu sắc
        self.treeview.insert("", "end", values=(time, level, message), tags=(level))
        self.treeview.tag_configure(level, foreground=color)

    def formatTime(self, record, datefmt=None):
        """Trả về thời gian của bản ghi log."""
        if datefmt:
            return record.asctime
        else:
            return self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Flask Server")

        self.app = create_app()  # Khởi tạo app ở đây

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.create_log_tab()
        self.create_performance_tab()
        self.create_routes_tab()
        self.create_config_tab()

        # Arrange buttons and status label in one row
        button_frame = tk.Frame(master)
        button_frame.pack(pady=5)

        # Thay đổi màu sắc cho các nút
        self.start_button = tk.Button(button_frame, text="Start Server", command=self.start_server, bg="darkgreen", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Shutdown Server", command=self.stop_server, state=tk.DISABLED, bg="darkred", fg="white")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_log_button = tk.Button(button_frame, text="Clear Logs", command=self.clear_logs, bg="darkblue", fg="white")
        self.clear_log_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(button_frame, text="Status: Not Started")
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.flask_thread = None
        self.server = None
        self.app.logger.setLevel(logging.INFO)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_log_tab(self):
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Logs")

        # Create treeview for logs
        self.log_tree = ttk.Treeview(log_tab, columns=("Time", "Level", "Message"), show="headings")
        self.log_tree.heading("Time", text="Time")
        self.log_tree.heading("Level", text="Level")
        self.log_tree.heading("Message", text="Message")

        # Set column widths
        self.log_tree.column("Time", width=120)
        self.log_tree.column("Level", width=80)
        self.log_tree.column("Message", width=500)

        self.log_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a scrollbar for the treeview
        scrollbar = ttk.Scrollbar(log_tab, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Set up logging handler
        self.text_handler = TextHandler(self.log_tree)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.text_handler.setFormatter(formatter)
        self.app.logger.addHandler(self.text_handler)

    def clear_logs(self):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

    def create_performance_tab(self):
        performance_tab = ttk.Frame(self.notebook)
        self.notebook.add(performance_tab, text="Performance")

        self.cpu_label = tk.Label(performance_tab, text="CPU Usage: ")
        self.cpu_label.pack(pady=5)

        self.memory_label = tk.Label(performance_tab, text="Memory Usage: ")
        self.memory_label.pack(pady=5)

        self.refresh_button = tk.Button(performance_tab, text="Refresh Performance", command=self.refresh_performance, bg="yellow", fg="black")
        self.refresh_button.pack(pady=5)

    def refresh_performance(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.memory_label.config(text=f"Memory Usage: {memory_usage}%")

    def create_routes_tab(self):
        routes_tab = ttk.Frame(self.notebook)
        self.notebook.add(routes_tab, text="Routes")

        self.routes_tree = ttk.Treeview(routes_tab, columns=("Method", "Path"), show="headings")
        self.routes_tree.heading("Method", text="Method")
        self.routes_tree.heading("Path", text="Path")
        self.routes_tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.refresh_routes_button = tk.Button(routes_tab, text="Refresh Routes", command=self.refresh_routes, bg="lightgreen", fg="black")
        self.refresh_routes_button.pack(pady=5)

    def refresh_routes(self):
        self.routes_tree.delete(*self.routes_tree.get_children())
        for rule in self.app.url_map.iter_rules():
            self.routes_tree.insert("", "end", values=(', '.join(rule.methods), rule.rule))

    def create_config_tab(self):
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="Configuration")

        # Create a frame for the configuration inputs
        config_frame = tk.Frame(config_tab)
        config_frame.pack(padx=10, pady=10)

        tk.Label(config_frame, text="IP:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = tk.Entry(config_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.ip_entry.insert(0, "0.0.0.0")  # Default value for IP

        tk.Label(config_frame, text="Port:").grid(row=1, column=0, padx=5, pady=5)
        self.port_entry = tk.Entry(config_frame)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        self.port_entry.insert(0, "5000")  # Default value for Port

        self.save_config_button = tk.Button(config_frame, text="Save Configuration", command=self.save_config, bg="lightblue", fg="black")
        self.save_config_button.grid(row=2, column=0, columnspan=2, pady=10)

    def save_config(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        # Save configuration to file or global variable if needed
        messagebox.showinfo("Notification", f"Configuration saved: IP={ip}, Port={port}")

    def start_server(self):
        # Stop server if running
        if self.server:
            self.stop_server()

        host = self.ip_entry.get()
        port = int(self.port_entry.get())

        # Check if the IP address is valid
        try:
            ipaddress.ip_address(host)  # Validate the IP address
        except ValueError:
            messagebox.showerror("Error", "Invalid IP address. Please enter a valid one.")
            return

        self.app.config['THREADED'] = True
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        
        try:
            self.server = make_server(host, port, self.app, threaded=True)
            self.flask_thread = threading.Thread(target=self.server.serve_forever)
            self.flask_thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Update log with the new IP address and port
            self.app.logger.info(f"Server started: {host}:{port}")
            self.status_label.config(text="Status: Running")  # Update status

        except Exception as e:
            self.app.logger.error(f"Error starting server: {e}")
            messagebox.showerror("Error", f"Could not start server: {e}")

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.flask_thread.join()
            self.server = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.app.logger.info("Server has been stopped")
            self.status_label.config(text="Status: Stopped")  # Update status

    def on_closing(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            if self.server:
                self.stop_server()
            self.app.logger.info("Application has been closed")
            self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()