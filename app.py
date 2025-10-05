import os
import json
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np

# Optional: use dotenv if available
try:
    from dotenv import load_dotenv, set_key
    load_dotenv()
    HAS_DOTENV = True
except Exception:
    HAS_DOTENV = False


app = Flask(__name__)

# Allow all origins by default for simplicity; change in production
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

NASA_API_KEY = os.getenv("NASA_API_KEY")

if not NASA_API_KEY:
    print("\nNASA_API_KEY not found in your environment.")
    try:
        NASA_API_KEY = input("Please enter your NASA API key: ").strip()
    except Exception:
        NASA_API_KEY = None

if not NASA_API_KEY:
    raise RuntimeError("No NASA API key provided. Exiting.")

# Optionally save it for next time
if HAS_DOTENV:
    env_path = ".env"
    try:
        set_key(env_path, "NASA_API_KEY", NASA_API_KEY)
        print(f"Saved NASA_API_KEY to {env_path}")
    except Exception:
        print("Failed to save API key to .env")
else:
    print("Install python-dotenv if you want to auto-save keys next time (pip install python-dotenv).")

IMPACT_FILE = "impacts.json"  # store user-simulated impacts


@app.route("/", methods=["GET"])
def index():
    """List all available API routes and their purpose."""
    routes = {
        "/": "API index - lists all routes and their purpose.",
        "/get_impacts": "GET historical + user-simulated impacts.",
        "/simulate_impact": "POST: Simulate an asteroid impact and save it.",
        "/nasa_asteroids": "GET: Fetch live asteroid data from NASA NEO API.",
        "/delete_impact/<id>": "DELETE: Remove a saved simulation by ID.",
    }
    return jsonify({
        "api_name": "Asteroid Impact Simulation API",
        "description": "Simulate asteroid impacts, view NASA asteroid data, and manage saved simulations.",
        "routes": routes,
    })


def load_impacts():
    if os.path.exists(IMPACT_FILE):
        with open(IMPACT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_impact(impact):
    impacts = load_impacts()
    impacts.append(impact)
    with open(IMPACT_FILE, "w", encoding="utf-8") as f:
        json.dump(impacts, f, indent=2)


HISTORICAL_IMPACTS = [
    {"id": "chicxulub", "name": "Chicxulub (66Mya)", "size": 10, "speed": 20, "lat": 21.4, "lon": -89.0},
    {"id": "tunguska", "name": "Tunguska (1908)", "size": 0.05, "speed": 16, "lat": 60.9, "lon": 101.9},
    {"id": "chelyabinsk", "name": "Chelyabinsk (2013)", "size": 0.02, "speed": 19, "lat": 54.9, "lon": 61.1},
]


@app.route("/get_impacts", methods=["GET"])
def get_impacts():
    """Return both historical and user-simulated impacts"""
    simulated = load_impacts()
    combined = HISTORICAL_IMPACTS + simulated
    return jsonify(combined)


def asteroid_kinetic_energy(diameter_m, velocity_km_s, density=3000):
    """Return kinetic energy in megatons for a spherical asteroid."""
    radius = diameter_m / 2.0
    volume = 4.0 / 3.0 * np.pi * radius ** 3
    mass = density * volume
    velocity = velocity_km_s * 1000.0
    energy_joules = 0.5 * mass * velocity ** 2
    return energy_joules / 4.184e15  # convert to megatons TNT


def impact_radius_km(megatons):
    # Very rough estimate: scales with cube root of energy
    return 1.5 * (megatons) ** (1.0 / 3.0) if megatons > 0 else 0.0


def population_affected(pop_density_per_km2, radius_km):
    area_km2 = np.pi * radius_km ** 2
    return int(area_km2 * pop_density_per_km2)


def impact_earthquake_magnitude(megatons):
    if megatons <= 0:
        return 0.0
    E_joules = megatons * 4.184e15
    magnitude = 0.67 * np.log10(E_joules) - 10.7
    return round(max(0.0, magnitude), 1)


@app.route("/nasa_asteroids", methods=["GET"])
def get_nasa_asteroids():
    """Fetches asteroid dataset from NASA NEO API"""
    if not NASA_API_KEY:
        return jsonify({"error": "NASA API key not configured"}), 400
    url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={NASA_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        asteroids = []
        for neo in data.get("near_earth_objects", []):
            est_diam = neo.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_max")
            if est_diam is None:
                est_diam = 0.0
            rel_vel = 20.0
            cad = neo.get("close_approach_data")
            if cad:
                try:
                    rel_vel = float(cad[0].get("relative_velocity", {}).get("kilometers_per_second", rel_vel))
                except Exception:
                    pass
            asteroids.append({
                "id": neo.get("id"),
                "name": neo.get("name"),
                "diameter_m": round(float(est_diam), 2),
                "velocity_km_s": round(float(rel_vel), 2),
                "hazardous": bool(neo.get("is_potentially_hazardous_asteroid", False)),
            })
        return jsonify({"count": len(asteroids), "asteroids": asteroids})
    except Exception as e:
        print("NASA API error:", e)
        return jsonify({"error": "Failed to fetch from NASA API"}), 500


@app.route("/simulate_impact", methods=["POST"])
def simulate_impact():
    data = request.get_json(silent=True) or {}
    diameter = float(data.get("diameter_m", 50.0))
    velocity = float(data.get("velocity_km_s", 20.0))
    lat = data.get("latitude", 0.0)
    lon = data.get("longitude", 0.0)
    pop_density = float(data.get("pop_density_per_km2", 1000.0))

    energy_mt = asteroid_kinetic_energy(diameter, velocity)
    radius_km = impact_radius_km(energy_mt)
    population = population_affected(pop_density, radius_km)
    earthquake_mag = impact_earthquake_magnitude(energy_mt)

    result = {
        "id": f"sim_{np.random.randint(10000,99999)}",
        "name": f"Simulated Impact ({round(float(lat),2)}, {round(float(lon),2)})",
        "latitude": lat,
        "longitude": lon,
        "diameter_m": diameter,
        "velocity_km_s": velocity,
        "energy_megatons": round(energy_mt, 2),
        "impact_radius_km": round(radius_km, 2),
        "population_affected": population,
        "earthquake_magnitude": earthquake_mag,
    }

    save_impact(result)
    return jsonify(result)


@app.route("/delete_impact/<impact_id>", methods=["DELETE"])
def delete_impact(impact_id):
    """Delete a saved simulation by ID"""
    impacts = load_impacts()
    new_impacts = [i for i in impacts if i.get("id") != impact_id]
    if len(new_impacts) == len(impacts):
        return jsonify({"error": "Impact not found"}), 404
    with open(IMPACT_FILE, "w", encoding="utf-8") as f:
        json.dump(new_impacts, f, indent=2)
    return jsonify({"message": f"Impact {impact_id} deleted"})


if __name__ == "__main__":
    app.run(debug=True)