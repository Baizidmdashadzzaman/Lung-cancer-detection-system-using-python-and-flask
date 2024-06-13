import pickle
import numpy as np
import os
import sys
import datetime
import cv2
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer.yml')
cascadePath = "cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX
id = 0
names = ['None','Asad','Zaman']

from flask import Flask, render_template, request, redirect, url_for, session, flash, app, jsonify,Response

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)


app.secret_key = 'supersecretkey'

classifier = pickle.load(open('model.pkl', 'rb'))

# image processing face recognization start
redirect_flag = False

def capture_by_frames(): 
    global cam,redirect_flag
    cam = cv2.VideoCapture(0)
    while True:
        ret, img =cam.read()
        img = cv2.flip(img, 1) # 1 Stright 0 Reverse
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        detector=cv2.CascadeClassifier(cascadePath)
        faces=detector.detectMultiScale(img,1.2,6)
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])           
            if (confidence < 100):
                id = names[id]
                confidence_raw = int("  {0}".format(round(100 - confidence)))
                confidence = "  {0}%".format(round(100 - confidence))
                
                if confidence_raw > 50:
                    redirect_flag = True
                else:
                    redirect_flag = False
            else:
                id = "Unknown"
                confidence = "  {0}%".format(round(100 - confidence))
            cv2.putText(img,str(id),(x+5,y-5),font,1,(255,255,255),2)
            #cv2.putText(img,str(confidence),(x+5,y+h),font,1,(255,255,0),1)
        ret1, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/face-scan')
def facescanlogin():
    user = session.get('user')
    if user:
        flash('Already logged in', 'success')
        return redirect(url_for('patientdashboard'))
    
    title = "Scan your face"
    return render_template('facescan/index.html',title=title)

@app.route('/scan-video-capture')
def scan_video_capture():
    return Response(capture_by_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check-redirect-after-face-scan')
def check_redirect_after_face_scan():
    global redirect_flag
    if redirect_flag:
         session['user'] = '01846200413'
    return jsonify({'redirect': redirect_flag})

# image processing face recognization start


# crud start
def convert_to_dict(cur, row):
    if cur.description:
        return dict((cur.description[idx][0], value) for idx, value in enumerate(row))
    return {}

@app.route('/patients')
def patients_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients")
    rows = cur.fetchall()
    patients_list = [convert_to_dict(cur, row) for row in rows]
    cur.close()
    title="Patients list"
    return render_template('admin/patients/list.html', patients=patients_list,title=title)

@app.route('/patients/add', methods=['GET', 'POST'])
def patients_add():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        isadmin = 0
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (username,email,password,isadmin) VALUES (%s,%s,%s,%s)", (username,email,password,isadmin))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('patients_list'))
    title="Add new patient"
    return render_template('admin/patients/add.html',title=title)

@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def patients_edit(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        isadmin = 0
        cur.execute("UPDATE patients SET username = %s, email = %s, password = %s, isadmin = %s WHERE id = %s", 
                    (username, email, password, isadmin, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('patients_list'))

    cur.execute("SELECT * FROM patients WHERE id = %s", (id,))
    row = cur.fetchone()
    patient = convert_to_dict(cur, row)
    cur.close()
    title="Edit patient information"
    return render_template('admin/patients/edit.html', patient=patient)

@app.route('/patients/delete/<int:id>')
def patients_delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM patients WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('patients_list'))
# crud end



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
    redirect_flag = False
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
    # app.run()
    app.run(debug=True)
    #app.run(debug=True,use_reloader=False, port=8000)
