from flask import Flask , render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('tut1_index.html')

@app.route("/about")
def suraj():
    name = 'Santosh Pudasaini  '
    return render_template('tut2_about.html',name2 = name )

@app.route("/bootstrap")
def bootstrap():
    return render_template('tut3_bootstrap.html')

app.run(debug=True)