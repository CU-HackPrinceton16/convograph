#dependencies: ffmpeg, requests, monotonic

import os, os.path
import sys
import requests
import time
from bing_voice import *
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
import requests
from pprint import pprint

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

	locale = 'en-us'
	localdir = os.path.dirname(__file__)


	##################
	# INPUT ANALYSIS #
	##################

	print("reading sample...")
	#file we want to analyze
	sample_filepath = os.path.join(localdir, "samples/sample1.wav")
	sound_input = AudioSegment.from_wav(sample_filepath)

	#folder/filename of split output
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	tts_filepath = os.path.join(localdir, "tts/section{0}.wav")
	
	#identified speakers in sample
	speakers = {}

	#count number of speakers
	DIR = os.path.join(localdir, "speaker_samples/")
	number_of_speakers = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) if not name.startswith(".")])
	print('{0} speakers identified'.format(number_of_speakers))

	print("reading learning material...")
	for aa in range(0, number_of_speakers):
		curr_speaker_filepath = os.path.join(localdir, "speaker_samples/speaker{0}.wav".format(aa))
		curr_speaker_outfile = os.path.join(localdir, "speaker_post/post{0}.wav".format(aa))
		curr_speaker_input = AudioSegment.from_wav(curr_speaker_filepath)
		curr_speaker_input = curr_speaker_input.split_to_mono()[0]
		curr_speaker_input = curr_speaker_input.set_frame_rate(16000)
		curr_speaker_input.export(curr_speaker_outfile, format="wav")
		speakers[str(aa)] = '000'
	
	# #Zach learning sample processing
	# zach_filepath = os.path.join(localdir, "samples/zachsample4.wav")
	# zach_outfile = os.path.join(localdir, "samples/zachpost.wav")
	# zach_input = AudioSegment.from_wav(zach_filepath)
	# zach_input = zach_input.split_to_mono()[0]
	# zach_input = zach_input.set_frame_rate(16000)
	# zach_input.export(zach_outfile, format="wav")

	# #Hillary learning sample processing
	# hillary_filepath = os.path.join(localdir, "samples/hillarysample1.wav")
	# hillary_outfile = os.path.join(localdir, "samples/hillarypost.wav")
	# hillary_input = AudioSegment.from_wav(hillary_filepath)
	# hillary_input = hillary_input.split_to_mono()[0]
	# hillary_input = hillary_input.set_frame_rate(16000)
	# hillary_input.export(hillary_outfile, format="wav")

	print("analyzing silences...")
	#generate timestamps of silent sections
	silence_tstamps = detect_silence(sound_input,
		min_silence_len = 300,
		silence_thresh = -40
	)

	if silence_tstamps[0][0] != 0:
		silence_tstamps.insert(0,[0,0])

	#list of split sections
	splitaudio = split_on_silence(sound_input,
		min_silence_len = 300,
		silence_thresh = -40,
		keep_silence = 200
	)

	section_count = 0		#number of generated sections
	section_list = []		#list of section filepaths
	timestamp_list = []		#list of silence timestamps
	audiolength_list = []	#list of audio lengths

	print("splitting audio...")
	#for each audio clip
	for i, section in enumerate(splitaudio):
		#meet MSFT's requirements
		section = section.split_to_mono()[0]
		section = section.set_frame_rate(16000)

		#export as wav
		section.export(sections_filepath.format(i), format="wav")

		#update no of sections
		section_count = i

		#store clip data
		section_list.append(sections_filepath.format(i))
		timestamp_list.append(silence_tstamps[i][1])
		audiolength_list.append(len(section))

	print(str(section_count) + " sections identified")

	id_list = []

	#scale this later
	#lol jk copy and paste

	####################
	# SPEAKER ANALYSIS #
	####################
	
	#SDK for speaker identifier API
	speakerhelper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(SPEAKER_KEY)

	#create a profile for the number of speakers
	print("training speakers...")
	for k in range(0,number_of_speakers):
		creation_resp = speakerhelper.create_profile(locale)
		profile_id = creation_resp.get_profile_id()
		id_list.append(profile_id)
		speakers[id_list[k]] = str(k)
		speakers[str(k)] = id_list[k]
		print("created speaker {0}".format(str(k)))
		enroll_response = speakerhelper.enroll_profile(id_list[k], os.path.join(localdir, "speaker_post/post{0}.wav".format(k)))
		print('H Total Time = {0}'.format(enroll_response.get_total_speech_time()))
		print('H Remaining Time = {0}'.format(enroll_response.get_remaining_speech_time()))
		print('H Speech Time = {0}'.format(enroll_response.get_speech_time()))
		print('H Enrollment Status = {0}'.format(enroll_response.get_enrollment_status()))

		if(str(enroll_response.get_remaining_speech_time()) == "0.0"):
			print("successfully enrolled speaker {0}".format(str(k)))
		else:
			print("unsuccessfully enrolled speaker {0}".format(str(k)))
			raise RuntimeError("lolfuck")
		

	# #relate Hillary to ID
	# speakers[id_list[0]] = 'Hillary'
	# speakers['Hillary'] = id_list[0]
	# print(id_list[0])

	# #relate Zach to ID
	# speakers[id_list[1]] = 'Zach'
	# speakers['Zach'] = id_list[1]
	# print(id_list[1])

	#training (response only for debugging, no use)
	# e_resps = []

	# e_resps.append(speakerhelper.enroll_profile(id_list[0], hillary_outfile))
	#print('H Total Time = {0}'.format(e_resps[0].get_total_speech_time()))
	#print('H Remaining Time = {0}'.format(e_resps[0].get_remaining_speech_time()))
	#print('H Speech Time = {0}'.format(e_resps[0].get_speech_time()))
	#print('H Enrollment Status = {0}'.format(e_resps[0].get_enrollment_status()))

	# e_resps.append(speakerhelper.enroll_profile(id_list[1], zach_outfile))
	# print('Z Total Time = {0}'.format(e_resps[1].get_total_speech_time()))
	# print('Z Remaining Time = {0}'.format(e_resps[1].get_remaining_speech_time()))
	# print('Z Speech Time = {0}'.format(e_resps[1].get_speech_time()))
	# print('Z Enrollment Status = {0}'.format(e_resps[1].get_enrollment_status()))

	speech_result = []
	print("identifying speaker...")
	#identify files
	for a in range(0, section_count + 1):
		print("si: {0}/{1}".format(str(a), str(section_count)))
		#[id, timestamp, length, speaker, confidence]
		section_result = []
		
		#id
		section_result.append(a)		
		#timestamp			
		section_result.append(timestamp_list[a])
		#length
		section_result.append(audiolength_list[a])

		if audiolength_list[a] < 1000:
			#speaker (?)
			section_result.append('?')		
			#confidence (?)
			section_result.append('?')		
		else:
			identification_response = speakerhelper.identify_file(sections_filepath.format(a), id_list, force_short_audio = True)
		
			if(str(identification_response.get_identified_profile_id()) != '00000000-0000-0000-0000-000000000000'):
				speaker_result = str(identification_response.get_identified_profile_id())
				#speaker
				section_result.append(speakers[speaker_result])		
			else:
				#speaker (?)
				section_result.append('?')							

			section_result.append(identification_response.get_confidence()) #confidence

		#add to overall list
		speech_result.append(section_result)

	#print(speech_result)

	speakerhelper.delete_profile(id_list[0])
	speakerhelper.delete_profile(id_list[1])


	###################
	# CONSECUTIVENESS #
	###################

	print("preparing clips for convo detection...")
	buffer_section = AudioSegment.empty()
	buffer_section = buffer_section.split_to_mono()[0]
	buffer_section = buffer_section.set_frame_rate(16000)
	#[[id, timestamp, length, speaker]]
	consec_list = []
	consec_time = 0
	tts_counter = 0
	tts_list = []

	#it works I swear
	for b in range(0, section_count + 1):
		#print(b)
		#print(consec_list)
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
	#print(tts_list)


	##################
	# TEXT TO SPEECH #
	##################

	print("text to speech...")

	#this is google.
	service = get_speech_service()

	for d in range(0, len(tts_list)):
		print("tts: {0}/{1}".format(str(d), str(len(tts_list)-1)))
		#google API limit
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
		#print(json.dumps(response))

		if(response != {}):
			text = response["results"][0]["alternatives"][0]["transcript"]
			tts_list[d].append(text)
		else:
			tts_list[d].append("?")
		
	#[[id, timestamp, length, speaker, text]]
	#print(tts_list)

	######################
	# SENTIMENT ANALYSIS #
	######################

	print("sentiment analysis...")

	for e in range(0, len(tts_list)):
		curr_transcript = tts_list[e][4]
		json_dict = {}
		json_dict["documents"] = [{"language": "en","id": str(e), "text": curr_transcript}]
		json_output = json.dumps(json_dict)
		
		sentiment_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
		try:
			sentiment_request = requests.post(sentiment_url, json_output, headers ={
				'Content-type': 'application/json',
				"Ocp-Apim-Subscription-Key": SENTIMENT_KEY
			})
			response_text = sentiment_request.json()
			sentiment_val = response_text["documents"][0]["score"]
			tts_list[e].append(sentiment_val)
		except HTTPError as e:
			raise RequestError("recognition request failed: {0}".format(
				getattr(e, "reason", "status {0}".format(e.code))))  # use getattr to be compatible with Python 2.6
		except URLError as e:
			raise RequestError("recognition connection failed: {0}".format(e.reason))

	#[id, timestamp, duration, speaker, text, sentiment]
	pprint(tts_list)

	edges = transcript_to_edge(tts_list)
	pprint(edges)
	nodes = transcript_to_node(tts_list)
	pprint(nodes)

def transcript_to_node(transcript):
	node_dict = {}
	node_timedlist = []
	for i in range(len(transcript)):
		curr_speaker = transcript[i][3]
		if curr_speaker == "?": continue

		if curr_speaker in node_dict:
			node_dict[curr_speaker]["count"] = node_dict[curr_speaker]["count"] + 1
			node_dict[curr_speaker]["total"] = node_dict[curr_speaker]["total"] + transcript[i][5]
		else: 
			node_dict[curr_speaker] = {"count": 1, "total": transcript[i][5]}

		node_list = []
		node_list.append(transcript[i][1])
		for speaker in node_dict:
			node_list.append([speaker, float(node_dict[speaker]["total"]) / float(node_dict[speaker]["count"])])
		node_timedlist.append(node_list)
	return node_timedlist 


#Written by Jimmy
def transcript_to_edge(transcript):    
	''' input is conversation json, output is list of source/target/sentiment averages'''

	speaker1 = None
	speaker2 = None
	speaker3 = None

	pairs = [] # [[speaker1, speaker2], [val1, val2, val3, ...]]
	timedgraph = []
	for i in range(len(transcript) - 2):
		speaker1 = transcript[i]
		speaker2 = transcript[i + 1]
		speaker3 = transcript[i + 2]

		if speaker1[3] == "?" or speaker2[3] == "?" or speaker3[3] == "?": continue

		# [3] --> speaker name
		if (speaker1[3] == speaker3[3]):
			average = (float(speaker1[5]) + float(speaker2[5]) + float(speaker3[5])) / 3.0

			found = False
			for pair in pairs:
				if speaker1[3] in pair[0] and speaker2[3] in pair[0]:
					pair[1].append(average)
					found = True
			
			if not found:
				pairs.append([[speaker1[3], speaker2[3]], [average]])

		for pair in pairs:
			timedgraph.append([speaker3[1],[pair[0][0], pair[0][1], (sum(pair[1]) / float(len(pair[1]))) / 10.0]])
	return timedgraph


main()