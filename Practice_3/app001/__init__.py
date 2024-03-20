from flask import Flask

app = Flask (__name__)

from app001 import routes

from app001 import app

if __name__ == '__main__':
    app.run(port='5001', debug=True)