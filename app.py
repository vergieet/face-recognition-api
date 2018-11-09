import base64
import time

import cv2
import face_recognition
from flask import Flask, Response, request, jsonify,redirect
from werkzeug.utils import secure_filename
from PIL import Image
import pymysql

app = Flask(__name__)
#
# mysql = MySQL()
#
# # MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'apps'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'Apps*2013'
# app.config['MYSQL_DATABASE_DB'] = 'facerec_db'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)

class Database:
    def __init__(self):
        host = "localhost"
        user = "apps"
        password = "Apps*2013"
        db = "facerec_db"

        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def insert_person(self,name,nip,encoding,file):
        # print(encoding)
        encstr = ",".join(str(x) for x in encoding[0])
        # print(name+" "+nip+person_id+" "+encstr+" "+file)
        sql = "INSERT INTO person (name, nip) VALUES (%s, %s)"
        val = (name, nip)
        self.cur.execute(sql,val)
        sql = "INSERT INTO encoding (person_id,encoding, file) VALUES (%s, %s, %s)"
        val = (nip,encstr,file)
        self.cur.execute(sql, val)
        self.con.commit()

    def list_encodings(self):
        self.cur.execute("SELECT * FROM encoding")
        result = self.cur.fetchall()
        return result

    def get_person_by_nip(self,nip):
        self.cur.execute("SELECT * FROM person WHERE nip = %s LIMIT 1",(nip))
        result = self.cur.fetchone()
        return result

class Person:
    def __init__(self):
        name = ""
        nip = -1
        encodings = []



UPLOAD_FOLDER = 'data/'
EDITED_METHOD = False
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/check',methods=['OPTIONS','POST'])
def check():
    if request.method == 'POST':
        data = request.form
        convertImage(data["fileupload"].replace("data:image/png;base64,",""), time.strftime("%Y%m%d-%H%M%S") +".jpg")
        image = face_recognition.load_image_file("./data/13863742.jpg")
        face_landmarks_list = face_recognition.face_locations(image)
        imageFound = 0
        res = ""
        for face in face_landmarks_list:
            print(face)
            imageFound +=1
            # res += face
        resp = Response(response="{\"count\":" + imageFound.__str__() + "}", status=200, mimetype="application/json",headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000
        })
        return resp
    else:
        resp = Response(response="{\"test\":\"ok\"}", status=200, mimetype="application/json",headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000
        })
        return resp


@app.route('/api/upload',methods=['OPTIONS','POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'fileupload' not in request.files:
            return Response(response="{\"status\":false,\"message\":\"No file part\"}", status=200, mimetype="application/json",headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000
            })
        file = request.files['fileupload']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return Response(response="{\"status\":false,\"message\":\"No selected file\"}", status=200,
                            mimetype="application/json", headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Max-Age': 1000
                })
        if file and allowed_file(file.filename):
            if request.form['action'] == "enroll":
                filename = secure_filename(file.filename)
                savedname = cv2.os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(savedname)
                if(EDITED_METHOD):
                    editedname = cv2.os.path.join(app.config['UPLOAD_FOLDER'], "edited_" + filename)
                    im = Image.open("./data/" + filename)
                    # print(im.size)
                    crop_rectangle = (500, 500, 2000, 2000)
                    cropped_im = im.crop(crop_rectangle)
                    cropped_im.rotate(90).save(editedname)
                    datax = detect_faces_in_image(editedname)
                else:
                    datax = detect_faces_in_image(savedname)

                # cropped_im.rotate(90).show()
                return Response(response="{\"status\":true,\"message\":\"Scan Success!\",\"data\":{\"nip\":\"" + str(datax["nip"]) + "\",\"name\":\"" + datax["name"] + "\"}}", status=200,
                                mimetype="application/json", headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                        'Access-Control-Max-Age': 1000
                    })
        return Response(response="{\"status\":false,\"message\":\"File not allowed\"}", status=200, mimetype="application/json",headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000
        })
    else:
        return Response(response="{\"status\":false,\"message\":\"Method Not Allowed\"}", status=200, mimetype="application/json",headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000
        })

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        data = request.form

        file = request.files['file']
        filename = secure_filename(file.filename)
        savedfilename = cv2.os.path.join(app.config['UPLOAD_FOLDER'], "enrollment/",filename);
        editedfilename = cv2.os.path.join(app.config['UPLOAD_FOLDER'], "enrollment/","edited_"+filename);
        file.save(savedfilename)

        if (EDITED_METHOD):
            im = Image.open(savedfilename)
            crop_rectangle = (500, 500, 2000, 2000)
            cropped_im = im.crop(crop_rectangle)
            cropped_im.rotate(90).save(editedfilename)
            imgx = face_recognition.load_image_file(editedfilename);
        else:
            imgx = face_recognition.load_image_file(savedfilename);

        faceenc = face_recognition.face_encodings(imgx)
        if len(faceenc) > 0:
            db = Database()
            db.insert_person(data["name"],data["nip"],faceenc,filename)
            return jsonify({
                "message": "insert success",
            })
        else:
            return jsonify({
                "message": "face not found",
            })
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>FACE REC ENROLLMENT</title>
    <h1>ENROLLMENT FORM!</h1>
    <form method="POST" enctype="multipart/form-data">
      Name:<input type="text" name="name"><br/>
      NIP:<input type="text" name="nip"><br/>
      Image:<input type="file" name="file"><br/>
      <input type="submit" value="Upload">
    </form>
    '''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convertImage(imgstring,filename):
    imgdata = base64.b64decode(imgstring)
    filename = './data/' + filename
    with open(filename, 'wb') as f:
        f.write(imgdata)



def detect_faces_in_image(file_stream):
    # Pre-calculated face encoding of Obama generated with face_recognition.face_encodings(img)
    # db = Database()
    # encodingList = []
    # for row in db.list_encodings():
    #     encodingList.append(row["encoding"].split(","))

    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    nip = -1

    if len(unknown_face_encodings) > 0:
        face_found = True
        db = Database()
        for row in db.list_encodings():
            print(list(map(float,row["encoding"].split(","))))
            match_results = face_recognition.compare_faces([list(map(float,row["encoding"].split(",")))], unknown_face_encodings[0])
            if match_results[0]:
                nip = row["person_id"]
        # See if the first face in the uploaded image matches the known face of Obama
    name = "unknown"
    if(nip != -1):
        db = Database()
        name = db.get_person_by_nip(nip)["name"]

    # Return the result as json
    result = {
        "face_found": face_found,
        "nip": nip,
        "name": name,
    }
    return result


if __name__ == '__main__':
    app.run()

#
# import face_recognition
# known_image = face_recognition.load_image_file("biden.jpg")
# unknown_image = face_recognition.load_image_file("unknown.jpg")
#
# biden_encoding = face_recognition.face_encodings(known_image)[0]
# unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
#
# results = face_recognition.compare_faces([biden_encoding], unknown_encoding)