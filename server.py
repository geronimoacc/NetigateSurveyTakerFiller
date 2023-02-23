from flask import Flask, request, render_template
from functions import *

#Create the application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    url = request.form['survey_url']
    runs = int(request.form['number_of_runs'])
    freetext_file = request.form['text_file']
    main(runs,url,freetext_file)
    return index()

if __name__ == '__main__':
    app.debug=True
    app.run()