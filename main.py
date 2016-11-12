#dependencies: ffmpeg, requests

import os
import requests
import msft_sr
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():
	localdir = os.path.dirname(__file__)
	sample_filepath = os.path.join(localdir, "samples/sample3.wav")
	print(sample_filepath)
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	sound_input = AudioSegment.from_wav(sample_filepath)

	sound_input.set_channels(1)				#Mono required
	sound_input.set_frame_rate(16000)		#16k required
	sound_input.set_sample_width(2)			#16bit required
	silence_tstamps = detect_silence(sound_input,
		min_silence_len = 300,
		silence_thresh = -40
	)

	if silence_tstamps[0][0] != 0:
		silence_tstamps.insert(0,[0,0])

	splitaudio = split_on_silence(sound_input,
		min_silence_len = 300,
		silence_thresh = -40,
		keep_silence = 200
	)

	section_count = 0
	section_list = []
	timestamp_list = []
	audiolength_list = []
	for i, section in enumerate(splitaudio):
		if(len(section) < 1000):
			section = section + AudioSegment.silent(duration = (1000 - len(section)))
		section.export(sections_filepath.format(i), format="wav", bitrate="16k")
		section_count = i
		section_list.append(sections_filepath.format(i))
		timestamp_list.append(silence_tstamps[i][1])
		audiolength_list.append(len(section))

	print(timestamp_list)
	print(audiolength_list)
	print(str(section_count) + " sections identified")


main()