# board-id = 38 (Muse 2)
# serial-number = Muse-[4 digits]

# -*- coding: utf-8 -*-
# vispy: gallery 2
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# integrating the muselsl visualizer code with a brainflow backend. 

import argparse
import logging

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

from vispy import gloo, app, visuals

import numpy as np
import math
from seaborn import color_palette
from scipy.signal import lfilter, lfilter_zi
from mne.filter import create_filter
from eegnb.devices.eeg import EEG

VERT_SHADER = """
#version 120
// y coordinate of the position.
attribute float a_position;
// row, col, and time index.
attribute vec3 a_index;
varying vec3 v_index;
// 2D scaling factor (zooming).
uniform vec2 u_scale;
// Size of the table.
uniform vec2 u_size;
// Number of samples per signal.
uniform float u_n;
// Color.
attribute vec3 a_color;
varying vec4 v_color;
// Varying variables used for clipping in the fragment shader.
varying vec2 v_position;
varying vec4 v_ab;
void main() {
    float n_rows = u_size.x;
    float n_cols = u_size.y;
    // Compute the x coordinate from the time index.
    float x = -1 + 2*a_index.z / (u_n-1);
    vec2 position = vec2(x - (1 - 1 / u_scale.x), a_position);
    // Find the affine transformation for the subplots.
    vec2 a = vec2(1./n_cols, 1./n_rows)*.9;
    vec2 b = vec2(-1 + 2*(a_index.x+.5) / n_cols,
                    -1 + 2*(a_index.y+.5) / n_rows);
    // Apply the static subplot transformation + scaling.
    gl_Position = vec4(a*u_scale*position+b, 0.0, 1.0);
    v_color = vec4(a_color, 1.);
    v_index = a_index;
    // For clipping test in the fragment shader.
    v_position = gl_Position.xy;
    v_ab = vec4(a, b);
}
"""

FRAG_SHADER = """
#version 120
varying vec4 v_color;
varying vec3 v_index;
varying vec2 v_position;
varying vec4 v_ab;
void main() {
    gl_FragColor = v_color;
    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;
    // Clipping test.
    vec2 test = abs((v_position.xy-v_ab.zw)/v_ab.xy);
    if ((test.x > 1))
        discard;
}
"""

class Canvas(app.Canvas):
    def __init__(self, board_shim, scale=500, filt=True):
        app.Canvas.__init__(self, title='EEG - Use your wheel to zoom!',
                            keys='interactive')
        
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate
        
        window = 10
        self.sfreq = BoardShim.get_sampling_rate(self.board_id)
        n_samples = int(self.sfreq * window)
        self.n_chans = len(self.eeg_channels)
        ch_names = BoardShim.get_eeg_names(self.board_id)

        # Number of cols and rows in the table.
        n_rows = self.n_chans
        n_cols = 1

        # Number of signals.
        m = n_rows * n_cols

        # Number of samples per signal.
        n = n_samples

        # Various signal amplitudes.
        amplitudes = np.zeros((m, n)).astype(np.float32)
        # gamma = np.ones((m, n)).astype(np.float32)
        # Generate the signals as a (m, n) array.
        y = amplitudes

        color = color_palette("RdBu_r", n_rows)

        color = np.repeat(color, n, axis=0).astype(np.float32)
        # Signal 2D index of each vertex (row and col) and x-index (sample index
        # within each signal).
        index = np.c_[np.repeat(np.repeat(np.arange(n_cols), n_rows), n),
                      np.repeat(np.tile(np.arange(n_rows), n_cols), n),
                      np.tile(np.arange(n), m)].astype(np.float32)

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = y.reshape(-1, 1)
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (n_rows, n_cols)
        self.program['u_n'] = n

        # text
        self.font_size = 48.
        self.names = []
        self.quality = []
        for ii in range(self.n_chans):
            text = visuals.TextVisual(ch_names[ii], bold=True, color='white')
            self.names.append(text)
            text = visuals.TextVisual('', bold=True, color='white')
            self.quality.append(text)

        self.quality_colors = color_palette("RdYlGn", 11)[::-1]

        self.scale = scale
        self.n_samples = n_samples
        self.filt = filt
        self.af = [1.0]

        self.data_f = np.zeros((n_samples, self.n_chans))
        self.data = np.zeros((n_samples, self.n_chans))

        self.bf = create_filter(self.data_f.T, self.sfreq, 3, 40.,
                                method='fir')

        zi = lfilter_zi(self.bf, self.af)
        self.filt_state = np.tile(zi, (self.n_chans, 1)).transpose()

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def on_key_press(self, event):

        # toggle filtering
        if event.key.name == 'D':
            self.filt = not self.filt

        # increase time scale
        if event.key.name in ['+', '-']:
            if event.key.name == '+':
                dx = -0.05
            else:
                dx = 0.05
            scale_x, scale_y = self.program['u_scale']
            scale_x_new, scale_y_new = (scale_x * math.exp(1.0 * dx),
                                        scale_y * math.exp(0.0 * dx))
            self.program['u_scale'] = (
                max(1, scale_x_new), max(1, scale_y_new))
            self.update()

    def on_mouse_wheel(self, event):
        dx = np.sign(event.delta[1]) * .05
        scale_x, scale_y = self.program['u_scale']
        scale_x_new, scale_y_new = (scale_x * math.exp(0.0 * dx),
                                    scale_y * math.exp(2.0 * dx))
        self.program['u_scale'] = (max(1, scale_x_new), max(0.01, scale_y_new))
        self.update()

    def on_timer(self, event):
        """Add some data at the end of each signal (real-time signals)."""
        
        data = self.board_shim.get_current_board_data(5)
        data = data.T
        eeg_samples = data[:, BoardShim.get_eeg_channels(self.board_id)]
        eeg_timestamps = data[:, BoardShim.get_timestamp_channel(self.board_id)]
        
        samples = np.array(eeg_samples)
        timestamps = np.array(eeg_timestamps)
        
        if any(timestamps):
            samples = np.array(samples)[:, ::-1]

            self.data = np.vstack([self.data, samples])
            self.data = self.data[-self.n_samples:]
            filt_samples, self.filt_state = lfilter(self.bf, self.af, samples,
                                                    axis=0, zi=self.filt_state)
            self.data_f = np.vstack([self.data_f, filt_samples])
            self.data_f = self.data_f[-self.n_samples:]

            if self.filt:
                plot_data = self.data_f / self.scale
            elif not self.filt:
                plot_data = (self.data - self.data.mean(axis=0)) / self.scale

            sd = np.std(plot_data[-int(self.sfreq):],
                        axis=0)[::-1] * self.scale
            co = np.int32(np.tanh((sd - 30) / 15) * 5 + 5)
            for ii in range(self.n_chans):
                self.quality[ii].text = '%.2f' % (sd[ii])
                self.quality[ii].color = self.quality_colors[co[ii]]
                self.quality[ii].font_size = 12 + co[ii]

                self.names[ii].font_size = 12 + co[ii]
                self.names[ii].color = self.quality_colors[co[ii]]

            self.program['a_position'].set_data(
                plot_data.T.ravel().astype(np.float32))
            self.update()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        for ii, t in enumerate(self.names):
            t.transforms.configure(canvas=self, viewport=vp)
            t.pos = (self.size[0] * 0.025,
                     ((ii + 0.5) / self.n_chans) * self.size[1])

        for ii, t in enumerate(self.quality):
            t.transforms.configure(canvas=self, viewport=vp)
            t.pos = (self.size[0] * 0.975,
                     ((ii + 0.5) / self.n_chans) * self.size[1])

    def on_draw(self, event):
        gloo.clear()
        gloo.set_viewport(0, 0, *self.physical_size)
        self.program.draw('line_strip')
        [t.draw() for t in self.names + self.quality]

def view(
    board_id=BoardIds.MUSE_2_BOARD,
    serial_id=None
):
    
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)
    
    params = BrainFlowInputParams()
    params.serial_number = serial_id
    
    try:
        board_shim = BoardShim(board_id, params)
        board_shim.prepare_session()
        board_shim.start_stream(450000, None)
        Canvas(board_shim)
        app.run()
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=10)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.MUSE_2_BOARD)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file

    try:
        board_shim = BoardShim(args.board_id, params)
        board_shim.prepare_session()
        board_shim.start_stream(450000, args.streamer_params)
        Canvas(board_shim)
        app.run()
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


if __name__ == '__main__':
    main()