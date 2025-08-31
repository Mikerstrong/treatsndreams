# TreatsDreams 🏋️

A workout motivation app that gamifies fitness with points, levels, treats, and dreams - now with Samsung Watch integration!

## Features

### 🏃‍♂️ Samsung Watch Integration (NEW!)
- **Automatic Step Sync**: Seamlessly sync daily steps from your Samsung smartwatch
- **Daily Step Goals**: Set and track customizable step targets (default: 10,000 steps)
- **Automatic Rewards**: Earn 5 points when you reach your daily step goal
- **Weekly History**: View your step progress over the last 7 days
- **No Manual Connection**: Steps sync automatically - no phone connection required!

### 🎮 Gamified Fitness System
- **User Levels**: Progress through 20+ levels with unique titles and icons
- **Activity Points**: Earn points by completing workouts and achieving step goals
- **Level Rewards**: Get bonus points when you level up

### 🎁 Personal Treats
- **Custom Rewards**: Set up personal treats you can "buy" with activity points
- **Progress Tracking**: Visual progress bars show how close you are to earning treats
- **Instant Purchase**: Buy treats when you have enough points

### 🌟 Shared Dreams
- **Combined Goal Bank**: All users contribute points to shared dream goals
- **Big Rewards**: Save up for larger goals like weekend trips or experiences
- **Team Motivation**: Work together with family/friends to achieve dreams

### 👥 Multi-User Support
- **Family Friendly**: Support for multiple users with individual progress
- **Personal Data**: Each user has their own points, level, treats, and step goals
- **Admin Controls**: Manage users and reset data when needed

## Quick Start

### Using Docker (Recommended)
```bash
docker run -p 8547:8547 -v treatsdreams_data:/app/data mikerstrong/treatsndreams
```

### Using Portainer
See [PORTAINER.md](PORTAINER.md) for detailed deployment instructions.

### Local Development
```bash
pip install streamlit
streamlit run main.py --server.port 8547
```

## Samsung Watch Setup

1. **Add a User**: Click "➕ Add New User" and create your profile
2. **View Steps**: Your Samsung watch steps will automatically appear in the "👟 Samsung Watch Steps" section
3. **Set Goals**: Expand "⚙️ Step Goal Settings" to customize your daily step target
4. **Earn Points**: Reach your daily goal to automatically earn 5 points!

*Note: Current implementation simulates Samsung Health API. For production use, integrate with actual Samsung Health SDK.*

## Data Storage

All data is stored in JSON files in the `data/` directory:
- `users.json` - User accounts
- `bank.json` - Activities, dreams, user points, and step goals
- `activity.json` - Activity history logs
- `steps.json` - Daily step data from Samsung watches

## Screenshots

![Samsung Watch Integration](https://github.com/user-attachments/assets/2af580c0-6345-4552-bfe8-5c53369ca180)

## Documentation

- [Samsung Watch Integration Guide](SAMSUNG_WATCH_INTEGRATION.md) - Detailed documentation for step tracking features
- [Portainer Deployment](PORTAINER.md) - Container deployment instructions

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Data Storage**: JSON files with persistent Docker volumes
- **Samsung Integration**: Samsung Health API simulation (ready for real API integration)
- **Deployment**: Docker containers with Portainer support

## Environment Variables

- `DATA_DIR` - Directory for data files (default: `data`)
- `STREAMLIT_SERVER_PORT` - Port for web interface (default: `8547`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the functionality
5. Submit a pull request

## License

This project is open source. Feel free to use and modify for personal or commercial use.

---

Made with ❤️ using Streamlit. Transform your fitness journey into an engaging game!