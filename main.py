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
	sample_filepath = os.path.join(localdir, "samples/sample4.wav")
	print(sample_filepath)
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	sound_input = AudioSegment.from_wav(sample_filepath)

	speakers = {
		'Hillary':'000',
		'Zach':'000'
	}

	zach_filepath = os.path.join(localdir, "samples/zachsample4.wav")
	zach_outfile = os.path.join(localdir, "samples/zachpost.wav")
	zach_input = AudioSegment.from_wav(zach_filepath)
	zach_input = zach_input.split_to_mono()[0]
	zach_input = zach_input.set_frame_rate(16000)
	zach_input.export(zach_outfile, format="wav")

	hillary_filepath = os.path.join(localdir, "samples/hillarysample1.wav")
	hillary_outfile = os.path.join(localdir, "samples/hillarypost.wav")
	hillary_input = AudioSegment.from_wav(hillary_filepath)
	hillary_input = zach_input.split_to_mono()[0]
	hillary_input = zach_input.set_frame_rate(16000)
	hillary_input.export(hillary_outfile, format="wav")

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
		section = section.split_to_mono()[0]
		section = section.set_frame_rate(16000)
		#if(len(section) < 1000):
		#	section = section + AudioSegment.silent(duration = (1000 - len(section)))

		section.export(sections_filepath.format(i), format="wav")
		section_count = i
		section_list.append(sections_filepath.format(i))
		timestamp_list.append(silence_tstamps[i][1])
		audiolength_list.append(len(section))

	print(timestamp_list)
	print(audiolength_list)
	print(str(section_count) + " sections identified")

	id_list = []

	#scale this later
	

	speakerhelper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(SPEAKER_KEY)

	for k in range(0,len(speakers)):
		creation_resp = speakerhelper.create_profile(locale)
		profile_id = creation_resp.get_profile_id()
		id_list.append(profile_id)
		time.sleep(3)

	speakers[id_list[0]] = 'Hillary'
	speakers['Hillary'] = id_list[0]
	print(id_list[0])
	speakers[id_list[1]] = 'Zach'
	speakers['Zach'] = id_list[1]
	print(id_list[1])

	e_resps = []

	e_resps.append(speakerhelper.enroll_profile(id_list[0], hillary_outfile))
	print('H Total Time = {0}'.format(e_resps[0].get_total_speech_time()))
	print('H Remaining Time = {0}'.format(e_resps[0].get_remaining_speech_time()))
	print('H Speech Time = {0}'.format(e_resps[0].get_speech_time()))
	print('H Enrollment Status = {0}'.format(e_resps[0].get_enrollment_status()))

	time.sleep(3)

	e_resps.append(speakerhelper.enroll_profile(id_list[1], zach_outfile))
	print('Z Total Time = {0}'.format(e_resps[1].get_total_speech_time()))
	print('Z Remaining Time = {0}'.format(e_resps[1].get_remaining_speech_time()))
	print('Z Speech Time = {0}'.format(e_resps[1].get_speech_time()))
	print('Z Enrollment Status = {0}'.format(e_resps[1].get_enrollment_status()))

	for a in range(0, section_count):
		time.sleep(3)

		if audiolength_list[a] < 1000:
			print('Audio bit is too short')
			continue

		identification_response = speakerhelper.identify_file(sections_filepath.format(a), id_list, force_short_audio = True)
		
		if(str(identification_response.get_identified_profile_id()) != '00000000-0000-0000-0000-000000000000'):
			print('Identified Speaker = {0}'.format(speakers[str(identification_response.get_identified_profile_id())]))
		else:
			print('Unidentified speaker')

		print('Confidence = {0}'.format(identification_response.get_confidence()))

		
		

	speakerhelper.delete_profile(id_list[0])
	speakerhelper.delete_profile(id_list[1])


main()