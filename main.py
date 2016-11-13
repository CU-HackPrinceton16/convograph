#dependencies: ffmpeg, requests, monotonic

import os
import sys
import requests
import time
from bing_voice import *
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():

	locale = 'en-us'
	localdir = os.path.dirname(__file__)


	##################
	# INPUT ANALYSIS #
	##################


	#file we want to analyze
	sample_filepath = os.path.join(localdir, "samples/sample4.wav")
	sound_input = AudioSegment.from_wav(sample_filepath)
	print(sample_filepath)

	#folder/filename of split output
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	tts_filepath = os.path.join(localdir, "tts/section{0}.wav")
	
	#identified speakers in sample
	speakers = {
		'Hillary':'000',
		'Zach':'000'
	}

	#Zach learning sample processing
	zach_filepath = os.path.join(localdir, "samples/zachsample4.wav")
	zach_outfile = os.path.join(localdir, "samples/zachpost.wav")
	zach_input = AudioSegment.from_wav(zach_filepath)
	zach_input = zach_input.split_to_mono()[0]
	zach_input = zach_input.set_frame_rate(16000)
	zach_input.export(zach_outfile, format="wav")

	#Hillary learning sample processing
	hillary_filepath = os.path.join(localdir, "samples/hillarysample1.wav")
	hillary_outfile = os.path.join(localdir, "samples/hillarypost.wav")
	hillary_input = AudioSegment.from_wav(hillary_filepath)
	hillary_input = hillary_input.split_to_mono()[0]
	hillary_input = hillary_input.set_frame_rate(16000)
	hillary_input.export(hillary_outfile, format="wav")

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

	######################
	# SENTIMENT ANALYSIS #
	######################
	
	#SDK for speaker identifier API
	speakerhelper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(SPEAKER_KEY)

	#create a profile for the number of speakers
	for k in range(0,len(speakers)):
		creation_resp = speakerhelper.create_profile(locale)
		profile_id = creation_resp.get_profile_id()
		id_list.append(profile_id)
		time.sleep(3)

	#relate Hillary to ID
	speakers[id_list[0]] = 'Hillary'
	speakers['Hillary'] = id_list[0]
	print(id_list[0])

	#relate Zach to ID
	speakers[id_list[1]] = 'Zach'
	speakers['Zach'] = id_list[1]
	print(id_list[1])

	#training (response only for debugging, no use)
	e_resps = []

	e_resps.append(speakerhelper.enroll_profile(id_list[0], hillary_outfile))
	print('H Total Time = {0}'.format(e_resps[0].get_total_speech_time()))
	print('H Remaining Time = {0}'.format(e_resps[0].get_remaining_speech_time()))
	print('H Speech Time = {0}'.format(e_resps[0].get_speech_time()))
	print('H Enrollment Status = {0}'.format(e_resps[0].get_enrollment_status()))

	e_resps.append(speakerhelper.enroll_profile(id_list[1], zach_outfile))
	print('Z Total Time = {0}'.format(e_resps[1].get_total_speech_time()))
	print('Z Remaining Time = {0}'.format(e_resps[1].get_remaining_speech_time()))
	print('Z Speech Time = {0}'.format(e_resps[1].get_speech_time()))
	print('Z Enrollment Status = {0}'.format(e_resps[1].get_enrollment_status()))


	speech_result = []

	#identify files
	for a in range(0, section_count + 1):
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

	print(speech_result)

	speakerhelper.delete_profile(id_list[0])
	speakerhelper.delete_profile(id_list[1])


	###################
	# CONSECUTIVENESS #
	###################

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


	##################
	# TEXT TO SPEECH #
	##################

	bingbing = bing_voice.BingVoice(BING_SPEECH_KEY)

	for d in range(0, len(tts_list)):
		curr_tts_path = tts_filepath.format(d)
		recognized_string = recognize(open(curr_tts_path,'rb'))
		print()


			

main()