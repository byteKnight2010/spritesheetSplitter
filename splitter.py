from pathlib import Path
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import multiprocessing


class SpritesheetSplitterGUI:
  def __init__(self, root: tk.Tk):
    self.Root: tk.Tk = root
    self.Root.title("Spritesheet Splitter")
    self.Root.geometry("600x600")
    self.Root.resizable(False, False)
    
    self.SpriteSheetPath: tk.StringVar = tk.StringVar()
    self.OutputPath: tk.StringVar = tk.StringVar(value = str(Path.home() / "Downloads" / "spritesheet_frames"))
    self.FrameWidth: tk.StringVar = tk.StringVar(value = "32")
    self.FrameHeight: tk.StringVar = tk.StringVar(value = "32")
    self.Prefix: tk.StringVar = tk.StringVar(value = "frame")
    self.StartIndex: tk.StringVar = tk.StringVar(value = "0")
    self.Padding: tk.StringVar = tk.StringVar(value = "4")
    self.PreviewInfo: tk.StringVar = tk.StringVar(value = "No spritesheet loaded")
    
    self.CachedSpritesheet = None
    self.CachedPath = None
        
    self.setup_ui()
  
  def setup_ui(self):
    main_frame = ttk.Frame(self.Root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    title = ttk.Label(main_frame, text="Spritesheet Splitter", font=("Arial", 18, "bold"))
    title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
    ttk.Label(main_frame, text="Spritesheet:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
    sheet_frame = ttk.Frame(main_frame)
    sheet_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
    ttk.Entry(sheet_frame, textvariable=self.SpriteSheetPath, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    ttk.Button(sheet_frame, text="Browse...", command=self.browse_spritesheet).pack(side=tk.LEFT)
        
    preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
    preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
    ttk.Label(preview_frame, textvariable=self.PreviewInfo, foreground="blue", wraplength=520).pack()
    ttk.Label(main_frame, text="Frame Dimensions:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
    dims_frame = ttk.Frame(main_frame)
    dims_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
    
    ttk.Label(dims_frame, text="Width:").pack(side=tk.LEFT, padx=(0, 5))
    width_entry = ttk.Entry(dims_frame, textvariable=self.FrameWidth, width=10)
    width_entry.pack(side=tk.LEFT, padx=(0, 20))
        
    ttk.Label(dims_frame, text="Height:").pack(side=tk.LEFT, padx=(0, 5))
    height_entry = ttk.Entry(dims_frame, textvariable=self.FrameHeight, width=10)
    height_entry.pack(side=tk.LEFT)
        
    ttk.Button(dims_frame, text="Calculate", command=self.calculate_preview).pack(side=tk.LEFT, padx=(20, 0))
    ttk.Label(main_frame, text="Output Settings:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
    ttk.Label(main_frame, text="Output Folder:").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        
    output_frame = ttk.Frame(main_frame)
    output_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
    ttk.Entry(output_frame, textvariable=self.OutputPath, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT)
        
    ttk.Label(main_frame, text="Filename Prefix:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
    ttk.Entry(main_frame, textvariable=self.Prefix, width=20).grid(row=9, column=1, sticky=tk.W, pady=(0, 5))
        
    ttk.Label(main_frame, text="Start Index:").grid(row=10, column=0, sticky=tk.W, pady=(0, 5))
    ttk.Entry(main_frame, textvariable=self.StartIndex, width=20).grid(row=10, column=1, sticky=tk.W, pady=(0, 5))
        
    ttk.Label(main_frame, text="Zero Padding:").grid(row=11, column=0, sticky=tk.W, pady=(0, 5))
    ttk.Entry(main_frame, textvariable=self.Padding, width=20).grid(row=11, column=1, sticky=tk.W, pady=(0, 5))
        
    self.example_label = ttk.Label(main_frame, text="", foreground="gray")
    self.example_label.grid(row=12, column=0, columnspan=3, sticky=tk.W, pady=(5, 15))
    self.update_example()
        
    self.Prefix.trace_add("write", lambda *args: self.update_example())
    self.StartIndex.trace_add("write", lambda *args: self.update_example())
    self.Padding.trace_add("write", lambda *args: self.update_example())
        
    self.progress = ttk.Progressbar(main_frame, mode='determinate', length=560)
    self.progress.grid(row=13, column=0, columnspan=3, pady=(0, 10))
        
    self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
    self.status_label.grid(row=14, column=0, columnspan=3, pady=(0, 15))
        
    self.split_button = ttk.Button(main_frame, text="Split Spritesheet", command=self.start_split, style="Accent.TButton")
    self.split_button.grid(row=15, column=0, columnspan=3, pady=(0, 0))
        
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 12, "bold"))
    
  def update_example(self):
    try:
      prefix = self.Prefix.get() or "frame"
      start = int(self.StartIndex.get() or 0)
      pad = int(self.Padding.get() or 4)
      example = f"Example: {prefix}_{str(start).zfill(pad)}.png"
      self.example_label.config(text=example)
    except ValueError:
      self.example_label.config(text="Example: Invalid settings")
    
  def browse_spritesheet(self):
    filename = filedialog.askopenfilename(title="Select Spritesheet", filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),("All files", "*.*")])
    if filename:
      self.SpriteSheetPath.set(filename)
      self.CachedSpritesheet = None
      self.CachedPath = None
      self.calculate_preview()
    
  def browse_output(self):
    directory = filedialog.askdirectory(title="Select Output Folder")
    if directory:
      self.OutputPath.set(directory)
    
  def load_spritesheet(self):
    """Load and cache the spritesheet to avoid repeated file I/O"""
    path = self.SpriteSheetPath.get()
    if self.CachedPath != path or self.CachedSpritesheet is None:
      self.CachedSpritesheet = Image.open(path)
      self.CachedPath = path
    return self.CachedSpritesheet
    
  def calculate_preview(self):
    if not self.SpriteSheetPath.get():
      self.PreviewInfo.set("No spritesheet loaded")
      return
        
    try:
      img = self.load_spritesheet()
      width, height = img.size
            
      frame_w = int(self.FrameWidth.get())
      frame_h = int(self.FrameHeight.get())
            
      frames_x = width // frame_w
      frames_y = height // frame_h
      total = frames_x * frames_y
            
      info = (f"Spritesheet: {width}×{height}px | "f"Frames: {frames_x}×{frames_y} grid | "f"Total: {total} frames")
      self.PreviewInfo.set(info)
     
    except Exception as e:
      self.PreviewInfo.set(f"Error: {str(e)}")
      self.CachedSpritesheet = None
      self.CachedPath = None
    
  def start_split(self):
    if not self.SpriteSheetPath.get():
      messagebox.showerror("Error", "Please select a spritesheet file")
      return
        
    try:
      frame_w = int(self.FrameWidth.get())
      frame_h = int(self.FrameHeight.get())
      if frame_w <= 0 or frame_h <= 0:
        raise ValueError()
    except ValueError:
      messagebox.showerror("Error", "Frame dimensions must be positive integers")
      return
    
    thread = Thread(target=self.split_spritesheet)
    thread.daemon = True
    thread.start()
  
  def save_frame(self, args):
    """Worker function for parallel frame saving"""
    spritesheet, left, top, right, bottom, output_path = args
    frame = spritesheet.crop((left, top, right, bottom))
    frame.save(output_path, "PNG", optimize=False)
    return True
    
  def split_spritesheet(self):
    self.split_button.config(state="disabled")
    self.status_label.config(text="Processing...", foreground="orange")
    self.progress['value'] = 0
        
    try:
      spritesheet = self.load_spritesheet()
      sheet_width, sheet_height = spritesheet.size
      
      frame_w = int(self.FrameWidth.get())
      frame_h = int(self.FrameHeight.get())
      output_dir = Path(self.OutputPath.get())
      prefix = self.Prefix.get()
      start = int(self.StartIndex.get())
      pad = int(self.Padding.get())
            
      frames_x = sheet_width // frame_w
      frames_y = sheet_height // frame_h
      total = frames_x * frames_y
            
      output_dir.mkdir(parents=True, exist_ok=True)
      
      if total > 100:
        tasks = []
        for row in range(frames_y):
          for col in range(frames_x):
            left = col * frame_w
            top = row * frame_h
            right = left + frame_w
            bottom = top + frame_h
            
            num = start + (row * frames_x + col)
            filename = f"{prefix}_{str(num).zfill(pad)}.png"
            output_path = output_dir / filename
            
            tasks.append((spritesheet, left, top, right, bottom, output_path))
        
        # Use ThreadPoolExecutor for I/O-bound operations
        max_workers = min(multiprocessing.cpu_count() * 2, 16)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
          completed = 0
          for _ in executor.map(self.save_frame, tasks):
            completed += 1
            progress = (completed / total) * 100
            self.progress['value'] = progress
            self.Root.update_idletasks()
        
        count = total
      else:
        count = 0
        for row in range(frames_y):
          for col in range(frames_x):
            left = col * frame_w
            top = row * frame_h
            right = left + frame_w
            bottom = top + frame_h
                      
            frame = spritesheet.crop((left, top, right, bottom))
                      
            num = start + count
            filename = f"{prefix}_{str(num).zfill(pad)}.png"
            frame.save(output_dir / filename, "PNG", optimize=False)
                      
            count += 1
            progress = (count / total) * 100
            self.progress['value'] = progress
            self.Root.update_idletasks()
      
      self.status_label.config(text=f"Success! Extracted {count} frames to {output_dir}", foreground="green")
      messagebox.showinfo("Success", f"Successfully extracted {count} frames!\n\nSaved to:\n{output_dir}")
            
    except Exception as e:
      self.status_label.config(text=f"Error: {str(e)}", foreground="red")
      messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    finally:
      self.split_button.config(state="normal")


def main():
  ROOT: tk.Tk = tk.Tk()
  APP: SpritesheetSplitterGUI = SpritesheetSplitterGUI(ROOT)
  ROOT.mainloop()


if __name__ == "__main__":
  main()