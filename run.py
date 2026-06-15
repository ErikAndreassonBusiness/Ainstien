from app import create_app
from app.server.models.model import model
from app.server.models.fundamental_model import fundamental_model
from app.server.models.metric_model import metric_model

app = create_app()

if __name__ == "__main__":
    #with app.app_context():
        #fundamental_model()
        #metric_model()
    app.run(port=5001, debug=True)