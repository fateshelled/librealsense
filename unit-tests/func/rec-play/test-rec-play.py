# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2021 Intel Corporation. All Rights Reserved.

#test:device L500*
#test:device D400*

import pyrealsense2 as rs, os, time, tempfile, sys
from rspy import devices, log, test

cp = dp = None
previous_depth_frame_number = -1
previous_color_frame_number = -1
got_frames = False

def got_frame():
    global got_frames
    got_frames = True

def color_frame_call_back( frame ):
    global previous_color_frame_number
    got_frame()
    test.check_frame_drops( frame, previous_color_frame_number )
    previous_color_frame_number = frame.get_frame_number()

def depth_frame_call_back( frame ):
    global previous_depth_frame_number
    got_frame()
    test.check_frame_drops( frame, previous_depth_frame_number )
    previous_depth_frame_number = frame.get_frame_number()

def restart_profiles():
    """
    you can't use the same profile twice, but we need the same profile several times. So this function resets the
    profiles with the given parameters to allow quick profile creation
    """
    global cp, dp, color_sensor, depth_sensor
    cp = next(p for p in color_sensor.profiles if p.fps() == 30
              and p.stream_type() == rs.stream.color
              and p.format() == rs.format.yuyv
              and p.as_video_stream_profile().width() == 1280
              and p.as_video_stream_profile().height() == 720)

    dp = next(p for p in
              depth_sensor.profiles if p.fps() == 30
              and p.stream_type() == rs.stream.depth
              and p.format() == rs.format.z16
              and p.as_video_stream_profile().width() == 1024
              and p.as_video_stream_profile().height() == 768)

# create temporary folder to record to that will be deleted automatically at the end of the script
temp_dir = tempfile.TemporaryDirectory(prefix='recordings_')
file_name = temp_dir.name + os.sep + 'rec.bag'

################################################################################################
test.start("Trying to record and playback using pipeline interface")
pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_record_to_file( file_name )
pipeline.start( cfg )
time.sleep(3)
pipeline.stop()
pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_device_from_file( file_name )
pipeline.start( cfg )

try:
    pipeline.wait_for_frames()
except Exception:
    test.unexpected_exception()

pipeline.stop()
del cfg

test.finish()

################################################################################################
test.start("Trying to record and playback using sensor interface")
dev = test.find_first_device_or_exit()
recorder = rs.recorder( file_name, dev )
depth_sensor = dev.first_depth_sensor()
color_sensor = dev.first_color_sensor()

restart_profiles()

depth_sensor.open( dp )
depth_sensor.start( lambda f: None )
color_sensor.open( cp )
color_sensor.start( lambda f: None )

time.sleep(3)

recorder.pause()
del recorder
color_sensor.stop()
color_sensor.close()
depth_sensor.stop()
depth_sensor.close()

ctx = rs.context()
playback = ctx.load_device( file_name )

depth_sensor = playback.first_depth_sensor()
color_sensor = playback.first_color_sensor()

restart_profiles()

depth_sensor.open( dp )
depth_sensor.start( depth_frame_call_back )
color_sensor.open( cp )
color_sensor.start( color_frame_call_back )

time.sleep(3)

color_sensor.stop()
color_sensor.close()
depth_sensor.stop()
depth_sensor.close()
playback.pause()

test.check( got_frames )

del playback
del depth_sensor
del color_sensor

test.finish()

#####################################################################################################
test.start("Trying to record and playback using sensor interface with syncer")

sync = rs.syncer()
dev = test.find_first_device_or_exit()
recorder = rs.recorder( file_name, dev )
depth_sensor = dev.first_depth_sensor()
color_sensor = dev.first_color_sensor()

restart_profiles()

depth_sensor.open( dp )
depth_sensor.start( sync )
color_sensor.open( cp )
color_sensor.start( sync )

time.sleep(3)

recorder.pause()
del recorder
color_sensor.stop()
color_sensor.close()
depth_sensor.stop()
depth_sensor.close()

ctx = rs.context()
playback = ctx.load_device( file_name )

depth_sensor = playback.first_depth_sensor()
color_sensor = playback.first_color_sensor()

restart_profiles()

depth_sensor.open( dp )
depth_sensor.start( sync )
color_sensor.open( cp )
color_sensor.start( sync )

try:
    sync.wait_for_frames()
except Exception:
    test.unexpected_exception()

color_sensor.stop()
color_sensor.close()
depth_sensor.stop()
depth_sensor.close()
playback.pause()
del playback
del depth_sensor
del color_sensor

test.finish()

#############################################################################################
test.print_results_and_exit()
