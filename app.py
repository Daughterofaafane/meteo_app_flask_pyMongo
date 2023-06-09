from flask import Flask,request, render_template, send_file
from flask_pymongo import PyMongo
import json
from bson.json_util import dumps
from datetime import datetime, timedelta
import requests
import pymongo
import numpy as np
import matplotlib.pyplot as plt
import pymongo

API="https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&facet=date&facet=nom&facet=temps_present&facet=libgeo&facet=nom_epci&facet=nom_dept&facet=nom_reg"

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/database"

mongo = PyMongo(app)




@app.route("/")
def home_page():
    home = mongo.db.apitry.distinct("nom")
    return render_template("index.html", home=home)


@app.route('/search', methods=["POST"])
def search():
    global name, date, station
    if request.method == "POST":
        name = request.form.get("seach")
        date = request.form.get("datei")
    station = mongo.db.apitry.find({"nom": name, "date":{"$regex": date}})
    stat = mongo.db.apitry.count_documents({"nom": name, "date":{"$regex": date}})

    #-------------------UPDATE DATA FROM API----------------------
    lastday1 = mongo.db.apitry.find({},{"_id":0, "date":1}).sort("date",-1).limit(1)

    now=datetime.now()
    for i in lastday1:
        lastday2 = i["date"]
        lastdayy = lastday2.split("+").pop(0)
        # print(lastdayy)
        lastday = datetime.strptime(lastdayy, '%Y-%m-%dT%H:%M:%S')
        
        print(lastday.date())
        print(now.date())
        # print(now.date()-lastday.date())

    if now.date() > lastday.date():
        print("yes")
        num = now.date()-lastday.date()
        print(num.days)
        b = int(num.days)
        list=[]
        count=1
        for i in range(1,b):
            a=lastday.date()+timedelta(days=i)
            param={"refine.date": a, "rows":10000}
            response = requests.get(API, params=param)
            print(response.json())
            response=response.json()["records"]
            for record in response:
                obj=["nom", "date", "tc", "u", "ff", "temps_present", "pres"]
                dict={}
                for i in obj:
                    if i in record["fields"]:
                        dict[i] = record["fields"][i]
                    else:
                        dict[i]=""
                print(dict)        
                list.append(dict)
            print(count)
            count += 1
        print(list)
    if len(list) != 0:
        mongo.db.apitry.insert_many(list)
        print("Done")


    if stat != 0:
        return render_template("aftrsearch.html", station=station)
    else:
        return render_template("index.html")   







@app.route('/download')
def download():
    datee = str(date)
    station = mongo.db.apitry.find({"nom": name, "date":{"$regex": datee}})
    stat=list(station)
    # print(stat)
    txt=dumps(stat, sort_keys=True, indent=4)
    path = 'file.json'
    with open(path, "w") as f:
        f.write(txt)

    return send_file(path, as_attachment=True)
        





@app.route('/graphs')
def graph():
    datee = str(date)
    x = mongo.db.apitry.find({"nom": name, "date":{"$regex": datee}})
    print(x)
    days = []
    temps = []
    for i in x:
        # print(i["date"])
        day = i["date"].split("T").pop(1).split("+").pop(0)
        print(day)
        temp = round(i["tc"],2)
        print(temp)
        days.append(day)
        temps.append(temp)
    courses = days
    values = temps
    # plt.bar(courses, values, color ='red', width = 0.4)
    plt.switch_backend("agg")
    plt.plot(courses, values, "r-o", label="Température(C°)", linewidth=2)
    plt.legend()
    plt.xlabel("Heures")
    plt.ylabel("Température(C°)")
    plt.title(datee)
    # plt.show()
    plt.savefig('static/images/new_plot.png')
    return render_template('graphs.html', name = name, url ='/static/images/new_plot.png')














if __name__ == '__main__':
    app.run(debug=True)
