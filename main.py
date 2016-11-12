#dependencies: ffmpeg, requests

import os
import sys
import requests
from keys import *
from msft_sr import IdentificationServiceHttpClientHelper
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def main():
	locale = 'en-us'

	localdir = os.path.dirname(__file__)
	sample_filepath = os.path.join(localdir, "samples/sample1.wav")
	print(sample_filepath)
	sections_filepath = os.path.join(localdir, "sections/section{0}.wav")
	sound_input = AudioSegment.from_wav(sample_filepath)

	speakers = {
		"Obama": "000",
		"Galifianakis": "000"
	}

	zach_filepath = os.path.join(localdir, "samples/zachsample2.wav")
	zach_outfile = os.path.join(localdir, "samples/zachpost.wav")
	zach_input = AudioSegment.from_wav(zach_filepath)
	zach_input = zach_input.split_to_mono()[0]
	zach_input = zach_input.set_frame_rate(16000)
	zach_input.export(zach_outfile, format="wav")

	obama_filepath = os.path.join(localdir, "samples/obamasample.wav")
	obama_outfile = os.path.join(localdir, "samples/obamapost.wav")
	obmaa_input = AudioSegment.from_wav(obama_filepath)
	obama_input = zach_input.split_to_mono()[0]
	obama_input = zach_input.set_frame_rate(16000)
	obama_input.export(obama_outfile, format="wav")

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
		if(len(section) < 1000):
			section = section + AudioSegment.silent(duration = (1000 - len(section)))

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
		print(profile_id)

	speakers[id_list[0]] = 'Obama'
	speakers[id_list[1]] = 'Zach'

	e_resps = []

	e_resps.append(speakerhelper.enroll_profile(id_list[0], obama_outfile))
	print('O Total Time = {0}'.format(e_resps[0].get_total_speech_time()))
	print('O Remaining Time = {0}'.format(e_resps[0].get_remaining_speech_time()))
	print('O Speech Time = {0}'.format(e_resps[0].get_speech_time()))
	print('O Enrollment Status = {0}'.format(e_resps[0].get_enrollment_status()))

	e_resps.append(speakerhelper.enroll_profile(id_list[1], zach_outfile))
	print('Z Total Time = {0}'.format(e_resps[1].get_total_speech_time()))
	print('Z Remaining Time = {0}'.format(e_resps[1].get_remaining_speech_time()))
	print('Z Speech Time = {0}'.format(e_resps[1].get_speech_time()))
	print('Z Enrollment Status = {0}'.format(e_resps[1].get_enrollment_status()))

	for a in range(0, section_count):
		identification_response = speakerhelper.identify_file(sections_filepath.format(a), id_list, force_short_audio = True)
		print('Identified Speaker = {0}'.format(speakers[str(identification_response.get_identified_profile_id())]))
		print('Confidence = {0}'.format(identification_response.get_confidence()))

	speakerhelper.delete_profile(id_list[0])
	speakerhelper.delete_profile(id_list[1])


main()