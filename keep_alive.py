from flask import Flask, send_from_directory, safe_join, abort
from threading import Thread

app = Flask('')
app.config["CLIENT_CSV"] = "files/"

@app.route('/')
def home():
    return "Hello. I am alive!"

@app.route('/get/<name_file>')
def get_csv(name_file):
  filename = str(name_file)
  try:
      return send_from_directory(app.config["CLIENT_CSV"], filename=filename, as_attachment=True)
  except FileNotFoundError:
      abort(404)

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()