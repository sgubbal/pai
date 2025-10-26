# PAI Chatbot Frontend

Modern, responsive web interface for the PAI (Personal AI) Chatbot built with React, TypeScript, and Vite. Deployed serverlessly on AWS Amplify.

## Features

- **Responsive Design**: Works seamlessly on mobile and desktop
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Conversation Management**: Create, switch between, and delete conversations
- **Markdown Support**: Rich text rendering with code syntax highlighting
- **Dark/Light Theme**: Toggle between themes with persistence
- **End-to-End Encryption**: Client-side encryption using Web Crypto API
- **Offline Support**: Conversations cached locally
- **Error Handling**: Automatic retry logic and error recovery
- **Type-Safe**: Built with TypeScript for reliability

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first styling
- **React Markdown** - Markdown rendering
- **Syntax Highlighter** - Code block highlighting
- **AWS Amplify** - Serverless hosting

## Prerequisites

- Node.js 18+ (only if developing locally)
- npm or yarn
- AWS Account (for deployment)
- PAI Backend API deployed

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
VITE_API_KEY=your-api-key-here
```

You can get these values from your backend CloudFormation stack outputs.

## Local Development (Optional)

If you want to develop locally:

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

The app will be available at `http://localhost:5173`

## Deployment to AWS Amplify

### Step 1: Push Code to GitHub

```bash
# Make sure you're in the PAI repository root
cd /Users/sgubbala/pai

# Add and commit the frontend
git add frontend/
git commit -m "Add React frontend with Amplify configuration"
git push origin main
```

### Step 2: Create Amplify App

1. Go to AWS Console → AWS Amplify
2. Click "New app" → "Host web app"
3. Choose "GitHub" as the repository service
4. Authorize AWS Amplify to access your GitHub account
5. Select your repository: `pai`
6. Select branch: `main` (or your preferred branch)

### Step 3: Configure Build Settings

AWS Amplify should auto-detect the `amplify.yml` configuration. Verify it shows:

- **Build command**: `npm run build`
- **Build output directory**: `dist`
- **Base directory**: `frontend`

If not auto-detected, set:
- **App build specification**: Use the `amplify.yml` from the repo
- **Monorepo**: Enable and set base directory to `frontend`

### Step 4: Configure Environment Variables

In the Amplify Console, go to:
1. Your App → App settings → Environment variables
2. Add the following variables:

```
VITE_API_URL = https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
VITE_API_KEY = your-api-key-here
```

**Important**: Get these values from your backend CloudFormation outputs:

```bash
# Get API URL
aws cloudformation describe-stacks \
  --stack-name pai-chatbot-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# API Key is stored in AWS Secrets Manager
# Use the same value you used when deploying the backend
```

### Step 5: Deploy

1. Click "Save and deploy"
2. Amplify will automatically:
   - Clone your repository
   - Install dependencies
   - Build your app
   - Deploy to global CDN
3. Wait for deployment to complete (2-5 minutes)
4. You'll get a URL like: `https://main.d1234567890.amplifyapp.com`

### Step 6: (Optional) Add Custom Domain

1. In Amplify Console → Domain management
2. Click "Add domain"
3. Enter your domain (e.g., `chat.yourdomain.com`)
4. Follow DNS configuration instructions
5. Wait for SSL certificate provisioning

## Automatic Deployments

Amplify is configured for continuous deployment:
- **Push to main** → Auto-deploy to production
- **Create PR** → Auto-deploy preview environment
- **Merge PR** → Auto-deploy to production

You can configure different branches for dev/staging/prod environments.

## Architecture

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Header.tsx
│   │   ├── ConversationsList.tsx
│   │   ├── MessageList.tsx
│   │   ├── Message.tsx
│   │   ├── ChatInput.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorBoundary.tsx
│   ├── services/          # API clients
│   │   └── api.ts
│   ├── utils/             # Utilities
│   │   ├── encryption.ts
│   │   ├── storage.ts
│   │   └── helpers.ts
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── styles/            # Global styles
│   │   └── index.css
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── config.ts          # App configuration
├── public/                # Static assets
├── index.html             # HTML template
├── amplify.yml            # Amplify build config
├── package.json           # Dependencies
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
└── tsconfig.json          # TypeScript configuration
```

## Features Breakdown

### Conversation Management
- Create new conversations
- Switch between conversations
- Delete conversations
- Auto-save to local storage
- Sync with backend API

### Chat Interface
- Send messages with Enter key
- Shift+Enter for new lines
- Auto-resize text input
- Character counter
- Copy message content
- Markdown rendering
- Code syntax highlighting
- Typing indicators

### Theme System
- Light/Dark mode toggle
- System preference detection
- Persistent theme selection
- Smooth transitions

### Error Handling
- API error handling
- Retry logic (3 attempts)
- Network error recovery
- User-friendly error messages
- Configuration validation

### Security
- Client-side encryption (Web Crypto API)
- API key authentication
- HTTPS only (enforced by Amplify)
- Environment variable management

## Cost Estimate

AWS Amplify Pricing (as of 2024):
- **Build**: $0.01 per build minute
- **Hosting**: $0.15 per GB stored + $0.15 per GB served
- **Free tier**: 1000 build minutes, 15 GB served/month

**Estimated monthly cost**: $1-5 for low-medium traffic

## Monitoring

Access Amplify Console to monitor:
- Build history and logs
- Deployment status
- Access logs
- Error rates
- Performance metrics

## Troubleshooting

### Build fails with "npm ci" error
- Check Node.js version in Amplify (should be 18+)
- Update build settings: "Build image settings" → Set to latest

### Environment variables not working
- Ensure variables start with `VITE_`
- Redeploy app after adding variables
- Check Amplify Console → Environment variables

### API calls failing
- Verify `VITE_API_URL` is correct
- Check `VITE_API_KEY` matches backend
- Verify backend API Gateway is deployed
- Check CORS configuration in backend

### Dark mode not persisting
- Check browser local storage permissions
- Clear browser cache and try again

## Development Tips

### Testing locally with backend
1. Deploy backend first
2. Get API URL and key from CloudFormation outputs
3. Create `.env` file with those values
4. Run `npm run dev`

### Hot Module Replacement (HMR)
Vite provides instant HMR - changes appear immediately without full reload.

### Type checking
```bash
npm run type-check  # TypeScript type checking
```

### Bundle analysis
```bash
npm run build
# Check dist/ folder size and contents
```

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Rotate API keys regularly** - Update in Amplify environment variables
3. **Use HTTPS only** - Amplify enforces this automatically
4. **Review Amplify access logs** - Monitor for suspicious activity
5. **Enable AWS WAF** (optional) - For additional DDoS protection

## Support

For issues or questions:
1. Check CloudWatch logs in Amplify Console
2. Review backend API Gateway logs
3. Check browser console for errors
4. Verify environment variables are set correctly

## License

Same as parent PAI project.
