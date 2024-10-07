from flask import Flask, render_template, request, send_from_directory, redirect, url_for, after_this_request
from werkzeug.utils import secure_filename
import os
from ultralytics import YOLO
import yolov8_segmentation as seg
import shutil



model = YOLO("yolov8x-seg.pt")

app = Flask(__name__)

upload_folder = os.path.join("static", 'uploads')
 
app.config['UPLOAD'] = upload_folder
app.config['BGFOLDER'] = os.path.join("static", "bgremoved")
app.config['CACHE'] = os.path.join("static", "bgremoved", "cache")

bgremoverpage = "/"
 
@app.route(bgremoverpage, methods=['GET', 'POST'])
def upload_file():
    
    if request.method == 'POST':
        
        file = request.files['img']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD'], filename))
        filepath = seg.getpersonsegmentation(model=model, imagepath=os.path.join(app.config['UPLOAD'], filename), destination=app.config['BGFOLDER'])
        print(filepath)
        if not filepath:
            print("it is in there")
            return render_template('image_render.html', noperson=True)
        seg.delete_all_png_files(app.config["CACHE"])
        seg.checktime(app.config['BGFOLDER'], 5) # uploaded files will be removed in 5 minutes
        return render_template('image_render.html', img=filepath)
    return render_template('image_render.html')

@app.route(f'{bgremoverpage}?<string:filepath>', methods=['POST'])
def makechange(filepath):
    path = os.path.join(app.config["BGFOLDER"], filepath)
    dest = os.path.join(app.config["CACHE"], filepath)
    checkbox_value = request.form.get("mycheckbox")
    color_value = request.form.get("rgb")
    if checkbox_value == "true":
        shutil.copy2(path, dest)
    else:
        seg.changebgcolor(path, color_value, dest)
    return redirect(url_for('download', filepath=filepath))

@app.route('/static/bgremoved/cache/<filepath>', methods=['GET', 'POST'])
def download(filepath):
    return send_from_directory(app.config["CACHE"], filepath, as_attachment=True)

@app.errorhandler(400)
def handle_bad_request(_):
    return render_template("badrequest.html"), 400

@app.errorhandler(404)
def noaddress(_):
    return render_template("handler.html"), 404

@app.errorhandler(Exception)
def ehandler(e):
    return render_template("exception.html", e=e)
 
 
if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")