# This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains a picture of Barack Obama.
# The result is returned as json. For example:
#
# $ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_picture_of_obama": true
# }
#
# This example is based on the Flask file upload example: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# NOTE: This example requires flask to be installed! You can install it with pip:
# $ pip3 install flask

import face_recognition
from flask import Flask, jsonify, request, redirect

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Is this a picture of Obama?</title>
    <h1>Upload a picture and see if it's a picture of Obama!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file_stream):
    # Pre-calculated face encoding of Obama generated with face_recognition.face_encodings(img)
    known_face_encoding = [-0.17165339,  0.14763767,  0.08349193, -0.03319434, -0.03074216,
       -0.05442678,  0.0141023 , -0.0896994 ,  0.1694102 , -0.11667049,
        0.23639323, -0.08861162, -0.20277153, -0.08206794,  0.00069661,
        0.1905003 , -0.20326646, -0.13727894, -0.03297636, -0.01996057,
        0.06634635, -0.0516543 , -0.01763321,  0.03707509, -0.10283119,
       -0.36979532, -0.10507199, -0.0825258 ,  0.02566614, -0.07506035,
       -0.04373353,  0.05107541, -0.20377067, -0.05800211, -0.05800483,
        0.08135618, -0.01214672, -0.01643079,  0.19689251, -0.00997648,
       -0.20775956,  0.0125386 , -0.00114008,  0.29659379,  0.14913695,
        0.04155755,  0.03006186, -0.08570188,  0.09821118, -0.12473544,
        0.05322195,  0.13854709,  0.11729003,  0.08998819, -0.05314345,
       -0.12281941,  0.04145799,  0.07545707, -0.14065436,  0.03430962,
        0.13876572, -0.13956814,  0.0091537 , -0.02375618,  0.28408626,
        0.03480123, -0.10625688, -0.15124322,  0.13018338, -0.08819306,
       -0.02923761,  0.03646172, -0.17589517, -0.16066793, -0.33713698,
        0.11262206,  0.40660083,  0.08046236, -0.14702784,  0.03913299,
       -0.12762196, -0.02006187,  0.12899914,  0.18714698, -0.04365598,
        0.00301594, -0.10514177,  0.03920277,  0.21227488, -0.04331422,
       -0.07487413,  0.15670036, -0.0035644 ,  0.07418029, -0.04368816,
       -0.02520423, -0.05489963,  0.05309147, -0.06463743,  0.02397378,
        0.01473818, -0.04750976, -0.05030409,  0.13764568, -0.16122742,
        0.13255273,  0.03520226,  0.06205078,  0.00132819,  0.06274346,
       -0.11362649, -0.11328004,  0.09330124, -0.23288581,  0.1884979 ,
        0.21568903,  0.05962493,  0.11587742,  0.10739607,  0.11180228,
        0.00956084,  0.03388467, -0.21723755,  0.0304551 ,  0.1588521 ,
        0.02394107,  0.11195635,  0.04917473]

    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    is_obama = False

    if len(unknown_face_encodings) > 0:
        face_found = True
        # See if the first face in the uploaded image matches the known face of Obama
        match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encodings[0])
        if match_results[0]:
            is_obama = True

    # Return the result as json
    result = {
        "face_found_in_image": face_found,
        "is_picture_of_obama": is_obama
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
