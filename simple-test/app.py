from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Tweener Insights - Cloud Run Test Working!'

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))