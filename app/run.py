
from app import app, socketio

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--prod', action='store_true')
    args = parser.parse_args()

    socketio.run(app, debug=not args.prod, port=args.port, host=args.host)
