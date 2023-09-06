import functools
import random
import sys

import requests
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, make_response

from .utils.database.database import database
import nfl_data_py as nfl
import os
import csv
import json

db = database()
pass_dic = {}
rush_dic = {}
rec_dic = {}






def process_csv_by_name_and_position(csv_file, player_name):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name_category = row['NAME']
            name_words = player_name.split(' ')[:2]
            if ' '.join(name_words) == name_category:
                return row

    return None


def append_non_numeric_part(string):
    non_numeric_part = ""
    for char in string:
        if not char.isdigit():
            non_numeric_part += char
    return non_numeric_part


def getPlayers():
    players = []
    with open('./flask_app/database/initial_data/StandardRankings.csv', 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            players.append([row[2], row[3], append_non_numeric_part(row[4])])

    players.pop(0)
    players.sort()
    return players


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)

    return secure_function


def getUser():
    return session['email'] if 'email' in session else 'Unknown'


@app.route('/login')
def login():
    return render_template('login.html', user=getUser(), msg='None')


@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/')


# Function to load the list from a file
def load_list_from_file():
    try:
        with open('my_list.txt', 'r') as file:
            return file.read().split(',')
    except FileNotFoundError:
        return []


# Function to save the list to a file
def save_list_to_file(my_list):
    with open('my_list.txt', 'w') as file:
        file.write(','.join(my_list))


@app.route('/processAdd', methods=["POST", "GET"])
@login_required
def processAdd():

    playerOwned = False
    p = request.form.get("select-player")

    # pass_dic = {}
    # rush_dic = {}
    # rec_dic = {}


    x = db.query("Select * From transactions Where user_id = '" + getUser() + "' and player_id = '" + p + "'")
    if not x:  # then we add the player

        # get the pass stats
        # get the rush stats
        # get the rec

        pass_file = './flask_app/database/initial_data/PassingStats.csv'
        words = p.split()
        first_two_words = words[:2]
        first_last = ' '.join(first_two_words)

        passing = process_csv_by_name_and_position(pass_file, first_last)

        rush_file = './flask_app/database/initial_data/RushingStats.csv'
        rushing = process_csv_by_name_and_position(rush_file, first_last)

        rec_file = './flask_app/database/initial_data/ReceivingStats.csv'
        rec = process_csv_by_name_and_position(rec_file, first_last)

        print("PLAYER IS: ")
        print(p)
        print(type(p))
        print("_______ PASSING BELOW __________")
        print(passing)
        print("_______ RUSHING BELOW __________")
        print(rushing)
        print("_______ RECEIVING BELOW __________")
        print(rec)

        pass_str = " "
        rush_str = " "
        rec_str = " "

        if passing is not None:
            print("_______ PASSING2 BELOW __________")
            for k, v in passing.items():
                print(k, v)

                if k != "NAME" and k != "POS" and k != "TEAM":
                    pass_str += v
                    pass_str += " "

                    pass_dic[k] = v

        if rushing is not None:
            print("_______ RUSHING2 BELOW __________")
            for k, v in rushing.items():
                print(k, v)

                if k != "NAME" and k != "POS" and k != "TEAM":
                    rush_str += v
                    rush_str += " "

                    rush_dic[k] = v

            for k, v in rush_dic.items():
                print(k, v)

        if rec is not None:
            print("_______ RECEIVING2 BELOW __________")
            for k, v in rec.items():
                print(k, v)

                if k != "NAME" and k != "POS" and k != "TEAM":
                    rec_str += v
                    rec_str += " "

                    rec_dic[k] = v

            for k, v in rec_dic.items():
                print(k, v)

        db.insertTransaction('transaction_table', parameters=[[getUser(), p, pass_str, rush_str, rec_str]])


        json_pass = json.dumps(pass_dic)
        json_rush = json.dumps(rush_dic)
        json_rec = json.dumps(rec_dic)

        print("PASS INFO", '\n')
        print(json_pass)
        print('\n')
        print("RUSH INFO", '\n')
        print(json_rush)
        print('\n')
        print("REC INFO", '\n')
        print(json_rec)
        print('\n')


        db.insertTest('transaction_table', parameters=[[getUser(), p, json_pass, json_rush, json_rec]])
    else:
        playerOwned = True





    updatedLst = db.query("Select * From transactions Where user_id = '" + getUser() + "' ")

    print("UPDATED LST")

    print(updatedLst)
    print('\n')
    print("END OF LST")

    test_lst = db.query("Select * From test Where user_id = '" + getUser() + "' ")
    print("TESTING LST")

    print(test_lst)
    print('\n')
    print("END OF LST")

    return render_template('home.html', user=getUser(), players=getPlayers(), numPicks=488, playerLst=updatedLst, own=playerOwned, rec_dic=rec_dic, rush_dic=rush_dic, pass_dic=pass_dic, testing=test_lst)


@app.route('/processlogin', methods=["POST", "GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    res = db.authenticate(form_fields['email'], db.onewayEncrypt(form_fields['password']))

    if res["success"] == -1:  # if we fail stay on login page
        return render_template('login.html', user=getUser(), msg='Fail')
    else:
        session['email'] = form_fields['email']
        session['password'] = form_fields['password']

        PL = db.query("Select * From transactions Where user_id = '" + getUser() + "' ")

        return render_template('home.html', user=getUser(), players=getPlayers(), numPicks=488, playerLst=PL, own=False, rec_dic={}, rush_dic={}, pass_dic={})


@app.route('/processSignup', methods=["POST", "GET"])
def processSignup():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    user_table = db.query("SELECT * FROM users")

    for item in user_table:

        if item["email"] == form_fields['email']:
            return render_template('signup.html', account='Fail', user='Unknown', accountUser=form_fields['email'])

    db.createUser(email=form_fields['email'], password=form_fields['password'], role='guest', tokens=100)

    return render_template('signup.html', account='Success', user='Unknown', accountUser=form_fields['email'])


#######################################################################################
# OTHER
#######################################################################################


@app.route('/signup')
def signup():
    return render_template('signup.html', user=getUser(), account='False')


@app.route('/')
def root():
    return redirect('/home')


@app.route('/team')
def team():

    PL = db.query("Select * From transactions Where user_id = '" + getUser() + "' ")

    trans = db.query("Select * From test Where user_id = '" + getUser() + "' ")

    player_rush = {}
    player_rec = {}
    player_pass = {}

    stats_dic = {}

    for player in trans:  # the transaction lst that represent each player of the team

        # Rushing related stats to player

        rsh_str = player['rush']

        rsh_dic = json.loads(rsh_str)  # string to dic

        player_rush[player['player_id']] = rsh_dic


        # Receiving related stats to player

        rc_str = player['rec']

        rc_dic = json.loads(rc_str)

        player_rec[player['player_id']] = rc_dic


        # Passing related stats to player

        ps_str = player['pass']

        ps_dic = json.loads(ps_str)

        player_pass[player['player_id']] = ps_dic


        # connect all stats in one dic

        stats_dic[player['player_id']] = [rsh_dic, rc_dic, ps_dic]

    return render_template('team.html', user=getUser(), playerLst=PL, lst=trans, player_pass=player_pass, player_rush=player_rush, player_rec=player_rec, stats_dic=stats_dic)


@app.route('/home')
def home():

    PL = db.query("Select * From transactions Where user_id = '" + getUser() + "' ")

    return render_template('home.html', user=getUser(), players=getPlayers(), numPicks=488, playerLst=PL, own=False, rec_dic={}, rush_dic={}, pass_dic={})


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r



@app.route('/schedule')
def schedule():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

    r = requests.get(url)
    d = r.json()

    count = 0

    myLst = []
    tstLst = []
    for key, val in d.items():

        if key == "events":

            tstLst.append({key: val})

            for event in val:

                myLst.append([])
                logo_count = 0

                for key2, val2 in event.items():

                    if key2 == "competitions":

                        for item in val2:

                            for k3, v3 in item.items():

                                if k3 == "odds":

                                    for item2 in v3:

                                        for k4, v4 in item2.items():

                                            if k4 != "provider":
                                                myLst[count].append({k4: v4})

                                elif k3 == "competitors":

                                    for i2 in v3:

                                        for k4, v4 in i2.items():

                                            if k4 == "team":

                                                for k5, v5 in v4.items():

                                                    if k5 == "logo":

                                                        if logo_count % 2 == 0:
                                                            myLst[count].append({"homeLogo": v5})
                                                        else:
                                                            myLst[count].append({"awayLogo": v5})

                                                        logo_count += 1

                    elif key2 == "status":

                        for k3, v3 in val2.items():

                            if k3 == "type":

                                for k4, v4 in v3.items():

                                    if k4 == "shortDetail":
                                        myLst[count].append({"time": v4})


                    elif key2 == "shortName":

                        myLst[count].append({"away": val2[0:3]})
                        myLst[count].append({"home": val2[-3:]})


                    elif key2 != "id" and key2 != "uid" and key2 != "date" and key2 != "season" and key2 != "links" \
                            and key2 != "name" and key2 != "week" and key2 != "link":
                        myLst[count].append({key2: val2})


                count += 1

    sorted_data = []

    for game in myLst:

        try:
            sorted_game = [
                {'matchUp': [game[3]['awayLogo'], game[0]['away'], game[2]['homeLogo'], game[1]['home']]},  # Home team
                {'time': game[6]['time']},  # Time
                {'spread': game[4]['details']},  # Details
                {'overUnder': game[5]['overUnder']}  # Over/Under
            ]
        except KeyError:
            sorted_game = [
                {'matchUp': [game[3]['awayLogo'], game[0]['away'], game[2]['homeLogo'], game[1]['home']]},  # Home team
                {'time': game[7]['time']},  # Time
                {'spread': game[4]['details']},  # Details
                {'overUnder': game[5]['overUnder']}  # Over/Under
            ]
        # sorted_data.append(sorted_game)
        # except KeyError:  # different format for pre season games
        #     sorted_game = [
        #         {'matchUp': [game[3]['awayLogo'], game[0]['away'], game[2]['homeLogo'], game[1]['home']]},  # Home team
        #         {'time': "Final"},  # Time
        #         {'spread': "N/A"},  # Details
        #         {'overUnder': "N/A"}  # Over/Under
        #     ]
        #     sorted_data.append(sorted_game)
        # except IndexError:  # different format for pre season games
        #     sorted_game = [
        #         {'matchUp': [game[3]['awayLogo'], game[0]['away'], game[2]['homeLogo'], game[1]['home']]},  # Home team
        #         {'time': game[4]['time']},  # Time
        #         {'spread': "N/A"},  # Details
        #         {'overUnder': "N/A"}  # Over/Under
        #     ]
        sorted_data.append(sorted_game)



    return render_template('schedule.html', user=getUser(), lst=sorted_data)
