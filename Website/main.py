import os
from flask import Flask, render_template, request, redirect, session
from flask_dropzone import Dropzone
from get_data import FlutterData, Vocabulary, Pad
import time

from predict import predict

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.update(
    UPLOAD_PATH= os.path.join(basedir, 'images'),
    DROPZONE_MAX_FILE_SIZE = 10,
    DROPZONE_TIMEOUT = 10 * 6 * 1000, # 10 MINUTES
    DROPZONE_ALLOWED_FILE_TYPE = 'image',
    DROPZONE_REDIRECT_VIEW = 'upload'
)
app.secret_key = b'kev254dwb#@$as^%je#$%wg64'

dropzone = Dropzone(app)

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        f = request.files.get('file')
        new_file_name = os.path.join(app.config['UPLOAD_PATH'], f.filename)
        session['fileloc'] = new_file_name
        f.save(new_file_name)
    
    return render_template("home.html")

@app.route('/upload')
def upload():
    fileloc = session.get('fileloc')

    time.sleep(5)
    
    result = predict(fileloc)

    code = """ import \'package:flutter/material.dart\';
        void main() {
        class MyApp StatelessWidget {@override
        Widget build(BuildContext context) {return MaterialApp(: 'Title',
                theme: SData(: Colors.blue,
home: BuildForm(),);
        class SigninPage 
            Widget build(BuildContext context) {
                return Scaffold(body: LayoutBuilder(builder: (context, constraints) {
                if (constraints.maxWidth > maxSize) {
                    return narrowLayout();
                } else {
                Center wideLayout() => Center(
                    child: SingleChildScrollView(
        child: Column(children: 
                    AppLinkToPage(text: 
                ])));Padding narrowLayout() => Padding(
                padding: const EdgeInsets.symmetric(horizontal: maxPadding),
                child: wideLayout());
        } """

    # for r in result:
    #     if r != '<SOS>' or r!= '<EOS>': 
    #         code += r + ' '
    # code = code.replace('<_N_>', '\n')

    return render_template("code.html", code=code)

if __name__ == "__main__":
    app.run()