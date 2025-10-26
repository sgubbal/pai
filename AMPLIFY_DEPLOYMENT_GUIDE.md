# AWS Amplify Deployment Guide for PAI Frontend

This guide walks you through deploying the PAI Chatbot frontend to AWS Amplify.

## Prerequisites

- ✅ Backend deployed (API Gateway URL and API Key available)
- ✅ GitHub account
- ✅ AWS Account with appropriate permissions
- ✅ Code pushed to GitHub repository

## Step-by-Step Deployment

### 1. Verify Backend is Deployed

Before deploying the frontend, ensure your backend is running:

```bash
# Check CloudFormation stack status
aws cloudformation describe-stacks \
  --stack-name pai-chatbot-prod \
  --query 'Stacks[0].StackStatus' \
  --output text

# Should output: CREATE_COMPLETE or UPDATE_COMPLETE
```

Get your backend API URL and API Key:

```bash
# Get API Gateway URL
aws cloudformation describe-stacks \
  --stack-name pai-chatbot-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# Example output: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

**Save these values** - you'll need them for Amplify environment variables.

### 2. Push Frontend Code to GitHub

```bash
# Navigate to project root
cd /Users/sgubbala/pai

# Check git status
git status

# Add all frontend files
git add frontend/

# Commit
git commit -m "Add production-ready React frontend with AWS Amplify support"

# Push to main branch
git push origin main
```

### 3. Create AWS Amplify Application

#### 3.1 Open AWS Amplify Console

1. Go to AWS Console: https://console.aws.amazon.com/amplify/
2. Select your region (same as backend, e.g., `us-east-1`)
3. Click **"Create new app"** → **"Host web app"**

#### 3.2 Connect to GitHub

1. Choose **"GitHub"** as the repository provider
2. Click **"Continue"**
3. Authorize AWS Amplify to access your GitHub account
   - Click **"Authorize AWS Amplify"**
   - Enter your GitHub password if prompted
   - Grant access to repositories

#### 3.3 Select Repository and Branch

1. **Repository**: Select `pai` (or your repository name)
2. **Branch**: Select `main` (or your deployment branch)
3. **Check** "Connecting a monorepo? Pick a folder"
4. **App name**: Enter `pai-chatbot-frontend`
5. Click **"Next"**

### 4. Configure Build Settings

#### 4.1 Verify Build Configuration

Amplify should auto-detect the `amplify.yml` file. Verify it shows:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

#### 4.2 Set Monorepo Configuration

1. **Enable monorepo**: ✅ Checked
2. **Base directory**: `frontend`

This tells Amplify to build only the `frontend/` directory, not the entire repo.

#### 4.3 Advanced Settings (Optional)

- **Build image**: Leave as default (Amazon Linux 2)
- **Node version**: Auto-detected (v18+)
- **Live updates**: Enable for instant deployments

Click **"Next"**

### 5. Configure Environment Variables

This is **CRITICAL** - your app won't work without these.

1. Scroll down to **"Environment variables"** section
2. Click **"Add environment variable"**

Add the following variables:

| Variable | Value | Example |
|----------|-------|---------|
| `VITE_API_URL` | Your API Gateway URL from Step 1 | `https://abc123.execute-api.us-east-1.amazonaws.com/prod` |
| `VITE_API_KEY` | Your API key from backend deployment | `your-secret-api-key-here` |

**Important Notes**:
- Variable names MUST start with `VITE_` for Vite to expose them
- Do NOT include trailing slashes in `VITE_API_URL`
- Keep `VITE_API_KEY` secret - never commit to Git

### 6. Review and Deploy

1. Review all settings:
   - App name: `pai-chatbot-frontend`
   - Repository: `pai`
   - Branch: `main`
   - Base directory: `frontend`
   - Environment variables: ✅ Set
2. Click **"Save and deploy"**

### 7. Monitor Deployment

The deployment process has 4 stages:

```
1. Provision   → Allocating resources
2. Build       → Running npm ci && npm run build
3. Deploy      → Uploading to CDN
4. Verify      → Health check
```

**Timeline**: 3-5 minutes for first deployment

You can view detailed logs for each stage by clicking on the stage name.

### 8. Verify Deployment

Once deployment shows ✅ **"Deployed"**:

1. Click on the **URL** (e.g., `https://main.d1234567890.amplifyapp.com`)
2. Your PAI Chatbot should load
3. Test the following:
   - ✅ Page loads without errors
   - ✅ Dark/light theme toggle works
   - ✅ Can create a new conversation
   - ✅ Can send a message
   - ✅ Receives response from backend
   - ✅ Can switch between conversations
   - ✅ Mobile responsive design works

## Troubleshooting

### Build Fails: "Module not found"

**Cause**: Dependencies not installed correctly

**Solution**:
1. Check `package.json` is in `frontend/` directory
2. Verify base directory is set to `frontend`
3. Redeploy

### Build Fails: "npm ERR! code ELIFECYCLE"

**Cause**: TypeScript compilation errors

**Solution**:
1. Check build logs for specific errors
2. Fix TypeScript errors locally
3. Commit and push

### App Loads but Shows "Configuration Error"

**Cause**: Environment variables not set

**Solution**:
1. Go to Amplify Console → App settings → Environment variables
2. Verify `VITE_API_URL` and `VITE_API_KEY` are set
3. Click **"Redeploy this version"**

### API Calls Return 401 Unauthorized

**Cause**: API key mismatch

**Solution**:
1. Verify `VITE_API_KEY` matches backend API key
2. Check backend Secrets Manager for correct key
3. Update Amplify environment variable
4. Redeploy

### API Calls Return CORS Error

**Cause**: Backend CORS not configured for Amplify URL

**Solution**:
1. Note your Amplify URL (e.g., `https://main.d123.amplifyapp.com`)
2. Update backend API Gateway CORS settings:
   ```yaml
   AllowOrigin: "'*'"  # Or specific Amplify URL
   ```
3. Redeploy backend
4. Test again

### Dark Mode Not Working

**Cause**: LocalStorage permissions

**Solution**:
- Clear browser cache
- Check browser console for errors
- Verify browser allows localStorage

## Advanced Configuration

### Custom Domain

1. In Amplify Console → Domain management
2. Click **"Add domain"**
3. Enter domain: `chat.yourdomain.com`
4. Follow DNS setup instructions:
   - For Route53: Automatic
   - For external DNS: Add CNAME record
5. Wait for SSL certificate (15-30 minutes)

### Branch-Based Deployments

Deploy different environments:

```
main branch     → Production  → chat.yourdomain.com
develop branch  → Staging     → staging.chat.yourdomain.com
feature/*       → Preview     → pr-123.chat.yourdomain.com
```

**Setup**:
1. Amplify Console → App settings → Branch settings
2. Add pattern: `develop`
3. Configure separate environment variables per branch

### Performance Optimization

Enable performance features:

1. **Compression**: Enabled by default (Gzip/Brotli)
2. **Caching**: Configured via Amplify
3. **CDN**: Global edge locations automatic

### Monitoring

View metrics in Amplify Console:
- **Traffic**: Page views, unique visitors
- **Errors**: 4xx and 5xx errors
- **Performance**: Load times, Core Web Vitals

## Continuous Deployment

### Automatic Deployments

Amplify auto-deploys when you:
- Push to `main` branch
- Merge a pull request
- Manually trigger via console

### Disable Auto-Deploy

If you want manual control:
1. Amplify Console → App settings → Build settings
2. Uncheck "Auto build" for branch
3. Click "Save"

### Manual Deployment

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Amplify automatically detects and builds
# Or manually trigger in Amplify Console
```

## Rollback

If deployment breaks:

1. Amplify Console → Branch: main
2. Find previous successful deployment
3. Click **"Redeploy this version"**

## Cost Management

### Cost Breakdown

- **Build minutes**: $0.01/minute
- **Hosting**: $0.15/GB stored + $0.15/GB served
- **Data transfer**: $0.15/GB

### Free Tier

- 1000 build minutes/month
- 15 GB served/month
- 5 GB stored

### Estimated Costs

| Traffic Level | Monthly Cost |
|--------------|--------------|
| Low (< 1000 visits) | $0-1 |
| Medium (1000-10k visits) | $1-5 |
| High (10k-100k visits) | $5-20 |

### Cost Optimization

1. **Enable caching** - Reduces build minutes
2. **Compress images** - Reduces bandwidth
3. **Use CloudFront** - Included with Amplify

## Security Best Practices

### 1. Protect Environment Variables

- ✅ Never commit `.env` files
- ✅ Use Amplify Console for secrets
- ✅ Rotate API keys regularly

### 2. Enable HTTPS

- ✅ Amplify enforces HTTPS automatically
- ✅ HTTP auto-redirects to HTTPS

### 3. Review Access Logs

1. Amplify Console → Monitoring → Access logs
2. Look for suspicious patterns
3. Set up CloudWatch alarms

### 4. Restrict API Access (Optional)

Update backend to only allow Amplify domain:

```yaml
# In backend API Gateway CORS config
AllowOrigin: "'https://your-amplify-url.amplifyapp.com'"
```

## Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Set up custom domain (optional)
3. ✅ Configure branch-based deployments
4. ✅ Set up monitoring alerts
5. ✅ Share URL with users
6. ✅ Update documentation with production URL

## Support Resources

- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [Amplify Hosting Guide](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)

## Cleanup (Delete Amplify App)

If you need to remove the deployment:

1. Amplify Console → Your app
2. Actions → Delete app
3. Confirm deletion

**Note**: This does NOT delete your code or backend - only the Amplify hosting.

---

## Quick Reference

### Get Backend API Info
```bash
aws cloudformation describe-stacks --stack-name pai-chatbot-prod --query 'Stacks[0].Outputs'
```

### Redeploy Manually
```bash
# From AWS CLI
aws amplify start-job --app-id <app-id> --branch-name main --job-type RELEASE
```

### View Build Logs
```bash
aws amplify get-job --app-id <app-id> --branch-name main --job-id <job-id>
```

---

**Congratulations!** 🎉 Your PAI Chatbot frontend is now live on AWS Amplify!
