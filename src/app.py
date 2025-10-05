import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)



@app.route('/people', methods=['GET'])
def get_all_people():
    """Get all characters"""
    characters = Characters.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):

    character = Characters.query.get(people_id)
    if character is None:
        raise APIException('Character not found', status_code=404)
    return jsonify(character.serialize()), 200



@app.route('/planets', methods=['GET'])
def get_all_planets():

    planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    """Get a single planet by id"""
    planet = Planets.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    return jsonify(planet.serialize()), 200



@app.route('/users', methods=['GET'])
def get_all_users():

    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():

    user_id = request.args.get('user_id', type=int)
    
    if user_id is None:
        raise APIException('user_id is required as query parameter', status_code=400)
    
    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    
    result = {
        "user": user.serialize(),
        "favorites": []
    }
    
    for fav in favorites:
        favorite_item = {"id": fav.id}
        
        if fav.planets_id:
            planet = Planets.query.get(fav.planets_id)
            favorite_item["type"] = "planet"
            favorite_item["planet"] = planet.serialize() if planet else None
        
        if fav.characters_id:
            character = Characters.query.get(fav.characters_id)
            favorite_item["type"] = "character"
            favorite_item["character"] = character.serialize() if character else None
        
        result["favorites"].append(favorite_item)
    
    return jsonify(result), 200



@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    body = request.get_json(silent=True)
    if body is None:
        raise APIException('Body is required', status_code=400)
    
    user_id = body.get('user_id')
    if user_id is None:
        raise APIException('user_id is required in body', status_code=400)
    
  
    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)
    
 
    planet = Planets.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    
  
    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, 
        planets_id=planet_id
    ).first()
    
    if existing_favorite:
        raise APIException('This planet is already in favorites', status_code=400)
    

    new_favorite = Favorite()
    new_favorite.user_id = user_id
    new_favorite.planets_id = planet_id
    
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Planet added to favorites successfully",
        "favorite_id": new_favorite.id,
        "planet": planet.serialize()
    }), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):

    body = request.get_json(silent=True)
    if body is None:
        raise APIException('Body is required', status_code=400)
    
    user_id = body.get('user_id')
    if user_id is None:
        raise APIException('user_id is required in body', status_code=400)
    

    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)
    

    character = Characters.query.get(people_id)
    if character is None:
        raise APIException('Character not found', status_code=404)
    

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, 
        characters_id=people_id
    ).first()
    
    if existing_favorite:
        raise APIException('This character is already in favorites', status_code=400)
    
 
    new_favorite = Favorite()
    new_favorite.user_id = user_id
    new_favorite.characters_id = people_id
    
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Character added to favorites successfully",
        "favorite_id": new_favorite.id,
        "character": character.serialize()
    }), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    body = request.get_json(silent=True)
    if body is None:
        raise APIException('Body is required', status_code=400)
    
    user_id = body.get('user_id')
    if user_id is None:
        raise APIException('user_id is required in body', status_code=400)
    

    favorite = Favorite.query.filter_by(
        user_id=user_id,
        planets_id=planet_id
    ).first()
    
    if favorite is None:
        raise APIException('Favorite planet not found', status_code=404)
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Planet removed from favorites successfully"
    }), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):

    body = request.get_json(silent=True)
    if body is None:
        raise APIException('Body is required', status_code=400)
    
    user_id = body.get('user_id')
    if user_id is None:
        raise APIException('user_id is required in body', status_code=400)
    

    favorite = Favorite.query.filter_by(
        user_id=user_id,
        characters_id=people_id
    ).first()
    
    if favorite is None:
        raise APIException('Favorite character not found', status_code=404)
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Character removed from favorites successfully"
    }), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)