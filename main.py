#dependencies: ffmpeg, requests

import os
import requests
from pydub import AudioSegment
from pydub.silence import split_on_silence

def main():
	localdir = os.path.dirname(__file__)
	sample_filename = os.path.join(localdir, "samples/sample1.wav")
	print(sample_filename)
	sectionsoutput = os.path.join(localdir, "sections/section{0}.wav")
	sound_input = AudioSegment.from_wav(sample_filename)

	splitaudio = split_on_silence(sound_input,
		min_silence_len = 500,
		silence_thresh = -40,
		keep_silence = 200
	)

	section_count = 0
	for i, section in enumerate(splitaudio):
		section.export(sectionsoutput.format(i), format="wav")
		section_count = i

	print(section_count)
main()