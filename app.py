# app.py

from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO

import threading, time

from operator import gt, ge, lt, le, eq, ne

import cv2

from picarx import Picarx
from vilib import Vilib

# comparator map for logic_compare
_comp_map = {
    'EQ':  eq,  'NEQ': ne,
    'LT':  lt,  'LTE': le,
    'GT':  gt,  'GTE': ge
}

app = Flask(__name__, static_folder="static", template_folder="templates")

socketio = SocketIO(app)

robot = Picarx()

vilib = Vilib()
vilib.camera_start(vflip=False, hflip=False, size=(640, 480))

stop_event = threading.Event()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """
    Video streaming route.   
    Returns a multipart MJPEG response, pulling frames from vilib.flask_img.
    """
    def gen():
        while True:
            if not hasattr(vilib, 'flask_img') or vilib.flask_img is None:
                time.sleep(0.01)
                continue

            # Encode as JPEG
            ret, jpeg = cv2.imencode('.jpg', vilib.flask_img)

            if not ret:
                continue

            frame = jpeg.tobytes()

            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            time.sleep(0.03)  # ~30 FPS

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


def eval_expr(block):
    """Evaluate simple expressions from Blockly JSON."""
    t = block['type']

    if t == 'math_number':
        return float(block['fields']['NUM'])

    if t == 'logic_boolean':
        # Blockly encodes TRUE/FALSE as strings
        return block['fields']['BOOL'] == 'TRUE'

    if t == 'logic_compare':
        op = block['fields']['OP']   # e.g. 'GT', 'LT'

        # use get_input_block instead of direct ['block']
        a_blk = get_input_block(block, 'A')
        b_blk = get_input_block(block, 'B')

        if not a_blk or not b_blk:
            raise RuntimeError("Incomplete logic_compare inputs")

        return _comp_map[op](eval_expr(a_blk), eval_expr(b_blk))
    
    if t == 'read_distance':
        return robot.get_distance()
    
    if t == 'read_line_status':
        # returns a list of 0/1 ints
        return robot.get_line_status(robot.get_grayscale_data())

    if t == 'read_cliff':
        # returns True/False
        return robot.get_cliff_status(robot.get_grayscale_data())

    if t == 'read_line':
        # read_line now returns the black/white status (0 or 1)
        idx = int(block['fields']['CHANNEL'])

        status = robot.get_line_status(robot.get_grayscale_data())
        return status[idx]

    raise RuntimeError(f"Unsupported expr type: {t}")


def get_input_block(b, name):
    """
    From a serialized block b, pull the real sub-block for input `name`,
    falling back to the shadow block if no real one is attached.
    """
    inp = b.get('inputs', {}).get(name, {})
    return inp.get('block') or inp.get('shadow')


def process_block(block, sid):
    """Recursively handle one block (and nested loops)."""
    btype  = block['type']
    fields = block.get('fields', {})

    # detection toggles
    if btype in ('face_detect_switch', 'traffic_detect_switch', 'qrcode_detect_switch', 
                 'hands_detect_switch', 'pose_detect_switch', 'object_detect_switch', 'image_classify_switch' ):
        # STATE field is a Python boolean literal True/False
        state = block['fields']['STATE'] == 'TRUE'

        # call the matching Vilib method
        getattr(Vilib, btype)(state)
        return

    # — Color detection toggle —
    if btype == 'color_detect':
        color = block['fields']['COLOR']
        
        if color == 'off':
            Vilib.close_color_detection()
        
        else:
            Vilib.color_detect(color)
        return

    # ——— Motion & Camera —————————————————————————————
    if btype == 'move_forward':
        robot.forward(float(fields.get('SPEED', 0)))
        return

    if btype == 'move_backward':
        robot.backward(float(fields.get('SPEED', 0)))
        return

    if btype == 'stop':
        robot.stop()
        return

    if btype == 'turn':
        robot.set_dir_servo_angle(float(fields.get('DEGREES', 0)))
        return

    if btype == 'pan_camera':
        robot.set_cam_pan_angle(float(fields.get('DEGREES', 0)))
        return

    if btype == 'tilt_camera':
        robot.set_cam_tilt_angle(float(fields.get('DEGREES', 0)))
        return

    # ——— Sleep ————————————————————————————————————————
    if btype == 'sleep':
        secs = float(fields.get('SECONDS', 1))

        # interruptible sleep
        if stop_event.wait(timeout=secs):
            raise KeyboardInterrupt()    
        return

    # ——— Built-in while/until loop —————————————————————
    if btype == 'controls_whileUntil':
        mode = block['fields']['MODE']  # 'WHILE' or 'UNTIL'
        cond_blk = get_input_block(block, 'BOOL')
        body_blk = get_input_block(block, 'DO')

        if not cond_blk:
            print("⚠ Missing condition block on controls_whileUntil; skipping")
            return

        if not body_blk:
            print("⚠ Missing DO stack on controls_whileUntil; skipping")
            return

        def cond_true():
            val = eval_expr(cond_blk)
            return val if mode == 'WHILE' else not val

        while not stop_event.is_set() and cond_true():
            curr = body_blk

            while curr and not stop_event.is_set():
                socketio.emit('highlight', {'id': curr['id']}, to=sid)
                stop_event.wait(0.1)
                process_block(curr, sid)
                curr = curr.get('next', {}).get('block')

        return

    if btype == 'controls_if':
        # Iterate through each IFn/DO n pair
        idx = 0

        while True:
            cond_name = f'IF{idx}'
            do_name = f'DO{idx}'

            if cond_name not in block.get('inputs', {}):
                break

            cond_blk = get_input_block(block, cond_name)

            # if there is no real or shadow condition, skip this clause
            if not cond_blk:
                idx += 1
                continue

            # evaluate and, if true, run its DO-stack
            if eval_expr(cond_blk):
                stmt = get_input_block(block, do_name)
                curr = stmt

                while curr and not stop_event.is_set():
                    socketio.emit('highlight', {'id': curr['id']}, to=sid)
                    stop_event.wait(0.1)
                    process_block(curr, sid)
                    curr = curr.get('next', {}).get('block')

                return   # done: don’t fall into else-clause or later IFs
            
            idx += 1

        # no IFn was true → run the ELSE clause if present
        else_blk = get_input_block(block, 'ELSE')
        curr = else_blk
        
        while curr and not stop_event.is_set():
            socketio.emit('highlight', {'id': curr['id']}, to=sid)
            stop_event.wait(0.1)
            process_block(curr, sid)
            curr = curr.get('next', {}).get('block')
        
        return

    # ——— Unknown block ———————————————————————————————
    print(f"⚠️ Unknown block type: {btype}")


@socketio.on('run_commands')
def handle_run(workspace_json):

    sid = request.sid
    stop_event.clear()

    def runner():
        
        try:
            
            # Iterate each top-level chain
            for root in workspace_json.get('blocks', {}).get('blocks', []):
                curr = root
                
                while curr and not stop_event.is_set():
                    # highlight & small delay
                    socketio.emit('highlight', {'id': curr['id']}, to=sid)
                    stop_event.wait(0.1)
                    # process (including nested loops)
                    process_block(curr, sid)
                    curr = curr.get('next', {}).get('block')
        
        except KeyboardInterrupt:
            # Stop was pressed mid-block
            pass
        
        finally:
            robot.stop()
            socketio.emit('highlight', {'id': None}, to=sid)
            socketio.emit('finished', to=sid)

    threading.Thread(target=runner, daemon=True).start()


@socketio.on('stop')
def handle_stop():
    stop_event.set()
    robot.stop()
    socketio.emit('finished', to=request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)