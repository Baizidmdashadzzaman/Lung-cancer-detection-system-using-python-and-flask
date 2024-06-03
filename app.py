import pickle
import numpy as np
import pandas as pd
import os
import sys
import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, app, jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'

classifier = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():

    title = "Home"
    return render_template('index.html',title=title)
@app.route('/about')
def about():
    title = "About"
    return render_template('index.html',title=title)

@app.route('/patient-login', methods=['GET', 'POST'])
def patientlogin():
    user = session.get('user')
    if user:
        flash('Already logged in', 'success')
        return redirect(url_for('patientdashboard'))

    title = "Patient login"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '01846200413' and password == 'password':
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('patientdashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('patient/login.html',title=title)


@app.route('/patient-dashboard')
def patientdashboard():
    user = session.get('user')
    if user is None:
        flash('You are not logged in,please login.', 'success')
        return redirect(url_for('patientlogin'))

    title = "Patient dashboard"
    return render_template('patient/dashboard.html',title=title)

@app.route('/if-you-dont-have-lung-cancer')
def ifyoudonthavelungcancer():
    user = session.get('user')
    if user is None:
        flash('You are not logged in,please login.', 'success')
        return redirect(url_for('patientlogin'))

    title = "If you dont have lung cancer"
    return render_template('patient/if-you-dont-have-lung-cancer.html',title=title)

@app.route('/if-you-have-lung-cancer')
def ifyouhavelungcancer():
    user = session.get('user')
    if user is None:
        flash('You are not logged in,please login.', 'success')
        return redirect(url_for('patientlogin'))

    title = "If you have lung cancer"
    return render_template('patient/if-you-have-lung-cancer.html',title=title)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))



@app.route('/predict', methods=['POST'])
def predict():
    age = request.form['age']
    gender = request.form['gender']
    air_pollution = request.form['air_pollution']
    alcohol_use = request.form['alcohol_use']
    dust_allergy = request.form['dust_allergy']
    occupational_hazards = request.form['occupational_hazards']
    genetic_risk = request.form['genetic_risk']
    chronic_lung_disease = request.form['chronic_lung_disease']
    balanced_diet = request.form['balanced_diet']
    obesity = request.form['obesity']
    smoking = request.form['smoking']
    passive_smoker = request.form['passive_smoker']
    chest_pain = request.form['chest_pain']
    coughing_of_blood = request.form['coughing_of_blood']
    fatigue = request.form['fatigue']
    weight_loss = request.form['weight_loss']
    shortness_of_breath = request.form['shortness_of_breath']
    wheezing = request.form['wheezing']
    swallowing_difficulty = request.form['swallowing_difficulty']
    clubbing_of_finger_nails = request.form['clubbing_of_finger_nails']
    frequent_cold = request.form['frequent_cold']
    dry_cough = request.form['dry_cough']
    snoring = request.form['snoring']

    prediction = classifier.predict([[age, gender, air_pollution, alcohol_use, dust_allergy, occupational_hazards, genetic_risk, chronic_lung_disease, balanced_diet, obesity, smoking, passive_smoker, chest_pain, coughing_of_blood, fatigue, weight_loss, shortness_of_breath, wheezing, swallowing_difficulty, clubbing_of_finger_nails, frequent_cold, dry_cough, snoring]])

    if(prediction == [1]):
        prediction_result = "কম ঝুঁকি"
    elif(prediction == [2]):   
        prediction_result = "মাঝারি ঝুঁকি"
    else:  
        prediction_result = "উচ্চ ঝুঁকি"  

    # print(prediction_result)
    # sys.exit()
    current_date = datetime.date.today()
    title = f"({prediction_result}) Patient test result"
    return render_template(
        'patient/patient-test-result.html',
        title=title,
        prediction=prediction,
        prediction_result=prediction_result,
        age=age,
        gender=gender,
        air_pollution=air_pollution,
        alcohol_use=alcohol_use,
        dust_allergy=dust_allergy,
        occupational_hazards=occupational_hazards,
        genetic_risk=genetic_risk,
        chronic_lung_disease=chronic_lung_disease,
        balanced_diet=balanced_diet,
        obesity=obesity,
        smoking=smoking,
        passive_smoker=passive_smoker,
        chest_pain=chest_pain,
        coughing_of_blood=coughing_of_blood,
        fatigue=fatigue,
        weight_loss=weight_loss,
        shortness_of_breath=shortness_of_breath,
        wheezing=wheezing,
        swallowing_difficulty=swallowing_difficulty,
        clubbing_of_finger_nails=clubbing_of_finger_nails,
        frequent_cold=frequent_cold,
        dry_cough=dry_cough,
        snoring=snoring,
        current_date=current_date
    )



if __name__ == '__main__':
    app.run()
