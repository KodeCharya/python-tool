import streamlit as st
import yt_dlp
from pathlib import Path
import tempfile
import os

# Function to get video details and available formats
def get_video_info(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

# Function to download the video
def download_video(url, quality):
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': quality,
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return temp_dir

# Streamlit UI
st.title("YouTube Video Downloader")

# Input for YouTube URL
url = st.text_input("Enter YouTube URL:")

if url:
    video_info = get_video_info(url)
    
    # Display video thumbnail
    st.image(video_info['thumbnail'], caption="Video Thumbnail", use_column_width=True)
    
    # Dropdown for video quality
    format_options = {
        f"{f.get('format_note', 'Unknown')} ({f.get('ext', 'unknown')})": f['format_id']
        for f in video_info['formats']
    }
    selected_quality = st.selectbox("Select Quality:", list(format_options.keys()))
    
    # Button to start download
    if st.button("Download"):
        with st.spinner('Downloading...'):
            download_path = download_video(url, format_options[selected_quality])
            video_file = next(Path(download_path).iterdir())
            st.success("Download completed!")
            st.markdown(f"[Download {video_file.name}](/{video_file.name})", unsafe_allow_html=True)
            st.write("If the download doesn't start, please use the link below:")
            st.download_button(label="Download Video", data=open(video_file, "rb"), file_name=video_file.name, mime="video/mp4")
