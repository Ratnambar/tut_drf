# Render Deployment Guide

This comprehensive guide will help you deploy your Django REST Framework project to Render and set up a CI/CD pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Render Setup](#initial-render-setup)
3. [Database Setup](#database-setup)
4. [Environment Variables](#environment-variables)
5. [Deployment Methods](#deployment-methods)
6. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
2. **GitHub Account**: For version control and CI/CD
3. **Git Repository**: Your project should be in a Git repository (GitHub recommended)
4. **Python 3.12.8**: Your project uses Python 3.12.8 (specified in `runtime.txt`)

---

## Initial Render Setup

### Method 1: Using Render Blueprint (Recommended)

Render Blueprint allows you to deploy your entire stack (web service + database) with a single configuration file.

#### Step 1: Push Your Code to GitHub

```bash
# If you haven't already, initialize git and push to GitHub
cd tutorial
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

#### Step 2: Deploy via Render Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` in your repository
5. Review the configuration and click **"Apply"**
6. Render will create:
   - A web service
   - A PostgreSQL database
   - All necessary environment variables

### Method 2: Manual Setup

#### Step 1: Create a Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `drf-project` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn tutorial.wsgi:application`
   - **Plan**: Choose `Free` (for testing) or `Starter`/`Standard` (for production)

#### Step 2: Configure Root Directory

If your `manage.py` is in a subdirectory (like `tutorial/`), set:
- **Root Directory**: `tutorial`

---

## Database Setup

### Using Render Blueprint

The database is automatically created when using `render.yaml`. The connection string is automatically set as `DATABASE_URL`.

### Manual Database Setup

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `drf-project-db`
   - **Database**: `drf_project`
   - **User**: `drf_project_user`
   - **Plan**: Choose `Free` (for testing) or `Starter`/`Standard` (for production)
4. After creation, copy the **Internal Database URL**
5. Add it to your web service environment variables as `DATABASE_URL`

---

## Environment Variables

Set the following environment variables in your Render web service:

### Required Variables

1. **SECRET_KEY**
   - Generate a secret key:
     ```python
     from django.core.management.utils import get_random_secret_key
     print(get_random_secret_key())
     ```
   - Or use Render's auto-generated value (if using Blueprint)

2. **DEBUG**
   - Set to: `False` (for production)

3. **BASE_URL**
   - Format: `https://your-service-name.onrender.com`
   - **Important**: Must include `https://` prefix
   - Or your custom domain if configured
   - Note: If using Blueprint, you may need to manually update this after first deployment to include `https://`

4. **RENDER**
   - Set to: `true` (enables Render-specific settings)

5. **RENDER_EXTERNAL_HOSTNAME**
   - Automatically set by Render (format: `your-service-name.onrender.com`)

### Optional Variables

6. **CUSTOM_DOMAIN**
   - Your custom domain (if you have one)

7. **client_id** (Google OAuth)
   - Your Google OAuth Client ID

8. **secret** (Google OAuth)
   - Your Google OAuth Client Secret

### How to Set Environment Variables

1. Go to your web service in Render Dashboard
2. Navigate to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add each variable with its value
5. Click **"Save Changes"**

---

## Deployment Methods

### Automatic Deployments (Recommended)

Render automatically deploys when you push to your connected branch (usually `main` or `master`).

1. Make changes to your code
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```
3. Render will automatically:
   - Build your application
   - Run migrations (if configured in `release` command)
   - Deploy the new version

### Manual Deployments

1. Go to your service in Render Dashboard
2. Click **"Manual Deploy"**
3. Select the branch and commit
4. Click **"Deploy"**

---

## CI/CD Pipeline Setup

### Step 1: Get Render API Key

1. Go to [Render Account Settings](https://dashboard.render.com/account)
2. Scroll to **"API Keys"** section
3. Click **"Create API Key"**
4. Copy the API key (you'll need it for GitHub Secrets)

### Step 2: Get Render Service ID

1. Go to your web service in Render Dashboard
2. The Service ID is in the URL: `https://dashboard.render.com/web/your-service-id`
3. Or go to **"Settings"** → **"Info"** → Copy the **Service ID**

### Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add the following secrets:

   - **RENDER_API_KEY**: Your Render API key
   - **RENDER_SERVICE_ID**: Your Render service ID
   - **SECRET_KEY** (optional): Your Django secret key for testing

### Step 4: Verify CI/CD Workflow

The CI/CD pipeline (`.github/workflows/render-ci-cd.yml`) will:

1. **On every push/PR**:
   - Run code linting (flake8)
   - Run Django tests
   - Check for pending migrations

2. **On push to main/master**:
   - Run all tests
   - Automatically deploy to Render (if tests pass)

### Step 5: Test the Pipeline

1. Make a small change to your code
2. Create a pull request
3. Check the **"Actions"** tab in GitHub to see the CI pipeline running
4. Merge the PR to trigger deployment

---

## Post-Deployment Configuration

### Step 1: Run Initial Migrations

After first deployment, run migrations:

1. Go to your service in Render Dashboard
2. Open **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   ```

Or use the Render CLI:
```bash
render exec <service-id> -- python manage.py migrate
```

### Step 2: Create Superuser

1. Open **"Shell"** in Render Dashboard
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow the prompts

### Step 3: Update Google OAuth Redirect URIs

If using Google OAuth:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Edit your OAuth 2.0 Client ID
4. Add authorized redirect URI:
   ```
   https://your-service-name.onrender.com/accounts/google/login/callback/
   ```

### Step 4: Verify Deployment

1. Visit your service URL: `https://your-service-name.onrender.com`
2. Check API docs: `https://your-service-name.onrender.com/api/docs/`
3. Test your endpoints

---

## Troubleshooting

### Common Issues

#### 1. Build Fails

**Problem**: Build command fails during deployment

**Solutions**:
- Check build logs in Render Dashboard
- Verify `requirements.txt` is correct
- Ensure Python version matches `runtime.txt`
- Check for missing dependencies

#### 2. Database Connection Errors

**Problem**: `django.db.utils.OperationalError` or connection refused

**Solutions**:
- Verify `DATABASE_URL` is set correctly
- Ensure database service is running
- Check database credentials
- Verify SSL is enabled (Render requires SSL)

#### 3. Static Files Not Loading

**Problem**: CSS/JS files return 404

**Solutions**:
- Verify `collectstatic` runs during build (check `release` command in Procfile)
- Check `STATIC_ROOT` and `STATIC_URL` in settings
- Ensure WhiteNoise middleware is enabled
- Check static files are collected: `python manage.py collectstatic --dry-run`

#### 4. ALLOWED_HOSTS Error

**Problem**: `DisallowedHost` error

**Solutions**:
- Verify `RENDER_EXTERNAL_HOSTNAME` is set
- Check `ALLOWED_HOSTS` in settings.py
- Ensure `RENDER=true` environment variable is set

#### 5. Environment Variables Not Working

**Problem**: Variables not being read

**Solutions**:
- Verify variables are set in Render Dashboard
- Check variable names match exactly (case-sensitive)
- Restart the service after adding variables
- Check logs for errors

### Debugging Commands

#### View Logs

1. Go to your service in Render Dashboard
2. Click **"Logs"** tab
3. View real-time logs

Or use Render CLI:
```bash
render logs <service-id> --tail
```

#### Access Shell

1. Go to your service in Render Dashboard
2. Click **"Shell"** tab
3. Run Django commands:
   ```bash
   python manage.py shell
   python manage.py dbshell
   python manage.py check
   ```

#### Check Service Status

1. Go to your service in Render Dashboard
2. Check **"Events"** tab for deployment history
3. Check **"Metrics"** tab for resource usage

---

## Project Structure

```
tutorial/
├── .github/
│   └── workflows/
│       └── render-ci-cd.yml      # CI/CD pipeline
├── render.yaml                    # Render Blueprint config
├── Procfile                       # Process configuration
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python version
├── release.sh                     # Release script (optional)
└── tutorial/
    └── settings.py               # Django settings (Render-ready)
```

---

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key | Auto-generated or custom |
| `DEBUG` | Yes | Debug mode | `False` |
| `RENDER` | Yes | Enable Render mode | `true` |
| `RENDER_EXTERNAL_HOSTNAME` | Auto | Service hostname | Auto-set by Render |
| `BASE_URL` | Yes | Full app URL | `https://your-app.onrender.com` |
| `DATABASE_URL` | Auto | Database connection | Auto-set by Render |
| `CUSTOM_DOMAIN` | No | Custom domain | `yourdomain.com` |
| `client_id` | Optional | Google OAuth ID | Your Google client ID |
| `secret` | Optional | Google OAuth secret | Your Google secret |

---

## Render Plans

### Free Tier (Testing/Development)
- **Web Service**: 750 hours/month, spins down after 15 min inactivity
- **Database**: 90 days retention, 1GB storage
- **Limitations**: Service may sleep, slower cold starts

### Starter Plan ($7/month)
- **Web Service**: Always on, 512MB RAM
- **Database**: Included, 1GB storage
- **Best for**: Small production apps

### Standard Plan ($25/month)
- **Web Service**: Always on, 2GB RAM
- **Database**: Included, 10GB storage
- **Best for**: Production apps with traffic

---

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django on Render](https://render.com/docs/deploy-django)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

## Support

For issues:
1. Check Render logs in Dashboard
2. Verify all environment variables are set
3. Check GitHub Actions logs for CI/CD issues
4. Review Render documentation

For Render-specific issues, contact [Render Support](https://render.com/docs/support).

