#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists',methods=["GET","POST"])
def get_scientists():
    if request.method=="GET":
        all = Scientist.query.all()
        # print (all)
        scientists = []
        for scientist in all:
            scientists.append(scientist.to_dict(rules=('-missions',)))
        # print (scientists)
        return scientists,200
    elif request.method=="POST":
        data = request.json
        # print (data)
        scientist = Scientist()
        try:
            for attr in data:
                setattr(scientist,attr,data[attr])
                # scientist[attr] = data[attr]
                print (attr,data[attr])
            # print (scientist.name, scientist.field_of_study)
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(),201
        except (IntegrityError,ValueError) as ie:
            return {"errors": [str(ie)]},400
            

@app.route('/scientists/<int:id>',methods=["GET","PATCH","DELETE"])
def get_scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id==id).first()
    if not scientist:
        return {"error": "Scientist not found"},404
    if request.method=="GET":
        return (scientist.to_dict(rules=("missions",))),200
    elif request.method=="PATCH":
        data = request.json
        try: 
            for attr in data:
                setattr(scientist,attr,data[attr])
            db.session.commit()
            return scientist.to_dict(),202
        except (IntegrityError,ValueError) as ie:
            return {"errors":ie.args},400
    elif request.method=="DELETE":
        db.session.delete(scientist)
        db.session.commit()
        return {},204
    
@app.route('/planets',methods=["GET"])
def get_planets():
    if request.method=="GET":
        all = Planet.query.all()
        planets = []
        for planet in all:
            planets.append(planet.to_dict(rules=('-missions',)))
        return planets,200
    
@app.route('/missions',methods=["POST"])
def add_mission():
    if request.method=="POST":
        data = request.json
        mission = Mission()
        try:
            for attr in data:
                setattr(mission,attr,data[attr])
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(rules=("scientist",'planet',)),201
        except (IntegrityError,ValueError) as ie:
            return {"errors":ie.args},400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
