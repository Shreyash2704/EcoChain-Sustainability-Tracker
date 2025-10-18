# 📊 EcoChain Analytics API Documentation

## 🎯 Overview

The Analytics API provides comprehensive insights into user activity, sustainability impact, and system-wide statistics. Perfect for building dashboards, leaderboards, and user profiles.

## 🚀 Available Endpoints

### 1. **User Analytics** - `/analytics/user/{user_wallet}`

Get detailed analytics for a specific user including upload history, blockchain data, and statistics.

**Example Request:**
```bash
GET /analytics/user/0x6C2E94dB5c3B89D2bC765e5B5E47058aF5E92DdD
```

**Response Structure:**
```json
{
  "user_wallet": "0x6C2E94dB5c3B89D2bC765e5B5E47058aF5E92DdD",
  "summary": {
    "total_documents_uploaded": 5,
    "successful_uploads": 4,
    "total_eco_tokens": "150.5 ECO",
    "total_credits_earned": 150.5,
    "total_nfts_owned": 4,
    "total_carbon_impact": 250.0,
    "recent_activity_30_days": 3,
    "success_rate": 80.0
  },
  "blockchain_data": {
    "eco_token_balance": {
      "balance": "150500000000000000000",
      "balance_formatted": "150.5 ECO",
      "name": "EcoCredit",
      "symbol": "ECO"
    },
    "nft_collection": {
      "count": 4,
      "nfts": [
        {
          "token_id": 1,
          "token_uri": "https://gateway.lighthouse.storage/ipfs/...",
          "metadata": {...}
        }
      ]
    }
  },
  "upload_history": [
    {
      "upload_id": "upload_123",
      "filename": "sustainability_report.pdf",
      "upload_timestamp": "2024-01-15T10:30:00Z",
      "credits_earned": 50.0,
      "impact_score": 85,
      "ipfs_url": "https://gateway.lighthouse.storage/ipfs/...",
      "blockchain_transactions": {
        "eco_token_tx": "0xabc123...",
        "nft_tx": "0xdef456...",
        "nft_token_id": 1,
        "eco_token_explorer": "https://sepolia.etherscan.io/tx/0xabc123...",
        "nft_explorer": "https://sepolia.etherscan.io/tx/0xdef456..."
      },
      "analysis": {
        "carbon_footprint": 100.0,
        "reasoning": "Significant carbon reduction achieved...",
        "document_type": "sustainability_document"
      }
    }
  ]
}
```

### 2. **Leaderboard** - `/analytics/leaderboard`

Get ranked list of top users based on various metrics.

**Query Parameters:**
- `limit` (int): Number of users to return (1-100, default: 10)
- `sort_by` (string): Sort criteria - `credits`, `uploads`, `nfts`, `carbon_impact` (default: `credits`)

**Example Request:**
```bash
GET /analytics/leaderboard?sort_by=credits&limit=10
```

**Response Structure:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_wallet": "0x6C2E94dB5c3B89D2bC765e5B5E47058aF5E92DdD",
      "total_uploads": 5,
      "successful_uploads": 4,
      "total_credits": 150.5,
      "total_nfts": 4,
      "total_carbon_impact": 250.0,
      "success_rate": 80.0,
      "first_upload": "2024-01-01T00:00:00Z",
      "last_upload": "2024-01-15T10:30:00Z"
    }
  ],
  "total_users": 25,
  "total_uploads": 150,
  "sort_by": "credits",
  "limit": 10
}
```

### 3. **System Overview** - `/analytics/stats/overview`

Get system-wide statistics and blockchain data.

**Example Request:**
```bash
GET /analytics/stats/overview
```

**Response Structure:**
```json
{
  "system_overview": {
    "total_users": 25,
    "total_uploads": 150,
    "successful_uploads": 120,
    "success_rate": 80.0,
    "total_credits_distributed": 5000.0,
    "total_carbon_impact": 10000.0,
    "recent_activity_7_days": 15
  },
  "blockchain_stats": {
    "total_eco_tokens_minted": "5000000000000000000000",
    "total_nfts_minted": 120,
    "eco_contract": "0x17874E9d6e22bf8025Fe7473684e50f36472CCd2",
    "nft_contract": "0x17874E9d6e22bf8025Fe7473684e50f36472CCd2"
  }
}
```

### 4. **Recent Activity** - `/analytics/user/{user_wallet}/recent`

Get recent activity for a specific user within a specified time period.

**Query Parameters:**
- `days` (int): Number of days to look back (1-365, default: 30)

**Example Request:**
```bash
GET /analytics/user/0x6C2E94dB5c3B89D2bC765e5B5E47058aF5E92DdD/recent?days=7
```

**Response Structure:**
```json
{
  "user_wallet": "0x6C2E94dB5c3B89D2bC765e5B5E47058aF5E92DdD",
  "period_days": 7,
  "recent_uploads": 2,
  "recent_credits_earned": 75.0,
  "recent_carbon_impact": 125.0,
  "uploads": [
    {
      "upload_id": "upload_456",
      "filename": "recent_report.pdf",
      "credits_earned": 50.0,
      "timestamp": "2024-01-14T15:20:00Z"
    }
  ]
}
```

## 🎯 Use Cases

### **Dashboard Integration**
```javascript
// Get user profile data
const userAnalytics = await fetch('/analytics/user/0x123...');
const userData = await userAnalytics.json();

// Display user stats
document.getElementById('total-uploads').textContent = userData.summary.total_documents_uploaded;
document.getElementById('total-credits').textContent = userData.summary.total_credits_earned;
document.getElementById('nft-count').textContent = userData.summary.total_nfts_owned;
```

### **Leaderboard Widget**
```javascript
// Get top users by credits
const leaderboard = await fetch('/analytics/leaderboard?sort_by=credits&limit=10');
const topUsers = await leaderboard.json();

// Display leaderboard
topUsers.leaderboard.forEach(user => {
  console.log(`#${user.rank} ${user.user_wallet}: ${user.total_credits} credits`);
});
```

### **System Monitoring**
```javascript
// Get system overview
const overview = await fetch('/analytics/stats/overview');
const systemStats = await overview.json();

// Monitor system health
console.log(`Total Users: ${systemStats.system_overview.total_users}`);
console.log(`Success Rate: ${systemStats.system_overview.success_rate}%`);
console.log(`Recent Activity: ${systemStats.system_overview.recent_activity_7_days} uploads`);
```

## 🔧 Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **404**: User not found
- **500**: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## 📊 Data Sources

The Analytics API combines data from multiple sources:

1. **Backend Database** (`upload_sessions`): Upload history, analysis results, metadata
2. **Blockchain Data**: Token balances, NFT ownership, transaction history
3. **IPFS Storage**: Document metadata and links
4. **Real-time Calculations**: Statistics computed on-demand

## 🚀 Performance Notes

- **Caching**: Consider implementing Redis caching for frequently accessed data
- **Pagination**: Large datasets are automatically limited (max 100 users in leaderboard)
- **Async Processing**: All blockchain calls are asynchronous for better performance
- **Error Resilience**: Individual user data failures don't affect system-wide stats

## 🎯 Integration Examples

### **React Dashboard Component**
```jsx
function UserDashboard({ userWallet }) {
  const [analytics, setAnalytics] = useState(null);
  
  useEffect(() => {
    fetch(`/analytics/user/${userWallet}`)
      .then(res => res.json())
      .then(setAnalytics);
  }, [userWallet]);
  
  if (!analytics) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>User Profile</h2>
      <p>Total Uploads: {analytics.summary.total_documents_uploaded}</p>
      <p>Total Credits: {analytics.summary.total_credits_earned}</p>
      <p>NFTs Owned: {analytics.summary.total_nfts_owned}</p>
    </div>
  );
}
```

### **Leaderboard Component**
```jsx
function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState(null);
  
  useEffect(() => {
    fetch('/analytics/leaderboard?sort_by=credits&limit=10')
      .then(res => res.json())
      .then(setLeaderboard);
  }, []);
  
  return (
    <div>
      <h2>Top Users by Credits</h2>
      {leaderboard?.leaderboard.map(user => (
        <div key={user.user_wallet}>
          #{user.rank} {user.user_wallet}: {user.total_credits} credits
        </div>
      ))}
    </div>
  );
}
```

This Analytics API provides everything you need to build comprehensive user dashboards, leaderboards, and system monitoring tools! 🚀
