from flask import Flask
from flask_cors import cross_origin

class FlaskStaticCors(Flask):
    @cross_origin()
    def send_from_directory(self, path, filename):
        return super(FlaskStaticCors, self).send_from_directory(path, filename)