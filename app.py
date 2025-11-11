# app.py
import flask
import os
from flask import request, render_template, redirect, send_from_directory, make_response
from src import classes
import subprocess

app = flask.Flask(__name__)

@app.route('/')
async def index():
  if "squareweb.app" in request.host:
    redirect_url = "https://mediato.cloud/"
    return redirect(redirect_url, code=302)
  try:
    input_url = request.args.get('url')
    media = None
    error = None
    
    if input_url and not input_url.startswith("http"):
        input_url = "https://" + input_url
    if input_url:
        cls = classes.get_social_media_class(input_url)
        if cls:
            try:
                instance = cls(input_url)
                media = await instance.get_post_media()
                if not media:
                    error = "No media found at the provided URL."
            except Exception as e:
                error = f"Error trying to found that media: {e}"
        else:
            error = "Not Supported Domain."

    return render_template("index.html", media_url=input_url, media=media, error=error)
  except Exception as err:
    return err
  
@app.errorhandler(404)
def page_not_found(_):
    response = make_response(render_template("404.html"), 404)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.route('/robots.txt')
def robots():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon/favicon.ico')

@app.route('/manifest.json')
def manifest():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'manifest/manifest.json')

app.run(
    host="0.0.0.0",
    port=80
)

