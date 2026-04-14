from flask import Flask, render_template

app = Flask()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    email = "support@example.com"
    return render_template('contact.html', email=email)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)