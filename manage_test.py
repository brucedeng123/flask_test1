from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return """
        <html>
            <body>
                <h1>Hello,user</h1>
            </body>
        </html>
"""
if __name__=='__name__':
    app.run()