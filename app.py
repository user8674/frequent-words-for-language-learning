"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, request, session, redirect
import sqlite3
from data import *
from helpers import *


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
# Make the WSGI interface  available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

db = sqlite3.connect("databases/words.db")
cursor = db.cursor()
sql_command_get_hundred = "SELECT word FROM words WHERE rowid <= {} AND rowid > {}"
first_hundred = (cursor.execute("SELECT word FROM words WHERE rowid <= 100 AND rowid > 0")).fetchall()
first_six_hundred = (cursor.execute("SELECT word FROM words WHERE rowid <= 600 AND rowid > 0")).fetchall()
db.close()
preffered_lang = ""
@app.route('/', methods=["GET", "POST"])
def whats_your_main_language():
    global preferred_lang
    if request.method == "GET":
        return render_template("index.html", langs=langs)
    else:
        preferred_lang = request.form.get("lang")
        long_way = request.form.get("long_way")
        if long_way:
            return redirect("/phase_one_long")
        return redirect('/phase_one')

@app.route('/phase_one', methods=["GET", "POST"])
def what_level_are_you():
    global current_grade, form_no, starting_point
    starting_point = (6000 - current_grade * 600) + 1
    if request.method == "GET":
        return render_template("level_determination.html", hundred=first_hundred, level="E10")
    
    else:
        selected = request.form.getlist('checkbox')
        points = len(selected)
        print(selected)
        
        if points > 5 and current_grade != 0:
            form_no += 1
            current_grade -= 1
            
            if current_grade == 0:
                current_grade = 0.5
                return redirect("/phase_two")

            upper_limit = form_no * 600
            lower_limit = upper_limit - 100
            test_command = sql_command_get_hundred.format(upper_limit, lower_limit)
            db = sqlite3.connect("databases/words.db")
            cursor = db.cursor()
            this_hundred = cursor.execute(test_command).fetchall() 
            db.close()
            return render_template("level_determination.html", hundred=this_hundred, level=f"E{current_grade}")
        
        return redirect("/phase_two")
to_be_excluded = []
@app.route('/phase_one_long', methods=["GET", "POST"])
def test_word_knowledge():
    global current_grade, to_be_excluded, multiplier
    if request.method == "GET":     
        return render_template("knowledge_determination.html", level="E10", six_hundred=first_six_hundred, multiplier=multiplier)
    else:
        multiplier += 1
        current_grade -= 1
        if current_grade == 0:
            return redirect("phase_two")
        selected = request.form.getlist('checkbox')
        db = sqlite3.connect("databases/words.db")
        cursor = db.cursor()
        for i in selected:
            i = int(i) + 1
            to_be_excluded.append(cursor.execute("SELECT word FROM words WHERE id = ?", (i,)).fetchone()[0])
        this_six_hundred = cursor.execute(sql_command_get_hundred.format(multiplier * 600, multiplier * 600 - 600)).fetchall()
        db.close()
        return render_template("knowledge_determination.html", level=f"E{current_grade}", six_hundred=this_six_hundred, multiplier=multiplier)

        
        

@app.route('/phase_two', methods=["GET", "POST"])
def generate_decks():
    global current_grade
    if request.method == "GET":
        if current_grade == 0.5:
            current_grade = 0
        urls = generate_deck(starting_point, preferred_lang, [])
        return render_template("result.html", links=urls)

@app.route('/about')
def show_about():
    return render_template("about.html")


           
            
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)


