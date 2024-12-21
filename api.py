### github.com/nfoisking

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import json

app = Flask(__name__)
CORS(app)

database = {}

KNOWN_CAPES = {
    "2340c0e03dd24a11b15a8b33c2a7e9e32abb2051b2481d0ba7defd635ca7a933": "Migrator",
    "f9a76537647989f9a0b6d001e320dac591c359e9e61a31f4ce11c88f207f0ad4": "Vanilla",
    "7658c5025c77cfac7574aab3af94a46a8886e3b7722a895255fbf22ab8652434": "Minecraft Experience",
    "cd9d82ab17fd92022dbd4a86cde4c382a7540e117fae7b9a2853658505a80625": "15TH Anniversary",
    "afd553b39358a24edfe3b8a9a939fa5fa4faa4d9a9c3d6af8eafb377fa05c2bb": "Cherry Blossom",
    "cb40a92e32b57fd732a00fc325e7afb00a7ca74936ad50d8e860152e482cfbde": "Purple Heart",
    "569b7f2a1d00d26f30efe3f9ab9ac817b1e6d35f4f3cfb0324ef2d328223d350": "Followers",
    "56c35628fe1c4d59dd52561a3d03bfa4e1a76d397c8b9c476c2f77cb6aebb1df": "MCC 15th Year",
    "e7dfea16dc83c97df01a12fabbd1216359c0cd0ea42f9999b6e97c584963e980": "Minecon 2016",
    "b0cc08840700447322d953a02b965f1d65a13a603bf64b17c803c21446fe1635": "Minecon 2015",
    "153b1a0dfcbae953cdeb6f2c2bf6bf79943239b1372780da44bcbb29273131da": "Minecon 2013",
    "a2e8d97ec79100e90a75d369d1b3ba81273c4f82bc1b737e934eed4a854be1b6": "Minecon 2012",
    "953cac8b779fe41383e675ee2b86071a71658f2180f56fbce8aa315ea70e2ed6": "Minecon 2011"
}

def fetch_capes(username):
    try:
        user_response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if user_response.status_code != 200:
            return {"error": "Jogador não encontrado"}

        user_data = user_response.json()
        uuid = user_data['id']

        profile_response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        if profile_response.status_code != 200:
            return {"error": "Erro ao buscar perfil do jogador"}

        profile_data = profile_response.json()

        texture_property = next((prop for prop in profile_data['properties'] if prop['name'] == 'textures'), None)
        if not texture_property:
            return {"error": "O jogador não possui dados de textura"}

        texture_value = texture_property['value']
        texture_data = json.loads(base64.b64decode(texture_value).decode())

        cape_data = texture_data.get('textures', {}).get('CAPE', None)
        if cape_data:
            cape_url = cape_data["url"]
            cape_id = cape_url.split("/")[-1]  
            cape_name = KNOWN_CAPES.get(cape_id, "Capa desconhecida")
            return {"name": username, "uuid": uuid, "cape_url": cape_url, "cape_name": cape_name}
        else:
            return {"name": username, "uuid": uuid, "cape_url": None, "cape_name": None}
    except Exception as e:
        return {"error": str(e)}

@app.route('/players', methods=['GET'])
def list_players():
    return jsonify(database)

@app.route('/player/<username>', methods=['GET'])
def get_player(username):
    cape_info = fetch_capes(username)

    if "error" in cape_info:
        return jsonify({"error": cape_info["error"]}), 400

    return jsonify(cape_info)

if __name__ == '__main__':
    app.run(debug=True)
