import { PrivyProvider } from '@privy-io/react-auth';
import { WagmiProvider } from '@privy-io/wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createConfig, http } from 'wagmi';
import { sepolia } from 'wagmi/chains';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

// Configure wagmi
const config = createConfig({
  chains: [sepolia],
  transports: {
    [sepolia.id]: http(),
  },
});

// Privy configuration
export const privyConfig = {
  appId: import.meta.env.VITE_PRIVY_APP_ID || 'clx1234567890', // Fallback for development
  config: {
    // Customize the appearance of the login modal
    appearance: {
      theme: 'light' as const,
      accentColor: '#22c55e' as const, // Eco green
    },
    // Configure login methods
    loginMethods: ['email', 'wallet'],
    // Configure embedded wallets
    embeddedWallets: {
      createOnLogin: 'users-without-wallets',
    },
    // Configure supported chains
    defaultChain: sepolia,
    supportedChains: [sepolia],
  } as any,
};

// Provider wrapper component
export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <PrivyProvider
      appId={privyConfig.appId}
      config={privyConfig.config}
    >
      <QueryClientProvider client={queryClient}>
        <WagmiProvider config={config}>
          {children}
          <ReactQueryDevtools initialIsOpen={false} />
        </WagmiProvider>
      </QueryClientProvider>
    </PrivyProvider>
  );
}

export { queryClient, config };