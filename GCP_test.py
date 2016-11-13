import os
import sys
import requests
import time

import argparse
import base64
import json
from transcribe import get_speech_service
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials

from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():
	localdir = os.path.dirname(__file__)

	tts_list = [[0, 0, 9323, 'Zach'], [1, 9702, 2061, 'Hillary'], [2, 12008, 2006, 'Zach'], [3, 14252, 4844, 'Hillary'], [4, 19728, 1044, '?'], [5, 20858, 7376, 'Hillary'], [6, 28680, 780, '?'], [7, 29382, 1237, 'Hillary'], [8, 30585, 971, '?'], [9, 32066, 8350, 'Zach'], [10, 41242, 659, '?'], [11, 41869, 7449, 'Zach'], [12, 51762, 1504, '?'], [13, 54382, 2400, 'Hillary'], [14, 56764, 1424, '?'], [15, 58250, 3712, 'Hillary'], [16, 62045, 3035, 'Zach'], [17, 65406, 2090, 'Hillary'], [18, 67705, 8190, 'Zach'], [19, 76444, 1727, '?'], [20, 78798, 2379, 'Hillary']]
	
	service = get_speech_service()
	tts_filepath = os.path.join(localdir, "tts/section{0}.wav")

	for d in range(0, len(tts_list)):
		time.sleep(1)
		curr_tts_path = tts_filepath.format(d)

		with open(curr_tts_path,'rb') as speech:
			speech_content = base64.b64encode(speech.read())

		service_request = service.speech().syncrecognize(
			body={
				'config': {
					# There are a bunch of config options you can specify. See
					# https://goo.gl/KPZn97 for the full list.
					'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
					'sampleRate': 16000,  # 16 khz
					# See http://g.co/cloud/speech/docs/languages for a list of
					# supported languages.
					'languageCode': 'en-US',  # a BCP-47 language tag
				},
				'audio': {
					'content': speech_content.decode('UTF-8')
				}
			})
		response = service_request.execute()
		print(json.dumps(response))

		if(response != {}):
			text = response["results"][0]["alternatives"][0]["transcript"]
			tts_list[d].append(text)
		else:
			tts_list[d].append("?")
		

	print(tts_list)


main()