#dependencies: ffmpeg, requests

import os
import sys
import requests
import time
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():

	locale = 'en-us'
	localdir = os.path.dirname(__file__)

	#file we want to analyze
	sample_filepath = os.path.join(localdir, "samples/sample4.wav")
	sound_input = AudioSegment.from_wav(sample_filepath)
	print(sample_filepath)

	#folder/filename of split output
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	
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
		#[id, timestamp, speaker, confidence]
		section_result = []
		
		#id
		section_result.append(a)		
		#timestamp			
		section_result.append(timestamp_list[a])	

		if audiolength_list[a] < 1000:
			#speaker (?)
			section_result.append('?')		
			#confidence (?)
			section_result.append('?')		
			continue
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


	#speech to text
	


main()