from galvanalyserapp import init_app, init_db

config = init_db()
app = init_app(config)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

