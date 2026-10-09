# SmartFood Grid AI — runnable demo

## Run in VS Code (Windows)
1. Extract the ZIP and open the `SmartFood_Grid_AI_Executed` folder in VS Code.
2. Select **Terminal → New Terminal**.
3. Run `py -m venv .venv`
4. Run `.\.venv\Scripts\Activate.ps1` (or use Command Prompt and run `.venv\Scripts\activate.bat`).
5. Run `python -m pip install -r requirements.txt`
6. Run `python app.py`
7. Open http://127.0.0.1:5000 in your browser.

Keep the terminal open. Press Ctrl+C to stop the server.

Features: add food listings, find nearby listings by coordinates/radius, mark partial/full rescue, and view dashboard statistics. Initial sample listings are in Hyderabad. This is a hackathon prototype, not a trained AI model or a food-safety verification system.
