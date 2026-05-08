import os
import pandas as pd
import random
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "history_secret_key"

# Force absolute path resolution (Bulletproof for Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, 'hist_events.csv')

df = None
startup_error = ""

try:
    if not os.path.exists(FILE_PATH):
        # If missing, grab a list of files actually present in the folder
        files_in_dir = ", ".join(os.listdir(BASE_DIR))
        startup_error = f"Missing File! Looked for '{FILE_PATH}'. Files actually present: {files_in_dir}"
    else:
        df = pd.read_csv(FILE_PATH, encoding='latin1')
        df.columns = df.columns.str.strip()
except Exception as e:
    startup_error = f"Error reading CSV: {str(e)}"

@app.route('/')
def index():
    # If the dataframe failed to load, show the error safely on the screen
    if df is None:
        return f"<h1>Deployment Error</h1><p>{startup_error}</p>"

    # Pick a new target and store its details in the session
    target_row = df.sample(n=1).iloc[0]
    session['target_event'] = target_row['Event']
    session['target_year'] = int(target_row['Year'])
    session['target_region'] = target_row['Region']
    session['target_category'] = target_row['Category']
    session['attempts'] = 0
    return render_template('index.html', events=df['Event'].tolist())

@app.route('/guess', methods=['POST'])
def guess():
    if df is None:
        return jsonify({"error": "System offline due to data missing."}), 500
        
    user_guess = request.json.get('guess', '').strip()
    
    # Check for hint command
    if user_guess.lower() == 'hint':
        return jsonify({
            "result": "hint",
            "region": session.get('target_region'),
            "category": session.get('target_category'),
            "attempts": session.get('attempts', 0)
        })

    match = df[df['Event'].str.lower() == user_guess.lower()]
    
    if match.empty:
        return jsonify({"error": "Event not found in database. Check spelling or use the dropdown."}), 400

    session['attempts'] = session.get('attempts', 0) + 1
    guess_row = match.iloc[0]
    guess_year = int(guess_row['Year'])
    target_year = session['target_year']
    
    if guess_year == target_year:
        return jsonify({
            "result": "correct",
            "message": f"Correct! It was {session['target_event']}.",
            "display_year": guess_row['Display Year'],
            "attempts": session['attempts']
        })
    
    direction = "BEFORE" if target_year < guess_year else "AFTER"
    return jsonify({
        "result": "incorrect",
        "direction": direction,
        "guess_name": guess_row['Event'],
        "guess_year": guess_row['Display Year'],
        "attempts": session['attempts']
    })

if __name__ == '__main__':
    app.run(debug=True)