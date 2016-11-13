import os
import sys
import requests
import time
import bing_voice
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():
	localdir = os.path.dirname(__file__)
	tts_list = [[0, 0, 9323, 'Zach'], [1, 9702, 2061, 'Hillary'], [2, 12008, 2006, 'Zach'], [3, 14252, 4844, 'Hillary'], [4, 19728, 1044, '?'], [5, 20858, 7376, 'Hillary'], [6, 28680, 780, '?'], [7, 29382, 1237, 'Hillary'], [8, 30585, 971, '?'], [9, 32066, 8350, 'Zach'], [10, 41242, 659, '?'], [11, 41869, 7449, 'Zach'], [12, 51762, 1504, '?'], [13, 54382, 2400, 'Hillary'], [14, 56764, 1424, '?'], [15, 58250, 3712, 'Hillary'], [16, 62045, 3035, 'Zach'], [17, 65406, 2090, 'Hillary'], [18, 67705, 8190, 'Zach'], [19, 76444, 1727, '?'], [20, 78798, 2379, 'Hillary']]
	
	bingbing = bing_voice.BingVoice(BING_SPEECH_KEY)
	tts_filepath = os.path.join(localdir, "tts/section{0}.wav")

	for d in range(0, len(tts_list)):
		try:
			curr_tts_path = tts_filepath.format(d)
			with open(curr_tts_path,'rb') as body:
				recognized_string = bingbing.recognize(body, language='en-US')

			print(recognized_string)
		except bing_voice.UnknownValueError:
			print("Unintelligible")
		except bing_voice.RequestError as e:
			print("Error: {0}".format(e))
main()