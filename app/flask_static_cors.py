from flask import Flask
from flask_cors import cross_origin

class FlaskStaticCors(Flask):
    @cross_origin()
    def send_static_file(self, filename):
        return super(FlaskStaticCors, self).send_static_file(filename)