from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Global state
video_state = {
    'is_playing': False,
    'video_time': 0,       # Last known video time (in seconds)
    'last_updated': time.time()  # When that time was recorded
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    now = time.time()
    if video_state['is_playing']:
        # Calculate current time based on how long video has been playing
        current_time = video_state['video_time'] + (now - video_state['last_updated'])
    else:
        current_time = video_state['video_time']
    
    print(f"[SYNC] New user - sending time {current_time:.2f}, playing: {video_state['is_playing']}")
    emit('sync', {'time': current_time, 'is_playing': video_state['is_playing']})

@socketio.on('play')
def handle_play(current_time):
    video_state['is_playing'] = True
    video_state['video_time'] = current_time
    video_state['last_updated'] = time.time()
    emit('play', current_time, broadcast=True, include_self=False)

@socketio.on('pause')
def handle_pause(current_time):
    video_state['is_playing'] = False
    video_state['video_time'] = current_time
    video_state['last_updated'] = time.time()
    emit('pause', current_time, broadcast=True, include_self=False)

@socketio.on('seek')
def handle_seek(current_time):
    video_state['video_time'] = current_time
    video_state['last_updated'] = time.time()
    emit('seek', current_time, broadcast=True, include_self=False)

@socketio.on('resync_request')
def handle_resync():
    now = time.time()
    if video_state['is_playing']:
        current_time = video_state['video_time'] + (now - video_state['last_updated'])
    else:
        current_time = video_state['video_time']
    emit('sync', {'time': current_time, 'is_playing': video_state['is_playing']})


if __name__ == '__main__':
    socketio.run(app, debug=True)
