import sys
sys.dont_write_bytecode = True

from app import app

@app.route("/")
def index():
    return {'name':"ECC-MVP", 'version':"0.0.1", 'status':"OK"}

@app.route('/health')
def health():
    # TODO do some checks here to confirm everything works
    return {'status':'OK'}, 200


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port=port)

    