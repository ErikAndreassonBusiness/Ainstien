from app import create_app
from app.model import model

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        model()
    app.run(port=5001, debug=True)