from final import create_app
app = create_app()

# celery_app = flask_app.extensions["celery"]
if __name__ == "__main__":
  app.run(host='0.0.0.0',port=6000,debug=True,ssl_context=(
    'cert.pem',
    'privkey.pem'))
