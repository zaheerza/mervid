#!/usr/bin/env python3
"""
Video Merger Application
A GUI application to merge multiple video clips into one video file.
Supports MP4, AVI, MOV, MKV, WMV, FLV, and WebM formats.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

# Video processing imports - handle both moviepy 1.x and 2.x
try:
    # moviepy 2.0+ (new API)
    from moviepy import VideoFileClip, concatenate_videoclips
except ImportError:
    try:
        # moviepy 1.x (old API)
        from moviepy.editor import VideoFileClip, concatenate_videoclips
    except ImportError:
        print("Error: moviepy is not installed. Please run: pip install moviepy")
        sys.exit(1)


class VideoMergerApp:
    """Main application class for the Video Merger GUI."""

    # Supported video formats
    SUPPORTED_FORMATS = (
        ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.mpeg *.mpg *.m4v"),
        ("MP4 Files", "*.mp4"),
        ("AVI Files", "*.avi"),
        ("MOV Files", "*.mov"),
        ("MKV Files", "*.mkv"),
        ("WMV Files", "*.wmv"),
        ("FLV Files", "*.flv"),
        ("WebM Files", "*.webm"),
        ("All Files", "*.*"),
    )

    def __init__(self, root):
        """Initialize the application."""
        print("DEBUG: Initializing VideoMergerApp...")
        self.root = root
        self.root.title("Video Merger")
        self.root.geometry("700x550")
        self.root.minsize(600, 450)
        print("DEBUG: Window configured")

        # List to store video file paths
        self.video_files = []

        # Flag to track if merge is in progress
        self.merging = False

        # Setup the UI
        print("DEBUG: Setting up UI...")
        try:
            self._setup_ui()
            print("DEBUG: UI setup complete")
        except Exception as e:
            print(f"ERROR during UI setup: {e}")
            import traceback
            traceback.print_exc()

    def _setup_ui(self):
        """Setup the user interface."""
        print("DEBUG: Creating main frame...")
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        print("DEBUG: Main frame created")

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title Label
        title_label = ttk.Label(
            main_frame,
            text="Video Merger",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # File list frame
        list_frame = ttk.LabelFrame(main_frame, text="Video Files to Merge", padding="5")
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Listbox with scrollbar
        self.file_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Consolas", 10)
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons frame for file operations
        file_buttons_frame = ttk.Frame(main_frame)
        file_buttons_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(
            file_buttons_frame,
            text="Add Videos",
            command=self._add_videos
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            file_buttons_frame,
            text="Remove Selected",
            command=self._remove_selected
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            file_buttons_frame,
            text="Clear All",
            command=self._clear_all
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            file_buttons_frame,
            text="Move Up",
            command=self._move_up
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            file_buttons_frame,
            text="Move Down",
            command=self._move_down
        ).pack(side=tk.LEFT)

        # Output settings frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="5")
        output_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        output_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        ttk.Button(
            output_frame,
            text="Browse...",
            command=self._browse_output
        ).grid(row=0, column=2)

        # Resolution settings
        ttk.Label(output_frame, text="Resolution:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))

        resolution_frame = ttk.Frame(output_frame)
        resolution_frame.grid(row=1, column=1, sticky="w", pady=(5, 0))

        self.resolution_var = tk.StringVar(value="original")
        ttk.Radiobutton(
            resolution_frame,
            text="Original (from first video)",
            variable=self.resolution_var,
            value="original"
        ).pack(side=tk.LEFT)

        ttk.Radiobutton(
            resolution_frame,
            text="720p",
            variable=self.resolution_var,
            value="720p"
        ).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Radiobutton(
            resolution_frame,
            text="1080p",
            variable=self.resolution_var,
            value="1080p"
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready. Add videos to merge.")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Merge button
        self.merge_button = ttk.Button(
            main_frame,
            text="Merge Videos",
            command=self._start_merge,
            style="Accent.TButton"
        )
        self.merge_button.grid(row=5, column=0, pady=(0, 5))

        # Info label
        info_text = "Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM, MPEG"
        info_label = ttk.Label(main_frame, text=info_text, font=("Helvetica", 8))
        info_label.grid(row=6, column=0)

    def _add_videos(self):
        """Open file dialog to add video files."""
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=self.SUPPORTED_FORMATS
        )

        for file_path in files:
            if file_path not in self.video_files:
                self.video_files.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))

        self._update_status()

    def _remove_selected(self):
        """Remove selected videos from the list."""
        selected_indices = list(self.file_listbox.curselection())
        # Remove in reverse order to maintain correct indices
        for index in reversed(selected_indices):
            self.file_listbox.delete(index)
            del self.video_files[index]

        self._update_status()

    def _clear_all(self):
        """Clear all videos from the list."""
        self.file_listbox.delete(0, tk.END)
        self.video_files.clear()
        self._update_status()

    def _move_up(self):
        """Move selected video up in the list."""
        selected = self.file_listbox.curselection()
        if not selected or selected[0] == 0:
            return

        index = selected[0]
        # Swap in data list
        self.video_files[index], self.video_files[index-1] = \
            self.video_files[index-1], self.video_files[index]

        # Update listbox
        text = self.file_listbox.get(index)
        self.file_listbox.delete(index)
        self.file_listbox.insert(index-1, text)
        self.file_listbox.selection_set(index-1)

    def _move_down(self):
        """Move selected video down in the list."""
        selected = self.file_listbox.curselection()
        if not selected or selected[0] == len(self.video_files) - 1:
            return

        index = selected[0]
        # Swap in data list
        self.video_files[index], self.video_files[index+1] = \
            self.video_files[index+1], self.video_files[index]

        # Update listbox
        text = self.file_listbox.get(index)
        self.file_listbox.delete(index)
        self.file_listbox.insert(index+1, text)
        self.file_listbox.selection_set(index+1)

    def _browse_output(self):
        """Open file dialog to select output file path."""
        file_path = filedialog.asksaveasfilename(
            title="Save Merged Video As",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 Files", "*.mp4"),
                ("AVI Files", "*.avi"),
                ("MOV Files", "*.mov"),
                ("MKV Files", "*.mkv"),
            ]
        )

        if file_path:
            self.output_path_var.set(file_path)

    def _update_status(self):
        """Update the status label."""
        count = len(self.video_files)
        if count == 0:
            self.status_var.set("Ready. Add videos to merge.")
        elif count == 1:
            self.status_var.set("1 video added. Add more videos to merge.")
        else:
            self.status_var.set(f"{count} videos ready to merge.")

    def _start_merge(self):
        """Start the merge process in a separate thread."""
        if self.merging:
            messagebox.showwarning("Warning", "Merge already in progress!")
            return

        if len(self.video_files) < 2:
            messagebox.showwarning("Warning", "Please add at least 2 videos to merge.")
            return

        output_path = self.output_path_var.get().strip()
        if not output_path:
            # Generate default output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                os.path.dirname(self.video_files[0]),
                f"merged_video_{timestamp}.mp4"
            )
            self.output_path_var.set(output_path)

        # Start merge in separate thread
        self.merging = True
        self.merge_button.configure(state="disabled")

        thread = threading.Thread(
            target=self._merge_videos,
            args=(output_path,),
            daemon=True
        )
        thread.start()

    def _merge_videos(self, output_path):
        """Merge videos (runs in separate thread)."""
        clips = []

        try:
            total_files = len(self.video_files)

            # Load all video clips
            for i, video_path in enumerate(self.video_files):
                self._update_progress(
                    (i / total_files) * 50,
                    f"Loading video {i+1}/{total_files}..."
                )

                clip = VideoFileClip(video_path)

                # Resize if needed
                resolution = self.resolution_var.get()
                if resolution == "720p":
                    clip = clip.resize(height=720)
                elif resolution == "1080p":
                    clip = clip.resize(height=1080)
                elif resolution == "original" and i > 0 and clips:
                    # Resize to match first video's dimensions
                    target_size = clips[0].size
                    clip = clip.resize(newsize=target_size)

                clips.append(clip)

            self._update_progress(50, "Concatenating videos...")

            # Concatenate all clips
            final_clip = concatenate_videoclips(clips, method="compose")

            self._update_progress(60, "Writing output file...")

            # Write the output file
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                logger=None,  # Suppress moviepy's progress bar
                threads=4
            )

            self._update_progress(100, f"Done! Saved to: {os.path.basename(output_path)}")

            # Cleanup
            final_clip.close()
            for clip in clips:
                clip.close()

            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Videos merged successfully!\n\nSaved to:\n{output_path}"
            ))

        except Exception as e:
            error_msg = str(e)
            self._update_progress(0, f"Error: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Failed to merge videos:\n\n{error_msg}"
            ))

            # Cleanup on error
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass

        finally:
            self.merging = False
            self.root.after(0, lambda: self.merge_button.configure(state="normal"))

    def _update_progress(self, value, status):
        """Update progress bar and status label (thread-safe)."""
        self.root.after(0, lambda: self.progress_var.set(value))
        self.root.after(0, lambda: self.status_var.set(status))


def main():
    """Main entry point for the application."""
    print("DEBUG: Starting main()...")
    root = tk.Tk()
    print("DEBUG: Tk root created")

    # Set app icon if available
    try:
        # This will work when running as executable
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
    except:
        pass

    # Create and run the application
    print("DEBUG: Creating VideoMergerApp...")
    app = VideoMergerApp(root)
    print("DEBUG: VideoMergerApp created")

    # Center window on screen
    print("DEBUG: Centering window...")
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    print(f"DEBUG: Window size: {width}x{height}")
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")
    print(f"DEBUG: Window centered at {x},{y}")

    print("DEBUG: Starting mainloop...")
    root.mainloop()
    print("DEBUG: Mainloop ended")


if __name__ == "__main__":
    main()
