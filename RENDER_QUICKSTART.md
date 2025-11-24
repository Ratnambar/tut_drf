# Render Deployment Quick Start

This is a quick reference guide for deploying to Render. For detailed instructions, see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md).

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Push to GitHub
```bash
cd tutorial
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Deploy via Render Blueprint

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click **"Apply"** and wait for deployment

### Step 3: Set Environment Variables

After deployment, go to your web service → **Environment** tab and add:

```
SECRET_KEY=<generate-a-secret-key>
DEBUG=False
BASE_URL=https://your-service-name.onrender.com  # Must include https://
RENDER=true
```

**Generate SECRET_KEY:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 4: Run Migrations

1. Go to your service → **Shell** tab
2. Run: `python manage.py migrate`
3. (Optional) Create superuser: `python manage.py createsuperuser`

### Step 5: Verify

Visit: `https://your-service-name.onrender.com/api/docs/`

---

## 🔄 CI/CD Setup (10 Minutes)

### Step 1: Get Render API Key
1. Go to [Render Account Settings](https://dashboard.render.com/account)
2. Create API Key and copy it

### Step 2: Get Service ID
1. Go to your web service
2. Copy Service ID from URL or Settings → Info

### Step 3: Add GitHub Secrets
1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add:
   - `RENDER_API_KEY` = Your Render API key
   - `RENDER_SERVICE_ID` = Your service ID

### Step 4: Test
1. Make a change and push to `main` branch
2. Check **Actions** tab in GitHub
3. Deployment happens automatically!

---

## 📋 Environment Variables Checklist

- [ ] `SECRET_KEY` - Django secret key
- [ ] `DEBUG` - Set to `False`
- [ ] `BASE_URL` - Your Render service URL
- [ ] `RENDER` - Set to `true`
- [ ] `client_id` - Google OAuth (if using)
- [ ] `secret` - Google OAuth (if using)
- [ ] `CUSTOM_DOMAIN` - Custom domain (optional)

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` and build logs |
| Database error | Verify `DATABASE_URL` is set (auto-set by Render) |
| Static files 404 | Check `collectstatic` runs in release command |
| ALLOWED_HOSTS error | Set `RENDER=true` and `RENDER_EXTERNAL_HOSTNAME` |

---

## 📚 Next Steps

- Read full guide: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
- Check Render docs: [render.com/docs](https://render.com/docs)
- Monitor logs: Dashboard → Your Service → Logs

---

## 🎯 What's Configured

✅ Render Blueprint (`render.yaml`)  
✅ CI/CD Pipeline (GitHub Actions)  
✅ Database auto-configuration  
✅ Static files (WhiteNoise)  
✅ Production settings  
✅ Health check endpoint  

Your app is ready to deploy! 🚀

