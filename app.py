from app import create_app

app = create_app()

@app.route('/')
def home():
    return "Hello World"




if __name__ == '__main__':
    app.run(port=5001,debug=True)
