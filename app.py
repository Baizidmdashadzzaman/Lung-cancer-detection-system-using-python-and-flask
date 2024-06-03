import pickle
import numpy as np
import pandas as pd
import os
import sys

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


@app.route('/predict_api', methods=['POST'])
def predict_api():
    data = request.json['data']
    print(data)
    print(np.array(list(data.values())).reshape(1, -1))
    new_data = scalar.transform(np.array(list(data.values())).reshape(1, -1))
    output = regmodel.predict(new_data)
    print(output[0])
    return jsonify(output[0])


@app.route('/predict', methods=['POST'])
def predict():
    # data = [float(x) for x in request.form.values()]
    # final_input = np.array(data).reshape(1, -1)
    print(request.form['level'])
    sys.exit()
    # output = regmodel.predict(final_input)[0]
    # return render_template("home.html",
    # prediction_text=f"The House Price Prediction is {output} hundreds of thousands of dollars")
    title = "If you dont have lung cancer"
    return render_template('patient/dashboard.html',title=title)



if __name__ == '__main__':
    app.run()
