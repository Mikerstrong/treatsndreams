# TreatsDreams Portainer Stack

This is a Portainer stack configuration for deploying the TreatsDreams workout motivation app.

## Quick Deploy in Portainer

1. **Login to Portainer**
2. **Go to Stacks** → **Add Stack**
3. **Name**: `treatsdreams`
4. **Build Method**: Choose "Repository" 
5. **Repository URL**: `https://github.com/Mikerstrong/treatsndreams`
6. **Compose Path**: `portainer-stack.yml`
7. **Deploy**

## Manual Deploy (Alternative)

If you prefer to deploy manually:

1. **Go to Stacks** → **Add Stack**
2. **Name**: `treatsdreams`
3. **Build Method**: Choose "Web editor"
4. **Copy and paste the portainer-stack.yml content**
5. **Deploy**

## Stack Configuration

The stack includes:
- **Streamlit App**: Workout motivation tracker
- **Port**: 8547 (accessible at http://your-server:8547)
- **Persistent Storage**: Data is saved in Docker volumes
- **Health Checks**: Automatic container health monitoring
- **Auto Restart**: Container restarts automatically if it fails

## Environment Variables

You can customize these in Portainer's stack editor:

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8547
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## Volumes

- `treatsdreams_data`: Persistent storage for users.json and bank.json
- Local bind mount: `./data:/app/data` (optional)

## Accessing the App

After deployment, access your app at:
- **Local**: http://localhost:8547
- **Server**: http://your-server-ip:8547

## Updating the App

To update:
1. Go to your stack in Portainer
2. Click **Editor**
3. Click **Update the stack**
4. Select "Re-pull image and redeploy"

## Troubleshooting

- **Check logs**: Go to Containers → treatsdreams-app → Logs
- **Health status**: Check the container health indicator
- **Port conflicts**: Ensure port 8547 is not used by other services
