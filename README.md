# 🎨 Art Gallery Web Application

> A production-grade web application deployed on AWS, showcasing famous paintings with a fully serverless-ready architecture using Elastic Beanstalk, DynamoDB, and S3.

![AWS](https://img.shields.io/badge/AWS-Elastic%20Beanstalk-orange?logo=amazon-aws)
![AWS](https://img.shields.io/badge/AWS-DynamoDB-blue?logo=amazon-aws)
![AWS](https://img.shields.io/badge/AWS-S3-green?logo=amazon-aws)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-lightgrey?logo=flask)
![Region](https://img.shields.io/badge/Region-us--west--2-yellow)

---

## 📌 Project Overview

The Art Gallery is a full-stack web application that allows visitors to browse six of the world's most famous paintings, click on any painting to open a dedicated detail page, and view rich metadata including the title, artist, year, and description.

This project is built as a **hands-on AWS lab** that demonstrates real-world cloud architecture patterns including:

- Separation of data from application code using **Amazon DynamoDB**
- Scalable static asset delivery via **Amazon S3**
- Zero-downtime deployments using **AWS Elastic Beanstalk**
- Automatic traffic distribution with an **Application Load Balancer**
- Dynamic capacity management through an **Auto Scaling Group**
- Secure access control using **AWS IAM roles and policies**
- Environment-based configuration using **Environment Variables** — no hardcoded secrets

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────┐
                        │         AWS Cloud (us-west-2)   │
                        │                                 │
  User Browser          │   ┌─────────────────────────┐   │
      │                 │   │   Elastic Beanstalk      │   │
      │  HTTPS          │   │   Environment            │   │
      ▼                 │   │                         │   │
 ┌─────────┐            │   │  ┌───────────────────┐  │   │
 │   ALB   │◄───────────┼───┼──│  Auto Scaling     │  │   │
 │  (pub)  │            │   │  │  Group            │  │   │
 └────┬────┘            │   │  │  ┌─────────────┐  │  │   │
      │                 │   │  │  │ EC2 Instance│  │  │   │
      │ internal        │   │  │  │ Flask+Gunic │  │  │   │
      ▼                 │   │  │  └──────┬──────┘  │  │   │
 ┌─────────┐            │   │  │         │         │  │   │
 │ Private │            │   │  │  ┌─────────────┐  │  │   │
 │ Subnets │            │   │  │  │ EC2 Instance│  │  │   │
 └─────────┘            │   │  │  │ Flask+Gunic │  │  │   │
                        │   │  │  └──────┬──────┘  │  │   │
                        │   │  └─────────┼─────────┘  │   │
                        │   └───────────┼─────────────┘   │
                        │               │                  │
                        │     ┌─────────┴──────────┐       │
                        │     │                    │       │
                        │     ▼                    ▼       │
                        │ ┌────────┐         ┌─────────┐   │
                        │ │Dynamo  │         │  S3     │   │
                        │ │  DB    │         │ Bucket  │   │
                        │ │(data)  │         │(images) │   │
                        │ └────────┘         └─────────┘   │
                        └─────────────────────────────────┘
```

### Request Flow

| Step | What Happens |
|------|-------------|
| 1 | User visits the Elastic Beanstalk URL |
| 2 | Request hits the **Application Load Balancer** |
| 3 | ALB routes to a healthy **EC2 instance** (round-robin) |
| 4 | **Flask** app processes the request |
| 5 | **boto3** fetches painting metadata from **DynamoDB** |
| 6 | Flask constructs S3 image URLs from environment variables |
| 7 | Rendered HTML is returned to the browser |
| 8 | Browser fetches images **directly from S3** — no app server involved |

---

## ☁️ AWS Services Used

| Service | Role in This Project |
|---------|---------------------|
| **AWS Elastic Beanstalk** | Orchestrates the entire deployment — provisions EC2, configures ALB, manages Auto Scaling, handles rolling deployments |
| **Amazon EC2** | Runs the Flask + Gunicorn web server (2 instances minimum across 2 Availability Zones) |
| **Application Load Balancer** | Distributes incoming HTTP traffic across EC2 instances; performs health checks every 30 seconds |
| **Auto Scaling Group** | Scales EC2 instances between 2 (min) and 4 (max) based on CPU utilization thresholds |
| **Amazon S3** | Stores painting image files; serves them directly to browsers with public read access |
| **Amazon DynamoDB** | NoSQL database storing all painting metadata (title, artist, year, description, image_key); On-demand capacity |
| **AWS IAM** | EC2 instance profile with least-privilege read access to DynamoDB and S3 |

---

## 🔑 Key Design Decisions

### 1. Data Separated from Code
Painting data lives in DynamoDB, not in the source code. Adding a new painting requires only a new database record and an S3 upload — zero code changes, zero redeployment.

### 2. No Hardcoded Configuration
All environment-specific values (S3 bucket URL, DynamoDB table name, AWS region) are injected as **Environment Variables** through Elastic Beanstalk configuration. The `.env` file is local-only and never committed.

### 3. Images Served Directly from S3
The Flask application never handles image binary data. It constructs image URLs pointing to S3, and the browser fetches images directly. This offloads bandwidth from your EC2 instances and leverages S3's virtually unlimited throughput.

### 4. High Availability by Default
The environment runs a minimum of **2 EC2 instances across 2 Availability Zones**. If one instance or AZ fails, traffic is automatically rerouted to the surviving instance with zero downtime.

---

## 🗂️ Project Structure

```
art-gallery/
├── app.py                  # Flask application — routes and DynamoDB queries
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn startup command for Elastic Beanstalk
├── .env                    # Local environment variables (never committed)
├── .gitignore              # Git ignore rules
├── templates/
│   ├── index.html          # Homepage — painting grid
│   ├── detail.html         # Painting detail page
│   └── 404.html            # Custom 404 error page
└── static/
    └── css/
        └── style.css       # Application stylesheet
```

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `S3_BUCKET_URL` | Base URL of your S3 bucket (no trailing slash) | `https://my-bucket.s3.us-west-2.amazonaws.com` |
| `DYNAMODB_TABLE` | Name of the DynamoDB table | `art-gallery-paintings` |
| `APP_REGION` | AWS region where your resources are deployed | `us-west-2` |

> **Note:** On Elastic Beanstalk, these are set in the environment configuration. Locally, they are loaded from a `.env` file via `python-dotenv`.

---

## 🗄️ DynamoDB Table Schema

**Table name:** `art-gallery-paintings`
**Partition key:** `id` (Number)

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | Number | Unique identifier (1, 2, 3...) |
| `title` | String | Painting title |
| `artist` | String | Artist full name |
| `year` | String | Year or date range of creation |
| `description` | String | Short descriptive paragraph |
| `image_key` | String | S3 object key (filename only, e.g. `starry-night.jpg`) |

---

## 🚀 Deployment

Full step-by-step deployment instructions are included in the `docs/` folder:

📄 **[Art_Gallery_AWS_Lab_Final.docx](docs/Art_Gallery_AWS_Lab_Final.docx)** — Complete hands-on lab guide covering:
- All application files with full code
- S3 bucket creation and image upload
- DynamoDB table setup and data insertion
- IAM role configuration
- VPC and networking setup
- Elastic Beanstalk deployment wizard (all 6 steps)
- Troubleshooting guide for 8 common errors
- Clean-up instructions

### Quick Deployment Summary

```
1. Create S3 bucket → upload images → apply public read policy
2. Create DynamoDB table → insert 6 painting records
3. Create IAM role (art-gallery-eb-ec2-role) with required policies
4. Create VPC with 2 public subnets across different AZs
5. Package application as ZIP (use PowerShell .NET method on Windows)
6. Deploy via Elastic Beanstalk → Python 3.11 → High availability preset
7. Set environment variables in Beanstalk configuration
```

---

## 🛠️ Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/art-gallery.git
cd art-gallery

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure local environment
cp .env.example .env
# Edit .env with your actual S3 bucket URL and DynamoDB table name

# Configure AWS CLI credentials
aws configure

# Run locally
python app.py
# Visit http://127.0.0.1:5000
```

> **Note:** Local development requires valid AWS credentials with read access to DynamoDB and S3. The app will return a `ResourceNotFoundException` if the DynamoDB table does not exist in the configured region.

---

## 💰 Estimated Cost

| Scenario | Duration | Estimated Cost |
|----------|----------|---------------|
| Testing (1 day) | 24 hours | ~$1.50 |
| Short lab (1 week) | 7 days | ~$9.00 |
| Full month running | 30 days | ~$38–40 |

> Largest cost driver: Application Load Balancer (~$22/month base charge). DynamoDB and S3 are effectively free at this scale.
>
> **Always terminate your Elastic Beanstalk environment when done to stop all charges.**

---

## 🧹 Clean Up

```
1. Elastic Beanstalk → Environments → art-gallery-env → Actions → Terminate environment
2. DynamoDB → Tables → art-gallery-paintings → Delete
3. S3 → Delete all objects → Delete bucket
```

---

## 📚 What This Project Demonstrates

- **PaaS deployment** with AWS Elastic Beanstalk
- **NoSQL data modeling** with Amazon DynamoDB
- **Object storage** and static asset delivery with Amazon S3
- **IAM least-privilege** access control
- **Twelve-Factor App** principles (config via environment variables)
- **High availability** architecture across multiple Availability Zones
- **Auto scaling** based on CPU metrics

---

## 📄 License

This project is for educational purposes as part of the AWS Cloud Diploma program.

---

*Built with Flask · Deployed on AWS Elastic Beanstalk · Data in DynamoDB · Images in S3*
