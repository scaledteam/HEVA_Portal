#
# Created by scaled
#

#
# You can configure settings there:
#

ARMATURE_NAME = 'Girl_HEVA'
FACE_NAME = 'Girl_Body'
PORT = 9000
CAPTURE_FRAMERATE = 30
AUDIO_ENABLE = False

# Just code

import bpy

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from threading import Thread

from time import perf_counter,sleep
from mathutils import Vector,Quaternion

if AUDIO_ENABLE:
    import pyaudio
    import wave

import datetime

def ShowMessageBox(message = "", title = "HEVA_Portal", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


# Object varriables
FRAMERATE = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
object_body = bpy.data.objects[ARMATURE_NAME]
object_face = bpy.data.objects[FACE_NAME].data.shape_keys
player_pose = object_body.pose.bones
player_values = object_face.key_blocks


# Audio settings
CHUNK = 1024
FORMAT = None
if AUDIO_ENABLE:
    FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

# Sound varriables
p = None
if AUDIO_ENABLE:
    p = pyaudio.PyAudio()
stream = None
frames = []

# Animation varriables
action_name = ""
capture_start_frame = 0
objects_capture_last_frame = 0
capture = False
local_frame_current = 0
time_previous = 0
capture_frame = 0
co = Vector((0, 0))
objects_capture_ready = False

# VMC varriables
bones_to_send = {
    'Head': player_pose['J_Bip_C_Head'],
    'Neck': player_pose['J_Bip_C_Neck'],
    'LeftEye': player_pose['J_Adj_L_FaceEye'],
    'RightEye': player_pose['J_Adj_R_FaceEye'],
    'A': player_values['MTH_A'],
    'U': player_values['MTH_U'],
    'E': player_values['MTH_E'],
    'Fun': player_values['MTH_Fun'],
    'Blink': player_values['EYE_Close'],
    'Blink_L': player_values['EYE_Close_L'],
    'Blink_R': player_values['EYE_Close_R'],
    'BrowsDownUp': player_values['BRW_Up'],
    #'BrowsDownUp': player_values['BRW_Fun'],
}


bones_to_apply1 = {
#    'Hips': [Vector(), Quaternion()],
#    'LeftUpperLeg': [Vector(), Quaternion()],
#    'RightUpperLeg': [Vector(), Quaternion()],
#    'LeftLowerLeg': [Vector(), Quaternion()],
#    'RightLowerLeg': [Vector(), Quaternion()],
#    'LeftFoot': [Vector(), Quaternion()],
#    'RightFoot': [Vector(), Quaternion()],
#    'Spine': [Vector(), Quaternion()],
#    'Chest': [Vector(), Quaternion()],
#    'Neck': [Vector(), Quaternion()],
    'Head': [Vector(), Quaternion()],
    'Neck': [Vector(), Quaternion()],
    'LeftEye': [Vector(), Quaternion()],
    'RightEye': [Vector(), Quaternion()],
#    'LeftShoulder': [Vector(), Quaternion()],
#    'RightShoulder': [Vector(), Quaternion()],
#    'LeftUpperArm': [Vector(), Quaternion()],
#    'RightUpperArm': [Vector(), Quaternion()],
#    'LeftLowerArm': [Vector(), Quaternion()],
#    'RightLowerArm': [Vector(), Quaternion()],
#    'LeftHand': [Vector(), Quaternion()],
#    'RightHand': [Vector(), Quaternion()],
}

bones_to_apply3 = {
    'A': 0,
    'U': 0,
    'E': 0,
    'Fun': 0,
    'Blink': 0,
    'Blink_L': 0,
    'Blink_R': 0,
    'BrowsDownUp': 0,
}
bones_to_apply1_list = list(bones_to_apply1)
bones_to_apply3_list = list(bones_to_apply3)

def heva_receiver_set_pos(address, *args):
    global bones_to_send
    global bones_to_apply1

    bone_name = args[0]
    if bone_name in bones_to_apply1:
        bones_to_apply1[bone_name][0][0] = args[1]
        bones_to_apply1[bone_name][0][1] = args[2]
        bones_to_apply1[bone_name][0][2] = args[3]
        bones_to_apply1[bone_name][1][0] = args[7]
        bones_to_apply1[bone_name][1][1] = args[6]
        bones_to_apply1[bone_name][1][2] = args[5]
        bones_to_apply1[bone_name][1][3] = args[4]

def heva_receiver_set_val(address, *args):
    global bones_to_send
    global bones_to_apply3
    #shape_key = bones_to_send[args[0]]
    #shape_key.value = args[1]
    bone_name = args[0]
    if bone_name in bones_to_apply3:
        bones_to_apply3[bone_name] = args[1]


def heva_receiver_set_keyframes(address, *args):
    #bpy.context.window_manager.update_tag()
    #bpy.context.scene.frame_current = this_frame
    #if len(bpy.context.view_layer.depsgraph.updates) > 0:
    #    bpy.context.view_layer.depsgraph.update()
    #bpy.context.view_layer.update()
    #bpy.context.evaluated_depsgraph_get().update()
    #for obj in bpy.context.scene.objects:
    #    obj.hide_render = obj.hide_render
    #global object_body
    #object_body.hide_render = not object_body.hide_render
    #bpy.context.scene.frame_current += 1
    #bpy.context.scene.frame_set(bpy.context.scene.frame_current)
    global objects_capture_ready
    objects_capture_ready = True
    pass


heva_receiver = None
def init_osc_server():
    dispatcher = Dispatcher()
    dispatcher.map("/VMC/Ext/Bone/Pos", heva_receiver_set_pos)
    dispatcher.map("/VMC/Ext/Blend/Val", heva_receiver_set_val)
    dispatcher.map("/VMC/Ext/Blend/Apply", heva_receiver_set_keyframes)

    try:
        global heva_receiver
        heva_receiver = ThreadingOSCUDPServer(("0.0.0.0", PORT), dispatcher)
        heva_receiver_thread = Thread(target=heva_receiver.serve_forever)
        heva_receiver_thread.start()
        return True
    except OSError:
        ShowMessageBox("OSC Server Not started", icon='ERROR')
        return False


def capture_start():
    global capture
    global capture_frame
    global capture_start_frame
    global local_frame_current
    global FRAMERATE
    global object_body
    global object_face
    global time_previous
    global co
    global objects_capture_last_frame
    global objects_capture_ready

    global CHUNK
    global FORMAT
    global CHANNELS
    global RATE
    global action_name
    global p
    global stream
    global frames
    capture_start_frame = bpy.context.scene.frame_current
    local_frame_current = bpy.context.scene.frame_current / FRAMERATE

    time_previous = perf_counter()

    for object in {object_body, object_face}:
        if object.animation_data and object.animation_data.nla_tracks:
            for nla_track in object.animation_data.nla_tracks:
                nla_track.mute=True
    if AUDIO_ENABLE:
        stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

    action_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    for bone_name in bones_to_apply1_list:
        bone = bones_to_send[bone_name]

        bone.keyframe_insert('location')
        bone.keyframe_insert('rotation_quaternion')

        rig_action = object_body.animation_data.action
        for fcurve in rig_action.fcurves:
            fcurve.mute = True

    for bone_name in bones_to_apply3_list:
        bone = bones_to_send[bone_name]

        bone.keyframe_insert('value')

        rig_action = object_face.animation_data.action
        for fcurve in rig_action.fcurves:
            fcurve.mute = True

def capture_stop():
    global capture
    global capture_frame
    global capture_start_frame
    global local_frame_current
    global FRAMERATE
    global object_body
    global object_face
    global time_previous
    global co
    global objects_capture_last_frame
    global objects_capture_ready

    global CHUNK
    global FORMAT
    global CHANNELS
    global RATE
    global action_name
    global p
    global stream
    global frames
    capture_frame = 0
    for object in {object_body, object_face}:
        if object.animation_data and object.animation_data.action:
            rig_action = object.animation_data.action
            rig_action.name = action_name + ' ' + object.name
            #for fcurve in rig_action.fcurves:
            #    fcurve.mute = False

            for fcurve in rig_action.fcurves:
                fcurve.mute = False

            strip = None
            try:
                strip = object.animation_data.nla_tracks.active.strips.new(action_name, capture_start_frame, rig_action)
            except:
                try:
                    strip = object.animation_data.nla_tracks.active.strips.new(action_name, capture_start_frame + 1, rig_action)
                except:
                    object.animation_data.nla_tracks.new()
                    strip = object.animation_data.nla_tracks.active.strips.new(action_name, capture_start_frame, rig_action)

            object.animation_data.action = None
            strip.extrapolation='NOTHING'
            for nla_track in object.animation_data.nla_tracks:
                nla_track.mute=False

    #this_frame = int(local_frame_current * FRAMERATE + 1)
    #bpy.context.scene.frame_current = this_frame

    if AUDIO_ENABLE:
        stream.stop_stream()
        stream.close()

        filename = '//' + action_name + '.wav'
        wf = wave.open(bpy.path.abspath(filename), 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        frames.clear()
        bpy.context.scene.sequence_editor.sequences.new_sound(action_name, filename, 1, capture_start_frame)



class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def execute(self, context):
        wm = context.window_manager
        #self._timer = wm.event_timer_add(1/CAPTURE_FRAMERATE, window=context.window)
        self._timer = wm.event_timer_add(0.5/CAPTURE_FRAMERATE, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global capture
        global capture_frame
        global capture_start_frame
        global local_frame_current
        global FRAMERATE
        global object_body
        global object_face
        global time_previous
        global co
        global objects_capture_last_frame
        global objects_capture_ready

        global CHUNK
        global FORMAT
        global CHANNELS
        global RATE
        global action_name
        global p
        global stream
        global frames

        local_frame_current += perf_counter() - time_previous
        time_previous = perf_counter()

        if event.value == 'RELEASE':
            if event.type == 'ESC':
                self.cancel(context)
                return {'CANCELLED'}
            elif event.type == 'F1':

                capture = not capture

                if capture:
                    capture_start()
                else:
                    capture_stop()


        #this_frame = int(local_frame_current * FRAMERATE + 1)
        #bpy.context.scene.frame_current = this_frame

        if objects_capture_ready:
            objects_capture_ready = False

            for bone_name in bones_to_apply1_list:
                bone = bones_to_send[bone_name]
                bone.location = bones_to_apply1[bone_name][0]
                bone.rotation_quaternion = bones_to_apply1[bone_name][1]

            for bone_name in bones_to_apply3_list:
                bone = bones_to_send[bone_name]
                bone.value = bones_to_apply3[bone_name]

            if capture:
                this_frame = int(local_frame_current * FRAMERATE + 1)

                #data = stream.read(CHUNK)
                #frames.append(data)
                if AUDIO_ENABLE:
                    data_frames = stream.get_read_available()
                    if data_frames:
                        data = stream.read(data_frames)
                        frames.append(data)

                if this_frame > objects_capture_last_frame:
                    objects_capture_last_frame = this_frame

                    ## Animation engine
                    delta_time = perf_counter() - time_previous
                    time_previous = perf_counter()

                    local_frame_current += delta_time

                    #capture_frame += 1
                    co[0] = local_frame_current * FRAMERATE

                    for object in {object_body, object_face}:
                        if object.animation_data and object.animation_data.action:
                            object_fcurves = object.animation_data.action.fcurves

                            for fcurve in object_fcurves:
                                try:
                                    co[1] = object.path_resolve(fcurve.data_path)[fcurve.array_index]
                                except:
                                    co[1] = object.path_resolve(fcurve.data_path)

                                capture_frame = len(fcurve.keyframe_points)
                                fcurve.keyframe_points.add(1)
                                fcurve.keyframe_points[capture_frame].co = co
                                fcurve.keyframe_points[capture_frame].handle_left = co
                                fcurve.keyframe_points[capture_frame].handle_right = co

                #bpy.context.scene.frame_current = int(local_frame_current * FRAMERATE + 1)
                #bpy.context.scene.frame_set(int(local_frame_current * FRAMERATE + 1))
                #bpy.context.scene.frame_current = int(local_frame_current * FRAMERATE + 1)
                bpy.context.scene.frame_current = this_frame

        return {'PASS_THROUGH'}

    def cancel(self, context):
        if capture:
            capture_stop()

        global heva_receiver
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        heva_receiver.shutdown()
        heva_receiver.server_close()

        if AUDIO_ENABLE:
            p.terminate()
        ShowMessageBox("Program terminated successfully!")

def register():
    bpy.utils.register_class(ModalTimerOperator)

def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)

if __name__ == "__main__":

    if init_osc_server():
        register()
        bpy.ops.wm.modal_timer_operator()
        ShowMessageBox("Program is running! Yay!")
