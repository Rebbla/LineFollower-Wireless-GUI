import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import socket
import time

class MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Monitor Trafobot")
        self.root.geometry('1250x850')

        self.judul = ["Motor", "Servo"]
        self.entries = []

        # Setup UDP
        self.udp_ip = "192.168.4.1"  # Ganti dengan IP ESP8266 Anda
        self.udp_port = 4210
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(1)

        ttk.Label(self.root, text="SISTEM MONITOR TRAFOBOT", font=("Segoe UI", 16, "bold"),
                  foreground="#0aa1ff").pack(pady=15)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.left_frame = ttk.Frame(main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.right_frame = ttk.Labelframe(main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.create_left_side()
        self.create_right_side()
        self.root.after(100, self.read_udp)

    def __del__(self):
        if hasattr(self, 'udp_socket'):
            self.udp_socket.close()

    def update_sensor_value(self, index, value):
        if 0 <= index < len(self.sensor_values):
            try:
                value = int(value)
                self.sensor_values[index]['value'] = value
            except ValueError:
                print(f"Error: Nilai bukan angka valid untuk Sensor {index+1}: {value}")


    def read_udp(self):
        try:
            data, addr = self.udp_socket.recvfrom(1024)
            line = data.decode(errors='ignore').strip()
            print(f"Received: {line}")
            if line:
                parts = line.split(',')
                if len(parts) == 5:
                    for i, val in enumerate(parts):
                        self.update_sensor_value(i, val)
                else:
                    print(f"Unexpected UDP format: {line}")
        except socket.timeout:
            pass
        except Exception as e:
            print(f"UDP read error: {e}")
        self.root.after(100, self.read_udp)

    def create_left_side(self):
        input_frame = ttk.Frame(self.left_frame)
        input_frame.pack(fill="x", pady=10)

        for i, label_text in enumerate(self.judul):
            label = ttk.Label(input_frame, text=f"{i+1}. {label_text}",
                              font=("Segoe UI", 13, "bold"), foreground="#0a75ff")
            label.grid(row=i, column=0, sticky="w", pady=6, padx=5)
            entry = ttk.Entry(input_frame, font=("Segoe UI", 13), width=18)
            entry.grid(row=i, column=1, pady=6, padx=5)
            self.entries.append(entry)
            btn = ttk.Button(input_frame, text="OK", width=4,
                             command=lambda e=entry, l=label_text: self.submit(e, l))
            btn.grid(row=i, column=2, padx=5, pady=6)

        map_nav_frame = ttk.Labelframe(self.left_frame, relief="ridge", text="Kontrol Tracker", bootstyle="primary")
        map_nav_frame.pack(pady=15, fill="both", expand=True)

        canvas_width = 350
        canvas_height = 160
        self.x_pos, self.y_pos, self.step = canvas_width // 2, canvas_height // 2, 10
        self.direction = "up"

        self.canvas = tk.Canvas(map_nav_frame, width=canvas_width, height=canvas_height, bg='skyblue')
        self.canvas.pack(pady=10)
        self.canvas.create_rectangle(1, 1, canvas_width-2, canvas_height-2, outline="#333", width=2)

        self.tracker = self.canvas.create_oval(self.x_pos-7, self.y_pos-7,
                                               self.x_pos+7, self.y_pos+7,
                                               fill="#007fff")

        btn_frame = ttk.Frame(map_nav_frame)
        btn_frame.pack(pady=8)

        style = ttk.Style()
        style.configure("Big.TButton", font=("Segoe UI", 12), padding=(10, 5))

        btn_opts = {"width": 10, "bootstyle": "primary"}

        ttk.Button(btn_frame, text="MAJU", command=self.move_up, style="Big.TButton", **btn_opts).grid(row=0, column=1, padx=8)
        ttk.Button(btn_frame, text="KIRI", command=self.move_left, style="Big.TButton", **btn_opts).grid(row=1, column=0, padx=8)
        ttk.Button(btn_frame, text="MUNDUR", command=self.move_down, style="Big.TButton", **btn_opts).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="KANAN", command=self.move_right, style="Big.TButton", **btn_opts).grid(row=1, column=2, padx=8)

        mode_frame = ttk.Frame(map_nav_frame)
        mode_frame.pack(pady=10)

        self.mode = tk.StringVar(value="MANUAL")

        ttk.Button(mode_frame, text="AUTO", width=10, command=self.set_auto, bootstyle="success").pack(side="left", padx=5)
        ttk.Button(mode_frame, text="MANUAL", width=10, command=self.set_manual, bootstyle="warning").pack(side="left", padx=5)
        ttk.Button(mode_frame, text="STOP ROBOT", width=12, command=self.move_stop, bootstyle="danger").pack(side="left", padx=5)
        ttk.Button(mode_frame, text="Cek Ping", command=self.check_ping, bootstyle="info").pack(side="left", padx=5)

    def create_right_side(self):
        ttk.Label(self.right_frame, text="Status Sensor", font=("Segoe UI", 15, "bold")).pack(anchor='nw', pady=12, padx=10)

        style = ttk.Style()
        style.configure(
            "custom.Horizontal.TProgressbar",
            troughcolor='#ddd',
            background='#0a75ff',
            thickness=16
        )

        self.sensor_values = []

        for i in range(5):
            frame = ttk.Frame(self.right_frame)
            frame.pack(fill="x", pady=8, padx=10)

            lbl = ttk.Label(frame, text=f"Sensor {i + 1}", font=("Segoe UI", 13), foreground="#333333")
            lbl.pack(side="left", padx=(10, 5))

            pb = ttk.Progressbar(frame, style="custom.Horizontal.TProgressbar", orient="horizontal",
                                 length=220, mode='determinate', maximum=1, value=0)
            pb.pack(side="left", padx=5)

            self.sensor_values.append(pb)

    def move_tracker(self, dx, dy):
        new_x = self.x_pos + dx
        new_y = self.y_pos + dy

        if 0 < new_x < 350 and 0 < new_y < 160:
            self.canvas.move(self.tracker, dx, dy)
            self.x_pos = new_x
            self.y_pos = new_y

    def move_up(self):
        self.move_tracker(0, -self.step)
        self.direction = "up"
        self.send_command(b'maju')

    def move_down(self):
        self.move_tracker(0, self.step)
        self.direction = "down"
        self.send_command(b'mundur')

    def move_left(self):
        self.move_tracker(-self.step, 0)
        self.direction = "left"
        self.send_command(b'kiri')

    def move_right(self):
        self.move_tracker(self.step, 0)
        self.direction = "right"
        self.send_command(b'kanan')

    def move_stop(self):
        self.direction = "stop"
        self.send_command(b'stop')

    def send_command(self, command):
        try:
            self.udp_socket.sendto(command, (self.udp_ip, self.udp_port))
        except Exception as e:
            Messagebox.show_error("Error", f"Gagal mengirim perintah: {e}")

    def set_auto(self):
        self.mode.set("AUTO")
        self.send_command(b"MODE:AUTO")
        Messagebox.show_info("Mode", "Robot masuk ke mode AUTO")

    def set_manual(self):
        self.mode.set("MANUAL")
        self.send_command(b"MODE:MANUAL")
        Messagebox.show_info("Mode", "Robot masuk ke mode MANUAL")

    def submit(self, entry, label):
        val = entry.get()
        if val.isdigit() and 0 <= int(val) <= 200:
            Messagebox.show_info("Sukses", f"{label} sebesar: {val}")
            # Kirim sesuai format ke ESP8266
            if label.lower() == "motor":
                self.send_command(f"M:{val}".encode())
            elif label.lower() == "servo":
                self.send_command(f"S:{val}".encode())
        else:
            Messagebox.show_warning("Error", f"Input {label} harus angka 0-200.")

    def check_ping(self):
        try:
            self.udp_socket.sendto(b'ping', (self.udp_ip, self.udp_port))
            start_time = time.time()
            data, addr = self.udp_socket.recvfrom(1024)
            round_trip_time = (time.time() - start_time) * 1000
            Messagebox.show_info("Ping", f"Ping ke ESP8266: {round_trip_time:.2f} ms")
        except socket.timeout:
            Messagebox.show_error("Ping", "Tidak ada respon dari ESP8266.")
        except Exception as e:
            Messagebox.show_error("Error", f"Gagal melakukan ping: {e}")

if __name__ == "__main__":
    try:
        root = ttk.Window(themename="cosmo")
        app = MonitorApp(root)
        root.mainloop()
    finally:
        try:
            del app
        except:
            pass
