# 🚀 Deployment Guide - Get Your App Live in 10 Minutes

## Quick Deploy to Streamlit Cloud (RECOMMENDED)

### Prerequisites
- ✅ GitHub account
- ✅ Code pushed to GitHub repository
- ✅ Working `app.py` (you have this!)

### Step-by-Step Deployment

#### 1. Prepare Repository (2 minutes)

Make sure your repo has:
```
✅ app.py
✅ requirements.txt
✅ .streamlit/config.toml
✅ README.md
```

#### 2. Sign Up for Streamlit Cloud (2 minutes)

1. Go to: https://streamlit.io/cloud
2. Click "Sign up"
3. Choose "Continue with GitHub"
4. Authorize Streamlit

#### 3. Deploy App (3 minutes)

1. Click "New app" button
2. Select your repository: `strategy-pipeline`
3. Set branch: `dev` or `main`
4. Main file path: `app.py`
5. Click "Deploy!"

#### 4. Configure Secrets (2 minutes)

If using OpenAI:

1. Click "⋮" menu → "Settings"
2. Go to "Secrets"
3. Add:
```toml
[llm]
provider = "openai"
openai_api_key = "sk-proj-xxxxxxxxxxxxx"
openai_model = "gpt-4o-mini"
openai_temperature = 0.7
```
4. Click "Save"

For Mock mode (free):
```toml
[llm]
provider = "mock"
```

#### 5. Share Your App! (1 minute)

You'll get a URL like:
```
https://strategy-pipeline-username.streamlit.app
```

🎉 **Done!** Your app is live!

---

## Alternative: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - LLM__PROVIDER=mock
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t research-pipeline .

# Run container
docker run -p 8501:8501 \
  -e LLM__PROVIDER=mock \
  research-pipeline

# Or with docker-compose
docker-compose up -d
```

### Deploy to Cloud

**AWS ECS:**
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag research-pipeline:latest <account>.dkr.ecr.us-east-1.amazonaws.com/research-pipeline:latest

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/research-pipeline:latest
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/<project-id>/research-pipeline
gcloud run deploy research-pipeline --image gcr.io/<project-id>/research-pipeline --platform managed
```

---

## Local Development Server

### Run Locally

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run app
streamlit run app.py

# Or with custom port
streamlit run app.py --server.port 8502
```

### Development Mode

Edit `.streamlit/config.toml`:
```toml
[server]
runOnSave = true
fileWatcherType = "auto"

[runner]
magicEnabled = true
fastReruns = true
```

---

## Configuration Management

### Environment Variables

`.env` file (local development):
```env
LLM__PROVIDER=mock
LLM__OPENAI_API_KEY=sk-proj-xxx
LLM__OPENAI_MODEL=gpt-4o-mini
```

### Streamlit Secrets

`.streamlit/secrets.toml` (cloud deployment):
```toml
[llm]
provider = "mock"
openai_api_key = ""
openai_model = "gpt-4o-mini"
```

### Access in Code

Both work automatically:
```python
from src.config import get_config

config = get_config()  # Reads from env or secrets
```

---

## Custom Domain

### Streamlit Cloud

1. Go to app settings
2. Click "Custom domain"
3. Add your domain: `research.yourdomain.com`
4. Update DNS CNAME record:
   ```
   CNAME: research -> cname.streamlit.app
   ```

### Other Platforms

Use reverse proxy (nginx):
```nginx
server {
    listen 80;
    server_name research.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Monitoring & Analytics

### Streamlit Built-in

Already included:
- Page view tracking
- Error logging
- Performance metrics

Access at: `https://your-app.streamlit.app/admin`

### Custom Analytics

Add to `app.py`:
```python
import streamlit as st
from datetime import datetime

# Track usage
if "sessions" not in st.session_state:
    st.session_state.sessions = []
    
st.session_state.sessions.append({
    "timestamp": datetime.now(),
    "stage": current_stage,
    "provider": config.llm.provider
})

# Log to file or database
save_analytics(st.session_state.sessions)
```

### Error Tracking

Integrate Sentry:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

---

## Performance Optimization

### Caching

Already implemented:
```python
@st.cache_resource
def get_model_service():
    return IntelligentModelService()

@st.cache_data
def validate_term(term):
    return validator.validate_term(term)
```

### Database Connection Pooling

For future:
```python
@st.cache_resource
def get_db_connection():
    return psycopg2.connect(...)
```

### Static Assets

Use CDN for large files:
```python
# Instead of local files
st.image("https://cdn.yoursite.com/logo.png")
```

---

## Security Best Practices

### API Keys

✅ **DO**: Store in secrets
```toml
[secrets]
api_key = "sk-xxx"
```

❌ **DON'T**: Hardcode in code
```python
api_key = "sk-xxx"  # Never do this!
```

### HTTPS

Streamlit Cloud: ✅ Automatic HTTPS

Self-hosted: Use Let's Encrypt
```bash
certbot --nginx -d research.yourdomain.com
```

### Rate Limiting

Add to app:
```python
from time import time

if "last_request" not in st.session_state:
    st.session_state.last_request = 0

# Rate limit: 1 request per 5 seconds
if time() - st.session_state.last_request < 5:
    st.error("Please wait 5 seconds between requests")
    st.stop()

st.session_state.last_request = time()
```

---

## Backup & Recovery

### Data Backup

```bash
# Backup projects
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Upload to cloud
aws s3 cp backup-*.tar.gz s3://your-bucket/backups/
```

### Automated Backups

Cron job:
```bash
0 0 * * * /path/to/backup-script.sh
```

### Disaster Recovery

Keep in git:
- ✅ All code
- ✅ Configuration templates
- ✅ Documentation

External backup:
- 📦 User data
- 📦 Generated projects
- 📦 Analytics logs

---

## Scaling

### Vertical Scaling

Streamlit Cloud tiers:
- **Free**: 1 GB RAM, 1 CPU
- **Pro**: 4 GB RAM, 2 CPU
- **Enterprise**: Custom

### Horizontal Scaling

For high traffic:
1. Load balancer
2. Multiple app instances
3. Shared database
4. Redis cache

---

## Testing Deployment

### Pre-Deploy Checklist

```bash
# Run tests
pytest tests/

# Check dependencies
pip check

# Test app locally
streamlit run app.py

# Check environment
python -c "from src.config import get_config; print(get_config().llm.provider)"

# Verify syntax
python demo_syntax_engine.py
```

### Post-Deploy Verification

1. ✅ App loads
2. ✅ All 3 stages work
3. ✅ Syntax generation works
4. ✅ Validation works (if OpenAI)
5. ✅ Export works
6. ✅ Mobile responsive

---

## Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check logs
streamlit run app.py --logger.level debug

# Verify imports
python -c "import streamlit; import src.services.intelligent_model_service"
```

**Slow performance:**
```bash
# Clear cache
streamlit cache clear

# Check caching
st.cache_data.clear()
st.cache_resource.clear()
```

**Module not found:**
```bash
# Rebuild venv
pip install -r requirements.txt --force-reinstall
```

---

## Cost Estimation

### Streamlit Cloud

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 1 app, 1GB RAM |
| Pro | $20/mo | Unlimited apps, 4GB RAM |
| Teams | $250/mo | Team features, SSO |

### OpenAI API

| Usage | Cost/Month |
|-------|------------|
| 100 workflows | ~$0.60 |
| 1,000 workflows | ~$6 |
| 10,000 workflows | ~$60 |

### Self-Hosted

| Service | Cost/Month |
|---------|------------|
| AWS t3.small | ~$15 |
| DigitalOcean Droplet | ~$12 |
| Google Cloud Run | ~$5 (pay per use) |

---

## 🎯 Recommended: Start with Streamlit Cloud Free

**Why:**
- ✅ $0 cost
- ✅ 10-minute setup
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ No server management

**You can always migrate later!**

---

## Quick Links

- 🌐 Streamlit Cloud: https://streamlit.io/cloud
- 📖 Streamlit Docs: https://docs.streamlit.io
- 🐳 Docker Hub: https://hub.docker.com
- 📊 Analytics: https://analytics.google.com

---

## Next Steps

1. ✅ Deploy to Streamlit Cloud (10 min)
2. ✅ Get public URL
3. ✅ Test all features
4. ✅ Share with 5 beta users
5. ✅ Collect feedback

**Then**: Iterate based on real usage!

---

**Ready to deploy?** Start with Streamlit Cloud → 10 minutes to live app! 🚀

