from app import create_app

app = create_app()


@app.route('/')
def health_check():
    return 'Image processing service is up and running!'

if __name__ == '__main__':
    app.run(port=5001,debug=True)
