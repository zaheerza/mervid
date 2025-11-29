#!/usr/bin/env python3
"""
Video Merger Application (Streamlit Web Version)
A web-based GUI application to merge multiple video clips into one video file.
Supports MP4, AVI, MOV, MKV, WMV, FLV, and WebM formats.

Run with: streamlit run video_merger_streamlit.py
"""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import streamlit as st

# Video processing imports - handle both moviepy 1.x and 2.x
try:
    from moviepy import VideoFileClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips
    except ImportError:
        st.error("Error: moviepy is not installed. Please run: pip install moviepy")
        st.stop()


def resize_clip(clip, **kwargs):
    """Resize clip - compatible with both moviepy 1.x and 2.x."""
    # Try new API first (moviepy 2.0+)
    if hasattr(clip, 'resized'):
        return clip.resized(**kwargs)
    # Fall back to old API (moviepy 1.x)
    elif hasattr(clip, 'resize'):
        return clip.resize(**kwargs)
    else:
        raise AttributeError("VideoFileClip has no resize method")


def merge_videos(video_files, resolution, progress_callback=None):
    """
    Merge multiple video files into one.

    Args:
        video_files: List of file paths or file objects
        resolution: One of 'original', '720p', '1080p'
        progress_callback: Optional callback function for progress updates

    Returns:
        Path to merged video file
    """
    clips = []
    temp_files = []

    try:
        total_files = len(video_files)

        # Save uploaded files to temp directory
        for i, uploaded_file in enumerate(video_files):
            if progress_callback:
                progress_callback(
                    int((i / total_files) * 30),
                    f"Saving video {i+1}/{total_files}..."
                )

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_file.write(uploaded_file.read())
            temp_file.close()
            temp_files.append(temp_file.name)

        # Load all video clips
        for i, video_path in enumerate(temp_files):
            if progress_callback:
                progress_callback(
                    30 + int((i / total_files) * 30),
                    f"Loading video {i+1}/{total_files}..."
                )

            clip = VideoFileClip(video_path)

            # Resize if needed
            if resolution == "720p":
                clip = resize_clip(clip, height=720)
            elif resolution == "1080p":
                clip = resize_clip(clip, height=1080)
            elif resolution == "original" and i > 0 and clips:
                # Resize to match first video's dimensions
                target_size = clips[0].size
                clip = resize_clip(clip, newsize=target_size)

            clips.append(clip)

        if progress_callback:
            progress_callback(60, "Concatenating videos...")

        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose")

        if progress_callback:
            progress_callback(70, "Writing output file...")

        # Create output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.mp4',
            prefix=f'merged_{timestamp}_'
        ).name

        # Write the output file
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger=None,
            threads=4
        )

        if progress_callback:
            progress_callback(100, "Done!")

        # Cleanup
        final_clip.close()
        for clip in clips:
            clip.close()

        # Clean up temp input files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

        return output_path

    except Exception as e:
        # Cleanup on error
        for clip in clips:
            try:
                clip.close()
            except:
                pass

        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

        raise e


def main():
    """Main Streamlit app."""

    # Page config
    st.set_page_config(
        page_title="Video Merger",
        page_icon="🎬",
        layout="centered"
    )

    # Title
    st.title("🎬 Video Merger")
    st.markdown("Merge multiple video clips into one video file")

    # Sidebar info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        **Video Merger** allows you to:
        - Upload multiple video files
        - Choose output resolution
        - Merge them into one video

        **Supported Formats:**
        - MP4, AVI, MOV, MKV
        - WMV, FLV, WebM, MPEG

        **Resolution Options:**
        - Original (from first video)
        - 720p
        - 1080p
        """)

        st.header("🚀 How to Use")
        st.markdown("""
        1. Upload 2 or more videos
        2. Select resolution
        3. Click "Merge Videos"
        4. Download merged video
        """)

    # File uploader
    st.header("1. Upload Videos")
    uploaded_files = st.file_uploader(
        "Choose video files to merge",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg', 'm4v'],
        accept_multiple_files=True,
        help="Upload 2 or more video files. Videos will be merged in the order uploaded."
    )

    # Show uploaded files
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} video(s) uploaded")

        with st.expander("View uploaded files"):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.getvalue()) / (1024 * 1024)  # Convert to MB
                st.write(f"{i}. **{file.name}** ({file_size:.2f} MB)")

        # Reorder controls
        st.info("💡 **Tip:** To reorder videos, re-upload them in the desired order.")

    # Resolution selection
    st.header("2. Select Resolution")
    resolution = st.radio(
        "Output resolution:",
        options=['original', '720p', '1080p'],
        format_func=lambda x: {
            'original': 'Original (from first video)',
            '720p': '720p (1280x720)',
            '1080p': '1080p (1920x1080)'
        }[x],
        horizontal=True
    )

    # Merge button
    st.header("3. Merge Videos")

    if len(uploaded_files) < 2:
        st.warning("⚠️ Please upload at least 2 videos to merge.")
        merge_disabled = True
    else:
        merge_disabled = False

    if st.button("🎬 Merge Videos", disabled=merge_disabled, type="primary", use_container_width=True):
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(percentage, message):
            progress_bar.progress(percentage / 100)
            status_text.text(message)

        try:
            # Reset file pointers
            for f in uploaded_files:
                f.seek(0)

            # Merge videos
            with st.spinner("Merging videos..."):
                output_path = merge_videos(
                    uploaded_files,
                    resolution,
                    progress_callback=update_progress
                )

            st.success("✅ Videos merged successfully!")

            # Download button
            st.header("4. Download")

            with open(output_path, 'rb') as f:
                merged_video = f.read()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"merged_video_{timestamp}.mp4"

            st.download_button(
                label="⬇️ Download Merged Video",
                data=merged_video,
                file_name=download_filename,
                mime="video/mp4",
                use_container_width=True
            )

            # Video preview
            with st.expander("🎥 Preview merged video"):
                st.video(merged_video)

            # Cleanup
            try:
                os.unlink(output_path)
            except:
                pass

        except Exception as e:
            st.error(f"❌ Error merging videos: {str(e)}")
            st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Made with ❤️ using Streamlit and MoviePy"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
