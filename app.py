from flask import Flask, request, redirect, url_for, render_template, jsonify
import boto3
import os
import random
from botocore.config import Config

app = Flask(__name__)


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image', methods=['GET'])
def view():
        bucket = os.environ["IMAGES_BUCKET"]
        config = Config(signature_version='s3v4')
        s3_client = boto3.client("s3",config=config)
        image_number = random.randint(1, 10)
        image_key = f"{image_number}.jpg"
        try:
            image_url = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": image_key}, ExpiresIn=300
        )
        except Exception as e:
            return "Error downloading image from S3: {}".format(str(e)), 500
        return render_template('image.html', image_url=image_url)

@app.route('/upload', methods=['POST'])
def upload():
    bucket = os.environ["IMAGES_BUCKET"]
    config = Config(signature_version='s3v4')
    s3_client = boto3.client("s3",config=config)
    file = request.files['file']
    if file:
        try:
            s3_client.upload_fileobj(file, bucket, file.filename)
        except Exception as e:
            return "Error uploading image to S3: {}".format(str(e)), 500
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)