import os
import tkinter as tk
from tkinter import filedialog
import vlc

def format_time(ms):
    hours = ms // (1000 * 60 * 60)
    ms %= (1000 * 60 * 60)
    minutes = ms // (1000 * 60)
    ms %= (1000 * 60)
    seconds = ms // 1000
    milliseconds = ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

class MediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music and Video Player")
        self.root.geometry("800x500")

        # VLC player instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Video frame
        self.video_frame = tk.Frame(root, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.player.set_hwnd(self.canvas.winfo_id())

        # Control bar
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.open_button = tk.Button(self.controls_frame, text="Open File", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.play_button = tk.Button(self.controls_frame, text="Play", command=self.play)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = tk.Button(self.controls_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = tk.Button(self.controls_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.backward_button = tk.Button(self.controls_frame, text="<<", command=self.backward)
        self.backward_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.forward_button = tk.Button(self.controls_frame, text=">>", command=self.forward)
        self.forward_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.time_label = tk.Label(self.controls_frame, text="00:00:00.000 / 00:00:00.000")
        self.time_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.time_slider = tk.Scale(self.controls_frame, from_=0, to=1000, orient=tk.HORIZONTAL, length=400, command=self.set_time)
        self.time_slider.pack(side=tk.LEFT, padx=5, pady=5)

        self.volume_slider = tk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume")
        self.volume_slider.set(50)  # Default volume
        self.volume_slider.pack(side=tk.RIGHT, padx=5, pady=5)
        self.volume_slider.bind("<Motion>", self.set_volume)

        # Update time slider periodically
        self.update_time_slider()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Media Files", "*.mp3 *.mp4 *.avi *.mkv *.wav"), ("All Files", "*.*")]
        )
        if file_path:
            self.media = self.instance.media_new(file_path)
            self.player.set_media(self.media)
            self.player.set_hwnd(self.canvas.winfo_id())
            # Reset time slider range to match new media duration
            self.root.after(100, self.update_time_slider)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
        self.time_slider.set(0)
        self.time_label.config(text="00:00:00.000 / 00:00:00.000")

    def forward(self):
        current_time = self.player.get_time()
        self.player.set_time(current_time + 10000)  # Forward 10 seconds

    def backward(self):
        current_time = self.player.get_time()
        self.player.set_time(current_time - 10000)  # Backward 10 seconds

    def set_volume(self, event):
        volume = self.volume_slider.get()
        self.player.audio_set_volume(volume)

    def set_time(self, value):
        self.player.set_time(int(value))

    def update_time_slider(self):
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            # Update the time slider to the current time
            current_time = self.player.get_time()
            duration = self.player.get_length()
            if duration > 0:
                self.time_slider.configure(to=duration)
                self.time_slider.set(current_time)
                # Update time label with formatted current time and total duration
                self.time_label.config(text=f"{format_time(current_time)} / {format_time(duration)}")
        self.root.after(500, self.update_time_slider)

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaPlayer(root)
    root.mainloop()
