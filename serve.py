from waitress import serve
import app

if __name__ == "__main__":
    serve(app.app, host="52.41.36.82", port=80)