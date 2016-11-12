#dependencies: ffmpeg, requests

import os
import requests
import msft_sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

def main():
	localdir = os.path.dirname(__file__)
	sample_filename = os.path.join(localdir, "samples/sample2.wav")
	print(sample_filename)
	sections_filename = os.path.join(localdir, "sections/section{0}.wav")
	sound_input = AudioSegment.from_wav(sample_filename)

	sound_input.set_channels(1)				#Mono required
	sound_input.set_frame_rate(16000)		#16k required
	sound_input.set_sample_width(2)			#16bit required
	splitaudio = split_on_silence(sound_input,
		min_silence_len = 300,
		silence_thresh = -40,
		keep_silence = 200
	)

	section_count = 0
	for i, section in enumerate(splitaudio):
		section.export(sections_filename.format(i), format="wav", bitrate="16k")
		section_count = i

	print(str(section_count) + " sections identified")

	#scale this later

	section_file = AudioSegment.from_wav(sections_filename.format(1))


main()