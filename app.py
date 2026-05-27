import os
import boto3
from flask import Flask, render_template, abort
from dotenv import load_dotenv

# Load .env for local development only
# On Elastic Beanstalk, env vars come from the platform configuration
load_dotenv()

app = Flask(__name__)

# All configuration from environment variables — nothing hardcoded
S3_BUCKET_URL  = os.environ.get("S3_BUCKET_URL", "")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "art-gallery-paintings")
AWS_REGION     = os.environ.get("APP_REGION", "us-west-2")

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table    = dynamodb.Table(DYNAMODB_TABLE)


def get_all_paintings():
    """Fetch all paintings from DynamoDB, sorted by id."""
    response = table.scan()
    items = response.get("Items", [])
    for item in items:
        item["id"]        = int(item["id"])
        item["image_url"] = f"{S3_BUCKET_URL}/{item['image_key']}"
    return sorted(items, key=lambda x: x["id"])


def get_painting_by_id(painting_id):
    """Fetch a single painting from DynamoDB by numeric id."""
    response = table.get_item(Key={"id": painting_id})
    item = response.get("Item")
    if item:
        item["id"]        = int(item["id"])
        item["image_url"] = f"{S3_BUCKET_URL}/{item['image_key']}"
    return item


@app.route("/")
def index():
    paintings = get_all_paintings()
    return render_template("index.html", paintings=paintings)


@app.route("/painting/<int:painting_id>")
def painting_detail(painting_id):
    painting = get_painting_by_id(painting_id)
    if painting is None:
        abort(404)
    return render_template("detail.html", painting=painting)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
