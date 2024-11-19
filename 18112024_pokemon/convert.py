# helper for converting .mov to .mp4
from moviepy.editor import VideoFileClip

input_file = "quick.mov"
output_file = "quick.mp4"

# Load the .mov file and write it as .mp4
clip = VideoFileClip(input_file)
clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

print("Conversion complete!")