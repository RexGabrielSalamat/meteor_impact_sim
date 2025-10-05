How to use the website: Meteor Impact-Sim

PLEASE NOTE THAT THIS IS A PROTOTYPE MODEL...

NOTE: You need the to have four files downloaded in the same file folder, with the same file name. BEFORE PROCEEDING - Please download the latest Python version on Microsoft Store, then run the terminal tab "pip install requests flask flask-cors numpy". Once all of it is running, you need to generate your own API from NASA API to access API key provided, then simply run the code.

*Note: The app.py only extracts from the NASA API dataset within the range of 7 days.

Used in Python terminal: Step by step to download the following packages:
- pip install requests
- m pip install flask
- pip install python-dotenv
- m pip install flask-cors
- m pip install numpy

--------------------------------------------------------------

Overview:
- Interactive 3D asteroid impact simulation on Earth.
- Backend calculates impact energy, radius, population affected, and earthquake magnitude.
- Frontend visualizes Earth, meteors, and orbiting asteroids in real-time with Three.js.

Features:
- Launch meteors by clicking on Earth.
- Pause, reset, analyze impacts, and switch camera POV (Earth or asteroid).
- Load datasets: historical impacts, NASA NEOs, or saved simulations.
- Realistic effects: flashes, shockwaves, particles, craters, and camera shake.

Setup:
- Backend: pip install flask flask-cors numpy requests, then python app.py.
- Frontend: Open index.html in a browser; it connects to the backend automatically.

Usage:
- Adjust meteor size, speed, and distance via sliders.
- Spawn meteors or run dataset impacts.
- View real-time impact analysis in the interface.

--------------------------------------------------------------

This project is a 3D Asteroid Impact Simulation combining a Python backend and a browser-based frontend.

Backend (Flask API)
- Purpose: Handles data storage, impact calculations, and NASA asteroid data fetching.

Key Endpoints:
/get_impacts → Returns historical and user-simulated impacts.
/simulate_impact → Accepts meteor size, speed, and location, calculates impact effects, and saves the simulation.
/nasa_asteroids → Fetches live asteroid data from NASA’s NEO API.
/delete_impact/<id> → Deletes a saved simulation by ID.

- Calculations: Kinetic energy, impact radius, population affected, earthquake magnitude.
- Storage: Saves user simulations in impacts.json.

To run:
- Install Python and required packages (flask, flask-cors, requests, numpy).
- Start the server with python app.py.
- Frontend fetches data from the API to visualize impacts.

--------------------------------------------------------------

Frontend (3D Earth Simulation)

Purpose: Provides interactive 3D visualization of Earth, meteors, and orbiting asteroids using Three.js.

Controls & Buttons:
- Pause / Resume → Stops or resumes meteor animation.
- Reset → Clears meteors, orbiting asteroids, craters, and resets camera & UI.
- Analyze Impact → Sends a user-defined meteor to backend for impact analysis.
- Asteroid POV / Earth POV → Switches camera between meteor and Earth view.
- Rerun Saved Impact → Replays a saved meteor simulation.
- Dataset Tab → Loads historical, NASA, or saved impacts and launches meteors from selected data.
- Visual Effects: Meteors, flashes, shockwaves, explosion particles, craters, and camera shake.
- Interaction: Clicking on Earth spawns meteors at the clicked location.
- Backend Integration: Sends meteor parameters to backend to compute energy, radius, population affected, and earthquake magnitude.

To run:
- Open the HTML file in a modern browser.
- Ensure the Flask backend is running.
- Use controls to simulate meteors, analyze impacts, and explore datasets.
