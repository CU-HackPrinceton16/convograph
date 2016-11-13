
import os
import sys
import requests
import time
from bing_voice import *
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

#GCP
import argparse
import base64
import json
from transcribe import get_speech_service
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials


def main():
	tts_list = [[0, 0, 9323, 'Zach', 'thank you very much mrs. Quinn for being here critics have questioned some of your decision-making recently and by you doing this show I hope it finally plays that to rest I think'], [1, 9702, 2061, 'Hillary', "it actually proves our case don't you"], [2, 12008, 2006, 'Zach', 'are you excited to be the first girl president'], [3, 14252, 4844, 'Hillary', 'why me being present it would be such an extraordinary honor and responsibility'], [4, 19728, 1044, '?', "I'm fat"], [5, 20858, 7376, 'Hillary', "being the first woman elected president and what that would mean for a country and what really what that would mean for I don't know just little girls little boys 2"], [6, 28680, 780, '?', '?'], [7, 29382, 1237, 'Hillary', "that's pretty special"], [8, 30585, 971, '?', '?'], [9, 32066, 8350, 'Zach', 'not to take away from the historic significance of you props becoming the first female president but for a younger younger generation you will also become'], [10, 41242, 659, '?', 'they are'], [11, 41869, 7449, 'Zach', "first White president and that's pretty neat to his secretary how many words per minute could you type and how does President Obama I like his coffee"], [12, 51762, 1504, '?', 'like himself'], [13, 54382, 2400, 'Hillary', 'you know that those are really'], [14, 56764, 1424, '?', 'out of date questions'], [15, 58250, 3712, 'Hillary', 'you need to get out more what happens if you become pregnant'], [16, 62045, 3035, 'Zach', 'are we going to be stuck with Tim Kaine for 9 months how does this work'], [17, 65406, 2090, 'Hillary', 'I could send you some pamphlets'], [18, 67705, 8190, 'Zach', "it might help you understand first you supported Obama's trans-pacific partnership deal and then you are against it I think the people deserve to know"], [19, 76444, 1727, '?', 'are you down with TPP'], [20, 78798, 2379, 'Hillary', "I'm not down with TPP"]]


	for e in range(0, len(tts_list)):
		curr_transcript = tts_list[e][4]
		json_dict = {}
		json_dict["documents"] = [{"language": "en","id": str(e), "text": curr_transcript}]
		json_output = json.dumps(json_dict)
		
		sentiment_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
		try:
			print(json_output)
			sentiment_request = requests.post(sentiment_url, json_output, headers ={
				'Content-type': 'application/json',
				"Ocp-Apim-Subscription-Key": SENTIMENT_KEY
			})
			response_text = sentiment_request.json()
			print(response_text)
			sentiment_val = response_text["documents"][0]["score"]
			tts_list[e].append(sentiment_val)
		except HTTPError as e:
			raise RequestError("recognition request failed: {0}".format(
				getattr(e, "reason", "status {0}".format(e.code))))  # use getattr to be compatible with Python 2.6
		except URLError as e:
			raise RequestError("recognition connection failed: {0}".format(e.reason))

	print(tts_list)

main()