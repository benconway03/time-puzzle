import pandas as pd
import random
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "history_secret_key" # Required for session storage

# Load the dataset globally
try:
    df = pd.read_csv('Historical Events 2.csv', encoding='latin1')
    # Clean up column names just in case
    df.columns = df.columns.str.strip()
except Exception as e:
    print(f"Error loading CSV: {e}")

@app.route('/')
def index():
    # Reset game state on refresh or new visit
    target_row = df.sample(n=1).iloc[0]
    session['target_event'] = target_row['Event']
    session['target_year'] = int(target_row['Year'])
    session['attempts'] = 0
    return render_template('index.html', events=df['Event'].tolist())

@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.json.get('guess', '').strip()
    match = df[df['Event'].str.lower() == user_guess.lower()]
    
    if match.empty:
        return jsonify({"error": "Event not found in database."}), 400

    session['attempts'] += 1
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