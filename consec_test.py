	#speech to text
import os
import sys
import requests
import time
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():
	localdir = os.path.dirname(__file__)
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	tts_filepath = os.path.join(localdir, "tts/section{0}.wav")


	section_count = 32

	speech_result = [[0, 0, 4972, 'Zach', 'High'], [1, 5378, 4351, 'Zach', 'High'], [2, 9702, 2061, 'Hillary', 'High'], [3, 12008, 2006, 'Zach', 'High'], [4, 14252, 1108, 'Hillary', 'Normal'], [5, 15714, 3736, 'Hillary', 'High'], [6, 19728, 1044, '?', 'Normal'], [7, 20858, 5236, 'Hillary', 'High'], [8, 26514, 2140, 'Hillary', 'High'], [9, 28680, 780, '?', '?'], [10, 29382, 1237, 'Hillary', 'Normal'], [11, 30585, 568, '?', '?'], [12, 31698, 403, '?', '?'], [13, 32066, 2790, 'Zach', 'High'], [14, 35058, 2244, 'Zach', 'High'], [15, 37464, 3316, 'Zach', 'High'], [16, 41242, 659, '?', '?'], [17, 41869, 1427, 'Zach', 'Normal'], [18, 43535, 1575, 'Zach', 'High'], [19, 46640, 2287, 'Zach', 'High'], [20, 49607, 2160, 'Zach', 'High'], [21, 51762, 946, '?', '?'], [22, 53739, 558, '?', '?'], [23, 54382, 2400, 'Hillary', 'High'], [24, 56764, 1424, '?', 'High'], [25, 58250, 3712, 'Hillary', 'High'], [26, 62045, 3035, 'Zach', 'High'], [27, 65406, 2090, 'Hillary', 'High'], [28, 67705, 4756, 'Zach', 'High'], [29, 72532, 1384, 'Zach', 'Normal'], [30, 74062, 2050, 'Zach', 'High'], [31, 76444, 1727, '?', 'Normal'], [32, 78798, 2379, 'Hillary', 'High']]

	buffer_section = AudioSegment.empty()
	buffer_section = buffer_section.split_to_mono()[0]
	buffer_section = buffer_section.set_frame_rate(16000)
	#[[id, timestamp, length, speaker, confidence]]
	consec_list = []
	consec_time = 0
	tts_counter = 0
	tts_list = []
	for b in range(0, section_count + 1):
		print(b)
		print(consec_list)
		if b == section_count:
			if len(consec_list) == 0:
				curr_section = AudioSegment.from_wav(sections_filepath.format(b))
				curr_section = curr_section.split_to_mono()[0]
				curr_section = curr_section.set_frame_rate(16000)
				curr_section.export(tts_filepath.format(tts_counter), format="wav")
				tts_list.append([tts_counter, speech_result[b][1], speech_result[b][2], speech_result[b][3]])
				tts_counter = tts_counter + 1
				consec_list = []
				consec_time = 0
			else:
				consec_list.append(speech_result[b])
				consec_time = consec_time + speech_result[b][2]
				for c in range(0, len(consec_list)):
					curr_section = AudioSegment.from_wav(sections_filepath.format(consec_list[c][0]))
					curr_section = curr_section.split_to_mono()[0]
					curr_section = curr_section.set_frame_rate(16000)
					buffer_section = buffer_section + curr_section
				buffer_section.export(tts_filepath.format(tts_counter), format="wav")
				tts_list.append([tts_counter, consec_list[0][1], consec_time, consec_list[0][3]])
				buffer_section = AudioSegment.empty()
				tts_counter = tts_counter + 1
				consec_list = []
				consec_time = 0
		elif (speech_result[b][3] != speech_result[b+1][3]) or (consec_time + speech_result[b+1][2] >= 10000):
			#end of consecutiveness
			consec_list.append(speech_result[b])
			consec_time = consec_time + speech_result[b][2]
			for c in range(0, len(consec_list)):
				curr_section = AudioSegment.from_wav(sections_filepath.format(consec_list[c][0]))
				curr_section = curr_section.split_to_mono()[0]
				curr_section = curr_section.set_frame_rate(16000)
				buffer_section = buffer_section + curr_section
			buffer_section.export(tts_filepath.format(tts_counter), format="wav")
			tts_list.append([tts_counter, consec_list[0][1], consec_time, consec_list[0][3]])
			buffer_section = AudioSegment.empty()
			tts_counter = tts_counter + 1
			consec_list = []
			consec_time = 0
		elif speech_result[b][3] == speech_result[b+1][3]:
			#still consecutive
			consec_list.append(speech_result[b])
			consec_time = consec_time + speech_result[b][2]
	print(tts_list)

main()