# EcoChain Frontend Setup

## Overview
The EcoChain frontend is a React + Vite + TypeScript application with TailwindCSS styling and Privy wallet integration.

## Features Implemented

### ✅ Core Setup
- React 19.1.1 + Vite + TypeScript
- TailwindCSS with custom eco theme
- Privy wallet authentication
- React Query for data fetching
- React Router for navigation

### ✅ Pages
- **HomePage**: Landing page with features and call-to-action
- **ChatPage**: AI chat interface with message history
- **UploadPage**: Document upload with drag-and-drop
- **DashboardPage**: User analytics and stats
- **LeaderboardPage**: Community rankings

### ✅ Components
- **Layout**: Navigation bar with wallet connection
- **API Service**: Centralized API calls
- **React Query Hooks**: Data fetching and caching

## Environment Setup

Create a `.env` file in the client directory:

```env
# Privy Configuration
VITE_PRIVY_APP_ID=your_privy_app_id_here

# API Configuration
VITE_API_BASE_URL=http://localhost:8002

# Development
VITE_DEBUG=true
```

## Getting Started

1. **Install dependencies** (already done):
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   - Get a Privy App ID from https://privy.io
   - Add it to your `.env` file

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## API Integration

The frontend integrates with the backend API endpoints:

- **Chat API**: `/chat/query`, `/chat/history`
- **Upload API**: `/upload/`
- **Analytics API**: `/analytics/user`, `/analytics/leaderboard`

## Wallet Integration

Uses Privy for wallet authentication with support for:
- Email login
- Wallet connection
- Embedded wallets
- Sepolia testnet

## Styling

Uses TailwindCSS with a custom eco theme:
- Primary colors: Green eco palette
- Dark mode support
- Responsive design
- Custom components and utilities

## Next Steps

1. **Test the application**:
   - Start both backend and frontend
   - Connect wallet
   - Test chat functionality
   - Upload a document
   - View dashboard and leaderboard

2. **Deploy to production**:
   - Set up production environment variables
   - Build and deploy to your hosting platform
   - Configure Privy for production

## Troubleshooting

### Common Issues

1. **Wallet connection fails**:
   - Check Privy App ID in environment variables
   - Ensure backend is running on correct port

2. **API calls fail**:
   - Verify backend is running on http://localhost:8002
   - Check CORS configuration in backend

3. **Styling issues**:
   - Ensure TailwindCSS is properly configured
   - Check if dark mode classes are applied

### Development Tips

- Use React Query DevTools for debugging API calls
- Check browser console for errors
- Use Privy dashboard to monitor wallet connections
- Test with different wallet types (MetaMask, embedded, etc.)
