import sys
import time

import openvr
from pynput.keyboard import Key, Listener


class ProbeCalibrator(object):
    def __init__(self):
        self._keep_polling = True
        self._pulse_remaining = 0
        self._was_pressed = False
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            self.poll()

    def handle_controller_buttons(self, poses):
        vr_system = openvr.VRSystem()
        openvr.VRControllerState_t
        for d in range(openvr.k_unMaxTrackedDeviceCount):
            dc = vr_system.getTrackedDeviceClass(d)
            if dc != openvr.TrackedDeviceClass_Controller:
                continue
            if dc == openvr.TrackedDeviceClass_HMD:
                continue
            pose = poses[d]
            if not pose.bPoseIsValid:
                continue
            result, state = vr_system.getControllerState(d)
            if state.ulButtonPressed & (1 << openvr.k_EButton_SteamVR_Trigger):
                if not self._was_pressed:
                    print('pressed')
                    self.start_pulse(d)
                    self._was_pressed = True
                self.check_pulse(d)
            else:
                self._was_pressed = False
            #     print('trigger')
            # print(pose.mDeviceToAbsoluteTracking)
            # todo:

    def on_press(self, key):
        if key == Key.esc:
            self._keep_polling = False

    def on_release(self, key):
        pass

    def poll(self):
        openvr.init(openvr.VRApplication_Scene)
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        poses = poses_t()
        while self._keep_polling:
            openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)
            self.handle_controller_buttons(poses)
        openvr.shutdown()

    def start_pulse(self, device_id):
        self._pulse_remaining = 6

    def check_pulse(self, device_id):
        if self._pulse_remaining > 0:
            openvr.VRSystem().triggerHapticPulse(device_id, 0, 2000)
            self._pulse_remaining -= 1


if __name__ == '__main__':
    ProbeCalibrator()
