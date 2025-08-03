# 🚀 Vercel Deployment Guide

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Vercel CLI** (optional): `npm i -g vercel`

## 🔧 Deployment Steps

### **Option 1: Deploy via Vercel Dashboard**

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Build Settings**:
   - **Framework Preset**: Other
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

3. **Environment Variables** (if needed):
   - Add any environment variables in the Vercel dashboard

4. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy your application

### **Option 2: Deploy via Vercel CLI**

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Confirm deployment settings
   - Wait for build and deployment

## ⚠️ Important Notes

### **Limitations on Vercel**:

1. **Serverless Functions**: 
   - Functions have a 10-second timeout by default
   - Maximum execution time is 30 seconds
   - No persistent state between function calls

2. **Real-time Features**:
   - The polling system won't work as expected
   - Data will be reset on each function call
   - Consider using external services for real-time features

3. **File System**:
   - Read-only file system
   - No persistent storage
   - Use external databases for data persistence

### **Recommended Modifications for Production**:

1. **Database Integration**:
   ```python
   # Use external database instead of in-memory storage
   import pymongo  # or psycopg2 for PostgreSQL
   ```

2. **Real-time Updates**:
   ```javascript
   // Use WebSockets or Server-Sent Events
   const eventSource = new EventSource('/api/updates');
   ```

3. **Environment Variables**:
   ```python
   # Use environment variables for configuration
   DATABASE_URL = os.getenv('DATABASE_URL')
   ```

## 🔄 Alternative Deployment Options

### **For Full Functionality**:

1. **Railway**: Better for Python apps with persistent storage
2. **Render**: Good for Flask applications
3. **Heroku**: Traditional choice for Python web apps
4. **DigitalOcean App Platform**: Simple deployment with databases

### **For Frontend Only**:

1. **Deploy React to Vercel**:
   - Move React code to separate repository
   - Deploy frontend to Vercel
   - Use external API for backend

2. **Use External Backend**:
   - Deploy Flask app to Railway/Render
   - Update API_BASE_URL in frontend
   - Deploy frontend to Vercel

## 📁 Project Structure for Vercel

```
payment-simulator/
├── api/
│   └── index.py          # Vercel serverless function
├── static/
│   └── js/
│       └── app.js        # React frontend
├── templates/
│   └── index.html        # HTML template
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README_VERCEL.md     # This file
```

## 🎯 Quick Start

1. **Fork/Clone** this repository
2. **Push** to your GitHub account
3. **Connect** to Vercel
4. **Deploy** with one click
5. **Access** your live application

## 🔗 Useful Links

- [Vercel Documentation](https://vercel.com/docs)
- [Python on Vercel](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Serverless Functions](https://vercel.com/docs/concepts/functions)

## 🐛 Troubleshooting

### **Common Issues**:

1. **Build Failures**:
   - Check `requirements.txt` for all dependencies
   - Ensure Python version compatibility

2. **Function Timeouts**:
   - Reduce simulation time in the code
   - Use external services for long-running tasks

3. **CORS Issues**:
   - Ensure CORS is properly configured
   - Check API endpoints are accessible

4. **Static Files Not Loading**:
   - Verify file paths in `vercel.json`
   - Check static file serving configuration

## 📞 Support

For deployment issues:
- Check Vercel deployment logs
- Review function execution logs
- Test locally with `vercel dev`

For application issues:
- Check browser console for errors
- Verify API endpoints are working
- Test with external tools like Postman 