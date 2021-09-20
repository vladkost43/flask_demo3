
from flask_project import app


@app.route('/')
def hello():
    return "Hello World! {0}"


if __name__ == '__main__':
    app.run(debug=True)
