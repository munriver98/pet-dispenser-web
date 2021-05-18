from flask import Flask, request
from flask import render_template
import requests
import json

app = Flask(__name__)

raspi_endpoint = "http://192.168.0.98:9100/api" # Set RaspberryPI IP

@app.route('/')
def index():
    try:
        meal_times = get_meal_times()
        avg_weight = calc_avg(meal_times)

        chart_lables = []
        chart_datas = []
        for meal_time in meal_times:
            chart_lables.append(f'{meal_time["date"]} {meal_time["time"]}')
            chart_datas.append(meal_time["weight"])
        chart_datastr = ",".join(str(i) for i in chart_datas)

        schedules = get_schedules()

        param_dict = dict()
        param_dict["chart_datastr"] = chart_datastr
        param_dict["chart_lables"] = chart_lables
        param_dict["avg_weight"] = avg_weight
        param_dict["schedules"] = schedules
       

    except Exception as e:
        print('Error occured.', e)
        return render_template('error.html')

    return render_template('index.html', params=param_dict)

@app.route('/feed/<type>' ,methods=['POST'])
def feed_now(type):
    try:
        response = requests.get(f'{raspi_endpoint}/feed/{type}')
        if response.status_code != 200:
            raise Exception
    except Exception as e:
        print('Error occured.', e)
        return {},400
    return response.json(),200    

@app.route('/saveSchedule' ,methods=['POST'])
def save_schedule():
    try:
        type = request.form["type"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        print(f'{type}{start_time}')

        response = requests.get(f'{raspi_endpoint}/setting/mealtime/{type}/{start_time}-{end_time}')
        if response.status_code != 200:
            raise Exception
    except Exception as e:
        print('Error occured.', e)
        return {},400
    return response.json(),200

def get_meal_times():
    response = requests.get(f'{raspi_endpoint}/mealdata/21')
    meal_times = response.json()

    meal_times = sorted(meal_times, key=(lambda x: (x['date'],x['time'])) )
    return meal_times

def calc_avg(meal_times):
    total_meal_weight = 0
    for meal_time in meal_times:
        total_meal_weight += int(meal_time["weight"])

    avg_weight = round(total_meal_weight / len(meal_times),1)
    return avg_weight

def get_schedules():
    response = requests.get(f'{raspi_endpoint}/setting/mealtime')
    schedules = response.json()
    return schedules

if __name__ == '__main__':
 app.run(host='0.0.0.0', port="8080")