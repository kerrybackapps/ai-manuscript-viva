# Deploy to Koyeb - Manual Instructions

## Step 1: Go to Koyeb Dashboard

Navigate to: https://app.koyeb.com/

## Step 2: Create New Service

1. Click **"Create Service"**
2. Choose **"GitHub"** as deployment source
3. Select repository: `kerrybackapps/ai-manuscript-viva`
4. Branch: `master`

## Step 3: Configure Build Settings

- **Builder**: Buildpack (auto-detected)
- **Build command**: (leave empty - auto-detected)
- **Run command**: `python demo_app.py`

## Step 4: Environment Variables

Add these environment variables (use your actual values from `.env` file):

| Variable | Value |
|----------|-------|
| `PORT` | `8000` |
| `ANTHROPIC_KEY` | Copy from your .env file |
| `OPENAI_API_KEY` | Copy from your .env file |
| `GEMINI_KEY` | Copy from your .env file |
| `ELEVENLABS_API_KEY` | Copy from your .env file |
| `ADMIN_PASSWORD` | `password` |
| `SECRET_KEY` | Copy from your .env file |

## Step 5: Service Configuration

- **Instance type**: `nano` (free tier) or `small` (recommended)
- **Regions**: Select closest region (e.g., `was` for Washington DC)
- **Port**: `8000`
- **Health check**: `/` (root path)

## Step 6: Deploy

Click **"Deploy"** and wait 2-3 minutes for build to complete.

## Step 7: Get Your Public URL

After deployment completes, Koyeb will provide a public URL:
- Format: `https://your-service-name-your-org.koyeb.app`
- Example: `https://ai-manuscript-viva-kerrybackapps.koyeb.app`

## Step 8: Initialize Database

After first deployment, initialize prompts and settings:

**Option 1: Automatic (Recommended)**
- Visit the app URL - database tables auto-create on first run
- Login to admin panel at `/admin`
- If prompts/settings are missing, run Option 2

**Option 2: Manual**
```bash
python initialize_prompts.py
```

This creates:
- All prompt templates (manuscript analysis, examiner agent, rubrics)
- Default assignment text (editable via admin panel)

## Access Your App

- **Upload page**: `https://your-app.koyeb.app/` (shows assignment and upload form)
- **Admin panel**: `https://your-app.koyeb.app/admin`
- **Admin password**: `password`

## Admin Panel Features

After logging in to `/admin`, you can:
- **Dashboard** - View all exam sessions with scores from all 3 graders
- **Exam Details** - See full transcripts and detailed grading assessments
- **Edit Prompts** - Modify exam questions and grading rubrics
- **Edit Settings** - Change assignment text shown to students
- All changes persist across deployments (no rebuild needed)

## Auto-Deploy

Koyeb automatically redeploys when you push to GitHub master branch.

To update:
```bash
git add .
git commit -m "your changes"
git push origin master
```

Koyeb will rebuild and redeploy automatically (~2 minutes).

## Database Persistence

SQLite database persists across deployments in Koyeb's persistent storage.

All prompts, exams, and grading results are preserved.

## Troubleshooting

**Build fails?**
- Check `requirements.txt` is in repository root
- Verify all dependencies are listed

**App won't start?**
- Check all environment variables are set
- View logs in Koyeb dashboard
- Verify PORT=8000

**Can't login to admin?**
- Check ADMIN_PASSWORD env var
- Clear browser cookies
- Try incognito/private window

**Database empty?**
- Prompts should auto-initialize on first run
- If not, manually run `initialize_prompts.py`

## Cost

- **Nano instance**: Free tier (limited resources, may sleep)
- **Small instance**: ~$5/month (always on, better performance)
- **API costs**: ~$1.15 per student exam

## GitHub Repository

https://github.com/kerrybackapps/ai-manuscript-viva

---

**Note**: This guide uses manual web UI deployment. Koyeb CLI installation was not available on this system.
