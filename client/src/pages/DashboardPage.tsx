import { usePrivy } from '@privy-io/react-auth';
import { useUserAnalytics, useRecentActivity } from '../hooks/useApi';
import { 
  BarChart3, 
  TrendingUp, 
  FileText, 
  Coins, 
  Award,
  Activity,
  Calendar,
  ExternalLink,
  Loader2,
  AlertCircle,
  Upload,
  MessageCircle,
  Trophy
} from 'lucide-react';

export default function DashboardPage() {
  const { authenticated, user } = usePrivy();
  const walletAddress = user?.wallet?.address || '';
  
  const { data: analytics, isLoading: analyticsLoading, error: analyticsError } = useUserAnalytics(walletAddress);
  const { data: recentActivity, isLoading: activityLoading } = useRecentActivity(walletAddress, 10);

  if (!authenticated) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card text-center">
          <BarChart3 className="w-16 h-16 text-eco-600 dark:text-eco-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Connect Your Wallet to View Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Connect your wallet to view your sustainability analytics and track your progress.
          </p>
        </div>
      </div>
    );
  }

  if (analyticsLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card text-center">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (analyticsError) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card text-center">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Unable to Load Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            There was an error loading your analytics data. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  const summary = analytics?.summary || {};
  const uploadHistory = analytics?.upload_history || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Track your sustainability progress and impact
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500 dark:text-gray-400">Wallet Address</p>
          <p className="font-mono text-sm text-gray-900 dark:text-white">
            {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Credits */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Credits</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {summary.total_credits_earned || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-eco-100 dark:bg-eco-900/20 rounded-lg flex items-center justify-center">
              <Coins className="w-6 h-6 text-eco-600 dark:text-eco-400" />
            </div>
          </div>
        </div>

        {/* Documents Uploaded */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Documents</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {summary.total_documents_uploaded || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>

        {/* Success Rate */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {summary.success_rate ? `${summary.success_rate.toFixed(1)}%` : '0%'}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        {/* Carbon Impact */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Carbon Impact</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {summary.total_carbon_impact || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Blockchain Data */}
      {summary.total_eco_tokens !== "N/A" && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Blockchain Assets
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-eco-50 dark:bg-eco-900/10 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Coins className="w-5 h-5 text-eco-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">ECO Tokens</h3>
              </div>
              <p className="text-2xl font-bold text-eco-600">
                {summary.total_eco_tokens}
              </p>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/10 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Award className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">NFTs Owned</h3>
              </div>
              <p className="text-2xl font-bold text-blue-600">
                {summary.total_nfts_owned}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Upload History */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Recent Uploads
        </h2>
        {uploadHistory.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-300">No uploads yet</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Upload your first sustainability document to get started
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {uploadHistory.slice(0, 5).map((upload: any, index: number) => (
              <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      upload.status === 'completed' ? 'bg-green-500' : 
                      upload.status === 'processing' ? 'bg-yellow-500' : 'bg-red-500'
                    }`} />
                    <span className="font-medium text-gray-900 dark:text-white">
                      Upload #{upload.upload_id?.slice(-8) || index + 1}
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    upload.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
                    upload.status === 'processing' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                    'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                  }`}>
                    {upload.status}
                  </span>
                </div>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-300">Credits:</span>
                    <span className="ml-2 font-medium">{upload.credits_earned || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-300">Impact Score:</span>
                    <span className="ml-2 font-medium">{upload.impact_score || 0}/100</span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-300">Date:</span>
                    <span className="ml-2 font-medium">
                      {upload.upload_timestamp ? 
                        new Date(upload.upload_timestamp).toLocaleDateString() : 
                        'Unknown'
                      }
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      {recentActivity && recentActivity.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Recent Activity
          </h2>
          <div className="space-y-3">
            {recentActivity.slice(0, 5).map((activity: any, index: number) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <Activity className="w-5 h-5 text-eco-600 dark:text-eco-400" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white">
                    {activity.description || 'New activity'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {activity.timestamp ? 
                      new Date(activity.timestamp).toLocaleString() : 
                      'Unknown time'
                    }
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <a
            href="/upload"
            className="btn-primary text-center"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </a>
          <a
            href="/chat"
            className="btn-secondary text-center"
          >
            <MessageCircle className="w-4 h-4 mr-2" />
            Chat with AI
          </a>
          <a
            href="/leaderboard"
            className="btn-secondary text-center"
          >
            <Trophy className="w-4 h-4 mr-2" />
            View Leaderboard
          </a>
        </div>
      </div>
    </div>
  );
}
