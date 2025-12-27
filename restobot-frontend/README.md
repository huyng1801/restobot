# 🍽️ RestoBot Frontend

React-based web interface for RestoBot - Intelligent Restaurant Virtual Assistant

## 🎨 Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Theme switching with Material-UI
- **Authentication**: Login/Register with JWT
- **Chat Interface**: Real-time chat with Rasa chatbot
- **Admin Dashboard**: Restaurant management interface
- **Menu Management**: Browse and filter menu items
- **Table Booking**: Reserve tables online
- **Order Management**: Create and track orders
- **User Profiles**: User account management

## 📋 Tech Stack

- **React** 18+
- **TypeScript** 4.9+
- **Material-UI** 5.14+ (MUI)
- **React Router** 6.20+
- **Axios** for HTTP requests
- **React Toastify** for notifications

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend API running on http://localhost:8000

### Installation

```bash
cd restobot-frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
src/
├── components/          # Reusable components
│   ├── admin/          # Admin components
│   ├── auth/           # Authentication components
│   ├── chat/           # Chat interface
│   ├── common/         # Common components
│   ├── customer/       # Customer components
│   └── layout/         # Layout components
├── pages/              # Page components
│   ├── admin/          # Admin pages
│   ├── auth/           # Auth pages
│   ├── customer/       # Customer pages
│   └── error/          # Error pages
├── services/           # API services
│   └── admin/          # Admin API services
├── context/            # React Context
│   ├── AuthContext
│   ├── ChatContext
│   ├── LoadingContext
│   └── ThemeContext
├── hooks/              # Custom hooks
├── utils/              # Utility functions
├── theme/              # Theme configuration
└── types/              # TypeScript types
```

## 🔌 Environment Variables

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CHAT_API_URL=http://localhost:5005

# App Configuration
REACT_APP_NAME=RestoBot
REACT_APP_VERSION=1.0.0

# Build Configuration
BUILD_PATH=build
PUBLIC_URL=/
```

## 📡 API Integration

### Services Location
- `src/services/` - Main API services
- `src/services/admin/` - Admin-specific services
- `src/utils/api.ts` - API client configuration

### Available Services
- `authService` - Authentication
- `userService` - User management
- `menuService` - Menu items
- `tableService` - Table bookings
- `orderService` - Orders
- `chatService` - Chat/Chatbot
- `dashboardService` - Admin dashboard

## 🎯 Key Components

### AuthContext
Manages user authentication state and token handling

### ChatContext
Manages chat state and messages with the chatbot

### ThemeContext
Handles light/dark theme switching

### LoadingContext
Global loading state management

## 🧩 Custom Hooks

### useAuth
```typescript
const { user, token, login, logout, register } = useAuth();
```

## 🎨 Theming

The app uses Material-UI's theming system. Customize in `src/theme/theme.ts`

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints:
  - xs: 0px
  - sm: 600px
  - md: 960px
  - lg: 1280px
  - xl: 1920px

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage
npm test -- --coverage
```

## 🔨 Build for Production

```bash
# Create production build
npm run build

# Serve the build
npx serve -s build
```

## 🐳 Docker

### Build Docker image
```bash
# Development with hot reload
docker build -f Dockerfile.dev -t restobot-frontend-dev .
docker run -p 3000:3000 -v $(pwd)/src:/app/src restobot-frontend-dev

# Production
docker build -f Dockerfile -t restobot-frontend .
docker run -p 3000:3000 restobot-frontend
```

## 📦 Docker Compose

```bash
# Run with entire stack
docker-compose -f docker-compose.dev.yml up frontend

# Or production
docker-compose up frontend
```

## 🚀 Deployment

### Build for production
```bash
npm run build
```

The `build/` folder contains optimized production build.

### Environment Variables for Production
Update `restobot-frontend/.env` with production URLs:
```env
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_CHAT_API_URL=https://your-domain.com/rasa
```

## 📚 Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject configuration (⚠️ irreversible)
npm run eject
```

## 🐛 Debugging

### Browser DevTools
- React DevTools extension recommended
- Redux DevTools for state management

### Logs
Check browser console (F12) for logs

## 🆘 Troubleshooting

### Module not found
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
# Kill the process
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### API connection errors
- Check if backend is running on correct port
- Verify `REACT_APP_API_URL` in `.env`
- Check CORS settings in backend

## 📖 Documentation

- [React Documentation](https://react.dev)
- [Material-UI Documentation](https://mui.com)
- [React Router Documentation](https://reactrouter.com)
- [Axios Documentation](https://axios-http.com)

## 👥 Contributors

See main README.md for contributor information

## 📄 License

Academic Project License

---

**Last Updated**: December 2024

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
