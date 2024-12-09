cd /home/serverpi/projects/wacsa/src
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 127.0.0.1:5000 'app:create_app()'