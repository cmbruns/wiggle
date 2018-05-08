#!/bin/env python

# file openvr_gl_renderer.py

from OpenGL import GL
import numpy

import openvr

"""
Renders OpenGL scenes to virtual reality headsets using OpenVR API
"""


# TODO: matrixForOpenVrMatrix() is not general, it is specific the perspective and 
# modelview matrices used in this example
def matrixForOpenVrMatrix(mat):
    if len(mat.m) == 4: # HmdMatrix44_t?
        result = numpy.matrix(
                ((mat.m[0][0], mat.m[1][0], mat.m[2][0], mat.m[3][0]),
                 (mat.m[0][1], mat.m[1][1], mat.m[2][1], mat.m[3][1]), 
                 (mat.m[0][2], mat.m[1][2], mat.m[2][2], mat.m[3][2]), 
                 (mat.m[0][3], mat.m[1][3], mat.m[2][3], mat.m[3][3]),)
            , numpy.float32)
    elif len(mat.m) == 3: # HmdMatrix34_t?
        result = numpy.matrix(
                ((mat.m[0][0], mat.m[1][0], mat.m[2][0], 0.0),
                 (mat.m[0][1], mat.m[1][1], mat.m[2][1], 0.0), 
                 (mat.m[0][2], mat.m[1][2], mat.m[2][2], 0.0), 
                 (mat.m[0][3], mat.m[1][3], mat.m[2][3], 1.0),)
            , numpy.float32)
    return result


class VrCamera(object):
    pass

class OpenVrFramebuffer(object):
    "Framebuffer for rendering one eye"
    
    def __init__(self, width, height, multisample = 0):
        self.fb = 0
        self.depth_buffer = 0
        self.texture_id = 0
        self.width = width
        self.height = height
        self.compositor = None
        self.multisample = multisample
        
    def init_gl(self):
        # Set up framebuffer and render textures
        self.fb = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fb)
        self.depth_buffer = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.depth_buffer)
        if self.multisample > 0:
            GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER, self.multisample, GL.GL_DEPTH24_STENCIL8, self.width, self.height)
        else:
            GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH24_STENCIL8, self.width, self.height)
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_STENCIL_ATTACHMENT, GL.GL_RENDERBUFFER, self.depth_buffer)
        self.texture_id = int(GL.glGenTextures(1))
        if self.multisample > 0:
            GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, self.texture_id)
            GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE, self.multisample, GL.GL_RGBA8, self.width, self.height, True)
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D_MULTISAMPLE, self.texture_id, 0)
        else:
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, self.width, self.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.texture_id, 0)
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            raise Exception("Incomplete framebuffer")
        # Resolver framebuffer in case of multisample antialiasing
        if self.multisample > 0:
            self.resolve_fb = GL.glGenFramebuffers(1)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.resolve_fb)
            self.resolve_texture_id = int(GL.glGenTextures(1))
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.resolve_texture_id)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, self.width, self.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.resolve_texture_id, 0)
            status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
            if status != GL.GL_FRAMEBUFFER_COMPLETE:
                GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
                raise Exception("Incomplete framebuffer")
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)   
        # OpenVR texture data
        self.texture = openvr.Texture_t()
        if self.multisample > 0:
            self.texture.handle = self.resolve_texture_id
        else:
            self.texture.handle = self.texture_id
        self.texture.eType = openvr.TextureType_OpenGL
        self.texture.eColorSpace = openvr.ColorSpace_Gamma
        
    def submit(self, eye):
        if self.multisample > 0:
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.fb)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.resolve_fb)
            GL.glBlitFramebuffer(0, 0, self.width, self.height, 
                              0, 0, self.width, self.height,
                              GL.GL_COLOR_BUFFER_BIT, GL.GL_LINEAR)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, 0)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
        openvr.VRCompositor().submit(eye, self.texture)
        
    def dispose_gl(self):
        GL.glDeleteTextures([self.texture_id])
        GL.glDeleteRenderbuffers(1, [self.depth_buffer])
        GL.glDeleteFramebuffers(1, [self.fb])
        self.fb = 0
        if self.multisample > 0:
            GL.glDeleteTextures([self.resolve_texture_id])
            GL.glDeleteFramebuffers(1, [self.resolve_fb])


class OpenVrGlRenderer(list):
    "Renders to virtual reality headset using OpenVR and OpenGL APIs"

    def __init__(self, actor=None, window_size=(800,600), multisample=0):
        self.vr_system = None
        self.left_fb = None
        self.right_fb = None
        self.window_size = window_size
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
        if actor is not None:
            try:
                len(actor)
                self.extend(actor)
            except TypeError:
                self.append(actor)
        self.do_mirror = False
        self.multisample = multisample
        self.compositor = None
        self.left_camera = VrCamera()
        self.right_camera = VrCamera()

    def init_gl(self):
        "allocate OpenGL resources"
        self.vr_system = openvr.init(openvr.VRApplication_Scene)
        w, h = self.vr_system.getRecommendedRenderTargetSize()
        self.left_fb = OpenVrFramebuffer(w, h, multisample=self.multisample)
        self.right_fb = OpenVrFramebuffer(w, h, multisample=self.multisample)
        self.compositor = openvr.VRCompositor()
        if self.compositor is None:
            raise Exception("Unable to create compositor") 
        self.left_fb.init_gl()
        self.right_fb.init_gl()
        # Compute projection matrix
        zNear = 0.2
        zFar = 500.0
        self.left_camera.projection = numpy.asarray(matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
                openvr.Eye_Left, 
                zNear, zFar)))
        self.right_camera.projection = numpy.asarray(matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
                openvr.Eye_Right, 
                zNear, zFar)))
        self.view_left = matrixForOpenVrMatrix(
            self.vr_system.getEyeToHeadTransform(openvr.Eye_Left)).I  # head_X_eye in Kane notation
        self.view_right = matrixForOpenVrMatrix(
            self.vr_system.getEyeToHeadTransform(openvr.Eye_Right)).I  # head_X_eye in Kane notation
        for actor in self:
            actor.init_gl()

    def render_scene(self):
        if self.compositor is None:
            return
        self.compositor.waitGetPoses(self.poses, openvr.k_unMaxTrackedDeviceCount, None, 0)
        hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if not hmd_pose0.bPoseIsValid:
            return
        hmd_pose1 = hmd_pose0.mDeviceToAbsoluteTracking # head_X_room in Kane notation
        hmd_pose = matrixForOpenVrMatrix(hmd_pose1).I # room_X_head in Kane notation
        # Use the pose to compute things
        modelview = hmd_pose
        self.left_camera.view_matrix = modelview * self.view_left # room_X_eye(left) in Kane notation
        self.right_camera.view_matrix = modelview * self.view_right # room_X_eye(right) in Kane notation
        # Repack the resulting matrices to have default stride, to avoid
        # problems with weird strides and OpenGL
        self.left_camera.view_matrix = numpy.asarray(numpy.matrix(self.left_camera.view_matrix, dtype=numpy.float32))
        self.right_camera.view_matrix = numpy.asarray(numpy.matrix(self.right_camera.view_matrix, dtype=numpy.float32))
        # 1) On-screen render:
        if self.do_mirror:
            GL.glViewport(0, 0, self.window_size[0], self.window_size[1])
            # Display left eye view to screen
            self.display_gl(self.left_camera.view_matrix, self.left_camera)
        # 2) VR render
        # Left eye view
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.left_fb.fb)
        GL.glViewport(0, 0, self.left_fb.width, self.left_fb.height)
        self.display_gl(camera=self.left_camera)
        self.left_fb.submit(openvr.Eye_Left)
        # self.compositor.submit(openvr.Eye_Left, self.left_fb.texture)
        # Right eye view
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.right_fb.fb)
        self.display_gl(camera=self.right_camera)
        self.right_fb.submit(openvr.Eye_Right)
        # self.compositor.submit(openvr.Eye_Right, self.right_fb.texture)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        
    def display_gl(self, camera):
        GL.glClearColor(0.5, 0.5, 0.5, 0.0) # gray background
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        for actor in self:
            actor.display_gl(camera)

    def dispose_gl(self):
        for actor in self:
            actor.dispose_gl()
        if self.vr_system is not None:
            openvr.shutdown()
            self.vr_system = None
        if self.left_fb is not None:
            self.left_fb.dispose_gl()
            self.right_fb.dispose_gl()
