from waitress import serve
import app

if __name__ == "__main__":
    serve(app.app, port=80)