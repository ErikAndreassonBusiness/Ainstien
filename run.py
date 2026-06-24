from app import create_app
from app.server.models.model_extras import compute_database_zscores, print_outlier_summary

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        print_outlier_summary(df=compute_database_zscores())
    app.run(port=5001, debug=True)