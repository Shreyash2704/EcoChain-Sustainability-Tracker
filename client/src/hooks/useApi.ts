import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatApi, uploadApi, analyticsApi, healthApi } from '../services/api';

// Query keys
export const queryKeys = {
  health: ['health'] as const,
  chatHealth: ['chat', 'health'] as const,
  chatHistory: (walletAddress: string) => ['chat', 'history', walletAddress] as const,
  agentsStatus: ['chat', 'agents', 'status'] as const,
  userAnalytics: (walletAddress: string) => ['analytics', 'user', walletAddress] as const,
  leaderboard: (limit: number) => ['analytics', 'leaderboard', limit] as const,
  systemOverview: ['analytics', 'overview'] as const,
  recentActivity: (walletAddress: string, limit: number) => ['analytics', 'recent', walletAddress, limit] as const,
  uploadStatus: (uploadId: string) => ['upload', 'status', uploadId] as const,
};

// Health check hooks
export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: healthApi.check,
    refetchInterval: 30000, // Check every 30 seconds
  });
};

export const useChatHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.chatHealth,
    queryFn: healthApi.checkChat,
    refetchInterval: 30000,
  });
};

// Chat hooks
export const useChatHistory = (walletAddress: string, limit = 10) => {
  return useQuery({
    queryKey: queryKeys.chatHistory(walletAddress),
    queryFn: () => chatApi.getHistory(walletAddress, limit),
    enabled: !!walletAddress,
  });
};

export const useAgentsStatus = () => {
  return useQuery({
    queryKey: queryKeys.agentsStatus,
    queryFn: chatApi.getAgentsStatus,
    refetchInterval: 60000, // Check every minute
  });
};

export const useSendMessage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ walletAddress, message, file }: { walletAddress: string; message: string; file?: File }) =>
      chatApi.sendMessage(walletAddress, message, file),
    onSuccess: (_, variables) => {
      // Invalidate chat history to refetch
      queryClient.invalidateQueries({
        queryKey: queryKeys.chatHistory(variables.walletAddress),
      });
    },
  });
};

export const useClearChatHistory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (walletAddress: string) => chatApi.clearHistory(walletAddress),
    onSuccess: (_, walletAddress) => {
      // Invalidate chat history
      queryClient.invalidateQueries({
        queryKey: queryKeys.chatHistory(walletAddress),
      });
    },
  });
};

// Analytics hooks
export const useUserAnalytics = (walletAddress: string) => {
  return useQuery({
    queryKey: queryKeys.userAnalytics(walletAddress),
    queryFn: () => analyticsApi.getUserAnalytics(walletAddress),
    enabled: !!walletAddress,
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useLeaderboard = (limit = 10) => {
  return useQuery({
    queryKey: queryKeys.leaderboard(limit),
    queryFn: () => analyticsApi.getLeaderboard(limit),
    refetchInterval: 300000, // Refetch every 5 minutes
  });
};

export const useSystemOverview = () => {
  return useQuery({
    queryKey: queryKeys.systemOverview,
    queryFn: analyticsApi.getSystemOverview,
    refetchInterval: 300000, // Refetch every 5 minutes
  });
};

export const useRecentActivity = (walletAddress: string, limit = 20) => {
  return useQuery({
    queryKey: queryKeys.recentActivity(walletAddress, limit),
    queryFn: () => analyticsApi.getRecentActivity(walletAddress, limit),
    refetchInterval: 60000, // Refetch every minute
    enabled: !!walletAddress, // Only run if wallet address is provided
  });
};

// Upload hooks
export const useUploadFile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ file, walletAddress }: { file: File; walletAddress: string }) =>
      uploadApi.uploadFile(file, walletAddress),
    onSuccess: (_, variables) => {
      // Invalidate user analytics to show updated data
      queryClient.invalidateQueries({
        queryKey: queryKeys.userAnalytics(variables.walletAddress),
      });
      // Invalidate system overview
      queryClient.invalidateQueries({
        queryKey: queryKeys.systemOverview,
      });
      // Invalidate recent activity
      queryClient.invalidateQueries({
        queryKey: queryKeys.recentActivity(20),
      });
    },
  });
};

export const useUploadStatus = (uploadId: string) => {
  return useQuery({
    queryKey: queryKeys.uploadStatus(uploadId),
    queryFn: () => uploadApi.getUploadStatus(uploadId),
    enabled: !!uploadId,
    refetchInterval: 5000, // Check every 5 seconds
  });
};
