from app import app

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', default='127.0.0.0')
    parser.add_argument('--prod', action='store_true')
    args = parser.parse_args()

    app.run(debug=not args.prod, port=args.port, host=args.host)
