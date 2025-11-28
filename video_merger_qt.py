#!/usr/bin/env python3
"""
Video Merger Application (PyQt5 Version)
A GUI application to merge multiple video clips into one video file.
Supports MP4, AVI, MOV, MKV, WMV, FLV, and WebM formats.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QRadioButton, QButtonGroup, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# Video processing imports - handle both moviepy 1.x and 2.x
try:
    from moviepy import VideoFileClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips
    except ImportError:
        print("Error: moviepy is not installed. Please run: pip install moviepy")
        sys.exit(1)


class MergeThread(QThread):
    """Thread for merging videos without blocking the UI."""

    progress = pyqtSignal(int, str)  # (percentage, status_message)
    finished = pyqtSignal(bool, str)  # (success, message)

    def __init__(self, video_files, output_path, resolution):
        super().__init__()
        self.video_files = video_files
        self.output_path = output_path
        self.resolution = resolution

    def run(self):
        """Run the merge process."""
        clips = []

        try:
            total_files = len(self.video_files)

            # Load all video clips
            for i, video_path in enumerate(self.video_files):
                self.progress.emit(
                    int((i / total_files) * 50),
                    f"Loading video {i+1}/{total_files}..."
                )

                clip = VideoFileClip(video_path)

                # Resize if needed
                if self.resolution == "720p":
                    clip = clip.resize(height=720)
                elif self.resolution == "1080p":
                    clip = clip.resize(height=1080)
                elif self.resolution == "original" and i > 0 and clips:
                    # Resize to match first video's dimensions
                    target_size = clips[0].size
                    clip = clip.resize(newsize=target_size)

                clips.append(clip)

            self.progress.emit(50, "Concatenating videos...")

            # Concatenate all clips
            final_clip = concatenate_videoclips(clips, method="compose")

            self.progress.emit(60, "Writing output file...")

            # Write the output file
            final_clip.write_videofile(
                self.output_path,
                codec="libx264",
                audio_codec="aac",
                logger=None,
                threads=4
            )

            self.progress.emit(100, f"Done! Saved to: {os.path.basename(self.output_path)}")

            # Cleanup
            final_clip.close()
            for clip in clips:
                clip.close()

            self.finished.emit(True, f"Videos merged successfully!\n\nSaved to:\n{self.output_path}")

        except Exception as e:
            error_msg = str(e)
            self.progress.emit(0, f"Error: {error_msg}")

            # Cleanup on error
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass

            self.finished.emit(False, f"Failed to merge videos:\n\n{error_msg}")


class VideoMergerWindow(QMainWindow):
    """Main window for the Video Merger application."""

    # Supported video formats
    SUPPORTED_FORMATS = "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.mpeg *.mpg *.m4v);;All Files (*.*)"

    def __init__(self):
        super().__init__()
        self.video_files = []
        self.merge_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Video Merger")
        self.setGeometry(100, 100, 700, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Title
        title_label = QLabel("Video Merger")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # File list group
        file_group = QGroupBox("Video Files to Merge")
        file_layout = QVBoxLayout()
        file_group.setLayout(file_layout)

        # List widget
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)

        # File control buttons
        file_btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Videos")
        self.add_btn.clicked.connect(self.add_videos)
        file_btn_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        file_btn_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        file_btn_layout.addWidget(self.clear_btn)

        self.up_btn = QPushButton("Move Up")
        self.up_btn.clicked.connect(self.move_up)
        file_btn_layout.addWidget(self.up_btn)

        self.down_btn = QPushButton("Move Down")
        self.down_btn.clicked.connect(self.move_down)
        file_btn_layout.addWidget(self.down_btn)

        file_layout.addLayout(file_btn_layout)
        main_layout.addWidget(file_group)

        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)

        # Output file path
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(QLabel("Output File:"))

        self.output_path_edit = QLineEdit()
        output_path_layout.addWidget(self.output_path_edit)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_output)
        output_path_layout.addWidget(self.browse_btn)

        output_layout.addLayout(output_path_layout)

        # Resolution options
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))

        self.resolution_group = QButtonGroup()

        self.original_radio = QRadioButton("Original (from first video)")
        self.original_radio.setChecked(True)
        self.resolution_group.addButton(self.original_radio)
        resolution_layout.addWidget(self.original_radio)

        self.radio_720p = QRadioButton("720p")
        self.resolution_group.addButton(self.radio_720p)
        resolution_layout.addWidget(self.radio_720p)

        self.radio_1080p = QRadioButton("1080p")
        self.resolution_group.addButton(self.radio_1080p)
        resolution_layout.addWidget(self.radio_1080p)

        resolution_layout.addStretch()
        output_layout.addLayout(resolution_layout)

        main_layout.addWidget(output_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready. Add videos to merge.")
        main_layout.addWidget(self.status_label)

        # Merge button
        self.merge_btn = QPushButton("Merge Videos")
        self.merge_btn.setMinimumHeight(40)
        merge_font = QFont()
        merge_font.setPointSize(12)
        merge_font.setBold(True)
        self.merge_btn.setFont(merge_font)
        self.merge_btn.clicked.connect(self.start_merge)
        main_layout.addWidget(self.merge_btn)

        # Info label
        info_label = QLabel("Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM, MPEG")
        info_font = QFont()
        info_font.setPointSize(8)
        info_label.setFont(info_font)
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)

    def add_videos(self):
        """Open file dialog to add video files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            self.SUPPORTED_FORMATS
        )

        for file_path in files:
            if file_path not in self.video_files:
                self.video_files.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))

        self.update_status()

    def remove_selected(self):
        """Remove selected videos from the list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            del self.video_files[row]

        self.update_status()

    def clear_all(self):
        """Clear all videos from the list."""
        self.file_list.clear()
        self.video_files.clear()
        self.update_status()

    def move_up(self):
        """Move selected video up in the list."""
        current_row = self.file_list.currentRow()
        if current_row <= 0:
            return

        # Swap in data list
        self.video_files[current_row], self.video_files[current_row - 1] = \
            self.video_files[current_row - 1], self.video_files[current_row]

        # Update list widget
        current_item = self.file_list.takeItem(current_row)
        self.file_list.insertItem(current_row - 1, current_item)
        self.file_list.setCurrentRow(current_row - 1)

    def move_down(self):
        """Move selected video down in the list."""
        current_row = self.file_list.currentRow()
        if current_row < 0 or current_row >= len(self.video_files) - 1:
            return

        # Swap in data list
        self.video_files[current_row], self.video_files[current_row + 1] = \
            self.video_files[current_row + 1], self.video_files[current_row]

        # Update list widget
        current_item = self.file_list.takeItem(current_row)
        self.file_list.insertItem(current_row + 1, current_item)
        self.file_list.setCurrentRow(current_row + 1)

    def browse_output(self):
        """Open file dialog to select output file path."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged Video As",
            "",
            "MP4 Files (*.mp4);;AVI Files (*.avi);;MOV Files (*.mov);;MKV Files (*.mkv)"
        )

        if file_path:
            self.output_path_edit.setText(file_path)

    def update_status(self):
        """Update the status label."""
        count = len(self.video_files)
        if count == 0:
            self.status_label.setText("Ready. Add videos to merge.")
        elif count == 1:
            self.status_label.setText("1 video added. Add more videos to merge.")
        else:
            self.status_label.setText(f"{count} videos ready to merge.")

    def get_resolution(self):
        """Get selected resolution option."""
        if self.radio_720p.isChecked():
            return "720p"
        elif self.radio_1080p.isChecked():
            return "1080p"
        else:
            return "original"

    def start_merge(self):
        """Start the merge process."""
        if self.merge_thread and self.merge_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Merge already in progress!")
            return

        if len(self.video_files) < 2:
            QMessageBox.warning(self, "Warning", "Please add at least 2 videos to merge.")
            return

        output_path = self.output_path_edit.text().strip()
        if not output_path:
            # Generate default output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                os.path.dirname(self.video_files[0]),
                f"merged_video_{timestamp}.mp4"
            )
            self.output_path_edit.setText(output_path)

        # Disable controls
        self.set_controls_enabled(False)

        # Create and start merge thread
        self.merge_thread = MergeThread(
            self.video_files.copy(),
            output_path,
            self.get_resolution()
        )
        self.merge_thread.progress.connect(self.on_progress)
        self.merge_thread.finished.connect(self.on_finished)
        self.merge_thread.start()

    def on_progress(self, percentage, message):
        """Handle progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)

    def on_finished(self, success, message):
        """Handle merge completion."""
        self.set_controls_enabled(True)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def set_controls_enabled(self, enabled):
        """Enable or disable controls."""
        self.add_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.up_btn.setEnabled(enabled)
        self.down_btn.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)
        self.merge_btn.setEnabled(enabled)

        for btn in self.resolution_group.buttons():
            btn.setEnabled(enabled)


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Video Merger")

    window = VideoMergerWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
