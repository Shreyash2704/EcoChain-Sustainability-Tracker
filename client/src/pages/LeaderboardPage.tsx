import { useLeaderboard, useSystemOverview } from '../hooks/useApi';
import { 
  Trophy, 
  Medal, 
  Award, 
  TrendingUp, 
  Users, 
  FileText,
  Coins,
  Loader2,
  AlertCircle,
  Crown,
  Star
} from 'lucide-react';

export default function LeaderboardPage() {
  const { data: leaderboard, isLoading: leaderboardLoading, error: leaderboardError } = useLeaderboard(20);
  const { data: systemOverview, isLoading: overviewLoading } = useSystemOverview();

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="w-6 h-6 text-yellow-500" />;
      case 2:
        return <Medal className="w-6 h-6 text-gray-400" />;
      case 3:
        return <Award className="w-6 h-6 text-amber-600" />;
      default:
        return <span className="w-6 h-6 flex items-center justify-center text-sm font-bold text-gray-500">
          {rank}
        </span>;
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800';
      case 2:
        return 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700';
      case 3:
        return 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-800';
      default:
        return 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700';
    }
  };

  if (leaderboardLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card text-center">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  if (leaderboardError) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card text-center">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Unable to Load Leaderboard
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            There was an error loading the leaderboard data. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  const topUsers = leaderboard?.top_users || [];
  const totalUsers = systemOverview?.total_users || 0;
  const totalDocuments = systemOverview?.total_documents || 0;
  const totalCredits = systemOverview?.total_credits_earned || 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center">
            <Trophy className="w-8 h-8 text-white" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Sustainability Leaderboard
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          See who's making the biggest impact on sustainability
        </p>
      </div>

      {/* System Overview */}
      {!overviewLoading && systemOverview && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card text-center">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {totalUsers}
            </h3>
            <p className="text-gray-600 dark:text-gray-300">Active Users</p>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
              <FileText className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {totalDocuments}
            </h3>
            <p className="text-gray-600 dark:text-gray-300">Documents Uploaded</p>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-eco-100 dark:bg-eco-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Coins className="w-6 h-6 text-eco-600 dark:text-eco-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {totalCredits}
            </h3>
            <p className="text-gray-600 dark:text-gray-300">Total Credits Earned</p>
          </div>
        </div>
      )}

      {/* Top 3 Podium */}
      {topUsers.length >= 3 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center">
            Top 3 Champions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 2nd Place */}
            {topUsers[1] && (
              <div className="text-center order-2 md:order-1">
                <div className="relative mb-4">
                  <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto">
                    <Medal className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gray-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    2
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  {topUsers[1].wallet_address?.slice(0, 6)}...{topUsers[1].wallet_address?.slice(-4)}
                </h3>
                <p className="text-2xl font-bold text-gray-400 mb-2">
                  {topUsers[1].total_credits_earned || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">Credits</p>
              </div>
            )}

            {/* 1st Place */}
            {topUsers[0] && (
              <div className="text-center order-1 md:order-2">
                <div className="relative mb-4">
                  <div className="w-24 h-24 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center mx-auto">
                    <Crown className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    1
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  {topUsers[0].wallet_address?.slice(0, 6)}...{topUsers[0].wallet_address?.slice(-4)}
                </h3>
                <p className="text-3xl font-bold text-yellow-600 mb-2">
                  {topUsers[0].total_credits_earned || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">Credits</p>
              </div>
            )}

            {/* 3rd Place */}
            {topUsers[2] && (
              <div className="text-center order-3">
                <div className="relative mb-4">
                  <div className="w-20 h-20 bg-amber-100 dark:bg-amber-900/20 rounded-full flex items-center justify-center mx-auto">
                    <Award className="w-8 h-8 text-amber-600" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-amber-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    3
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  {topUsers[2].wallet_address?.slice(0, 6)}...{topUsers[2].wallet_address?.slice(-4)}
                </h3>
                <p className="text-2xl font-bold text-amber-600 mb-2">
                  {topUsers[2].total_credits_earned || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">Credits</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Full Leaderboard */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
          Complete Leaderboard
        </h2>
        
        {topUsers.length === 0 ? (
          <div className="text-center py-8">
            <Trophy className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-300">No users yet</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Be the first to upload a sustainability document!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {topUsers.map((user: any, index: number) => (
              <div
                key={index}
                className={`flex items-center justify-between p-4 rounded-lg border-2 ${getRankColor(index + 1)}`}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center justify-center w-8">
                    {getRankIcon(index + 1)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {user.wallet_address?.slice(0, 6)}...{user.wallet_address?.slice(-4)}
                      </h3>
                      {index < 3 && (
                        <Star className="w-4 h-4 text-yellow-500" />
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
                      <span>{user.total_documents_uploaded || 0} documents</span>
                      <span>•</span>
                      <span>{user.success_rate ? `${user.success_rate.toFixed(1)}%` : '0%'} success</span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {user.total_credits_earned || 0}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">credits</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Call to Action */}
      <div className="card text-center bg-gradient-to-r from-eco-50 to-eco-100 dark:from-eco-900/10 dark:to-eco-800/10">
        <Trophy className="w-12 h-12 text-eco-600 dark:text-eco-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Want to Climb the Leaderboard?
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Upload sustainability documents, improve your metrics, and earn more credits to rise in the rankings!
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="/upload" className="btn-primary">
            Upload Document
          </a>
          <a href="/chat" className="btn-secondary">
            Get Recommendations
          </a>
        </div>
      </div>
    </div>
  );
}
