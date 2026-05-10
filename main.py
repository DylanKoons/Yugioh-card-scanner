import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import cv2
from PIL import Image, ImageTk
import threading
from camera import CameraCapture
from ocr import CardOCR
from api import YGOProDeckAPI

class CardScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yu-Gi-Oh Card Scanner")
        self.root.geometry("1200x800")

        self.camera = None
        self.ocr = None
        self.scanning = False
        self.paused = False
        self.last_set_code = None

        self._setup_ui()
        self._initialize_components()
        self.root.bind('<space>', self._on_spacebar)

    def _setup_ui(self):
        """Setup GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side - Camera feed
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(left_frame, text="Camera Feed", font=("Arial", 12, "bold")).pack()
        self.camera_label = ttk.Label(left_frame, background="black")
        self.camera_label.pack(fill=tk.BOTH, expand=True)

        # Right side - Results
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right_frame, text="Scan Results", font=("Arial", 12, "bold")).pack()

        # Set code display
        ttk.Label(right_frame, text="Set Code:", font=("Arial", 10)).pack(anchor=tk.W)
        self.set_code_var = tk.StringVar(value="Waiting for scan...")
        self.set_code_label = ttk.Label(right_frame, textvariable=self.set_code_var,
                                        foreground="blue", font=("Arial", 14, "bold"))
        self.set_code_label.pack(anchor=tk.W, pady=(0, 10))

        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(right_frame, textvariable=self.status_var,
                                      foreground="green", font=("Arial", 9))
        self.status_label.pack(anchor=tk.W, pady=(0, 10))

        # Extracted text display
        ttk.Label(right_frame, text="Detected Text:", font=("Arial", 9)).pack(anchor=tk.W)
        self.detected_text_var = tk.StringVar(value="")
        self.detected_text_label = ttk.Label(right_frame, textvariable=self.detected_text_var,
                                             foreground="gray", font=("Arial", 8), wraplength=300, justify=tk.LEFT)
        self.detected_text_label.pack(anchor=tk.W, pady=(0, 10))

        # Card info text area
        ttk.Label(right_frame, text="Card Information:", font=("Arial", 10)).pack(anchor=tk.W)
        self.results_text = scrolledtext.ScrolledText(right_frame, height=25, width=40)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_btn = ttk.Button(button_frame, text="Start Scanning", command=self.start_scanning)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(button_frame, text="Stop Scanning", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # Manual search frame
        manual_frame = ttk.LabelFrame(right_frame, text="Manual Search", padding=5)
        manual_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(manual_frame, text="Set Code:").pack(side=tk.LEFT, padx=(0, 5))
        self.manual_code_var = tk.StringVar()
        code_entry = ttk.Entry(manual_frame, textvariable=self.manual_code_var, width=15)
        code_entry.pack(side=tk.LEFT, padx=(0, 5))
        code_entry.bind('<Return>', lambda e: self._manual_search())

        ttk.Button(manual_frame, text="Search", command=self._manual_search).pack(side=tk.LEFT)

    def _initialize_components(self):
        """Initialize camera and OCR"""
        try:
            self.camera = CameraCapture(camera_id=0)
            self.ocr = CardOCR()
            messagebox.showinfo("Success", "Camera and OCR initialized successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {e}")

    def start_scanning(self):
        """Start scanning cards"""
        try:
            if not self.camera or not self.ocr:
                messagebox.showerror("Error", "Components not initialized")
                return

            self.camera.start()
            self.scanning = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.results_text.delete("1.0", tk.END)

            # Start camera update loop
            self._update_camera_feed()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scanning: {e}")

    def stop_scanning(self):
        """Stop scanning cards"""
        self.scanning = False
        if self.camera:
            self.camera.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.camera_label.config(image="")
        self.set_code_var.set("Waiting for scan...")

    def _update_camera_feed(self):
        """Update camera feed and process OCR"""
        if not self.scanning or self.paused:
            return

        frame = self.camera.get_frame()
        if frame is not None:
            # Display camera feed
            self._display_frame(frame)

            # Process OCR
            set_code, extracted_texts = self.ocr.extract_set_code(frame)

            # Show extracted text
            if extracted_texts:
                text_display = "\n".join([f"{text} ({conf:.0%})" for text, conf in extracted_texts[:5]])
                self.detected_text_var.set(text_display)

            if set_code and set_code != self.last_set_code:
                self.last_set_code = set_code
                self.set_code_var.set(f"Set Code: {set_code}")
                self.status_var.set("✓ Card scanned! Press SPACE to continue...")
                self.paused = True
                self._lookup_card(set_code)
                return

        # Schedule next update
        self.root.after(100, self._update_camera_feed)

    def _display_frame(self, frame):
        """Display camera frame in GUI"""
        # Resize frame
        frame = cv2.resize(frame, (480, 360))

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to PhotoImage
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)

        self.camera_label.config(image=photo)
        self.camera_label.image = photo  # Keep a reference

    def _lookup_card(self, set_code):
        """Lookup card information from API"""
        def lookup_thread():
            try:
                results = YGOProDeckAPI.search_by_set_code(set_code)

                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete("1.0", tk.END)

                if results:
                    for i, card in enumerate(results, 1):
                        self.results_text.insert(tk.END, f"--- Card {i} ---\n")
                        self.results_text.insert(tk.END, f"Name: {card.get('name', 'N/A')}\n")
                        self.results_text.insert(tk.END, f"Type: {card.get('type', 'N/A')}\n")
                        self.results_text.insert(tk.END, f"ATK: {card.get('atk', 'N/A')} ")
                        self.results_text.insert(tk.END, f"DEF: {card.get('def', 'N/A')}\n")
                        self.results_text.insert(tk.END, f"Level: {card.get('level', 'N/A')}\n")
                        self.results_text.insert(tk.END, f"Rarity: {card.get('set_rarity', 'N/A')}\n")
                        self.results_text.insert(tk.END, f"Desc: {card.get('desc', 'N/A')}\n\n")
                else:
                    self.results_text.insert(tk.END, f"No cards found for set code: {set_code}\n")

                self.results_text.config(state=tk.DISABLED)
            except Exception as e:
                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, f"Error: {e}\n")
                self.results_text.config(state=tk.DISABLED)

        threading.Thread(target=lookup_thread, daemon=True).start()

    def on_closing(self):
        """Handle window closing"""
        self.stop_scanning()
        self.root.destroy()

    def _manual_search(self):
        """Search for set code entered manually"""
        set_code = self.manual_code_var.get().strip().upper()
        if not set_code:
            messagebox.showwarning("Input Error", "Please enter a set code")
            return

        self.set_code_var.set(f"Set Code: {set_code}")
        self.status_var.set("✓ Card scanned! Press SPACE to continue...")
        self.paused = True
        self._lookup_card(set_code)
        self.manual_code_var.delete(0, tk.END)

    def _on_spacebar(self, event):
        """Resume scanning on spacebar"""
        if self.scanning and self.paused:
            self.paused = False
            self.last_set_code = None
            self.status_var.set("Scanning...")
            self.detected_text_var.set("")
            self._update_camera_feed()


if __name__ == "__main__":
    root = tk.Tk()
    app = CardScannerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
