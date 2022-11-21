from galvanalyser import app, celery

if __name__ == "__main__":
    print("Launching server")
    app.run(host='0.0.0.0', debug=True)
