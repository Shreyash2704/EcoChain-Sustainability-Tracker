/**
 * Blockscout Service
 * Provides real-time blockchain data integration using Blockscout API
 */

export interface Transaction {
  hash: string;
  from: string;
  to: string;
  value: string;
  gasUsed: string;
  gasPrice: string;
  blockNumber: number;
  timestamp: number;
  status: 'pending' | 'confirmed' | 'failed';
  confirmations: number;
  explorerUrl?: string;
}

export interface TokenBalance {
  address: string;
  symbol: string;
  name: string;
  decimals: number;
  balance: string;
  balanceFormatted: string;
}

export interface NFTMetadata {
  tokenId: string;
  name: string;
  description: string;
  image: string;
  attributes: Array<{
    trait_type: string;
    value: string;
  }>;
}

export interface NFT {
  contractAddress: string;
  tokenId: string;
  owner: string;
  metadata: NFTMetadata;
  transactionHash: string;
  blockNumber: number;
}

export interface BlockscoutConfig {
  baseUrl: string;
  apiKey?: string;
  chainId: number;
}

class BlockscoutService {
  private config: BlockscoutConfig;
  private pollingInterval: number | null = null;

  constructor(config: BlockscoutConfig) {
    this.config = config;
  }

  /**
   * Get transaction status and details
   */
  async getTransaction(txHash: string): Promise<Transaction | null> {
    try {
      const response = await fetch(
        `${this.config.baseUrl}/transaction/${txHash}`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch transaction: ${response.statusText}`);
      }

      const data = await response.json();
      return this.formatTransaction(data);
    } catch (error) {
      console.error('Error fetching transaction:', error);
      return null;
    }
  }

  /**
   * Get token balance for an address
   */
  async getTokenBalance(address: string, tokenAddress: string): Promise<TokenBalance | null> {
    try {
      const response = await fetch(
        `${this.config.baseUrl}/token-balance/${address}?token_address=${tokenAddress}`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch token balance: ${response.statusText}`);
      }

      const data = await response.json();
      return this.formatTokenBalance(data);
    } catch (error) {
      console.error('Error fetching token balance:', error);
      return null;
    }
  }

  /**
   * Get NFT collection for an address
   */
  async getNFTs(address: string, contractAddress: string): Promise<NFT[]> {
    try {
      const response = await fetch(
        `${this.config.baseUrl}/nfts/${address}?contract_address=${contractAddress}`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch NFTs: ${response.statusText}`);
      }

      const data = await response.json();
      return this.formatNFTs(data);
    } catch (error) {
      console.error('Error fetching NFTs:', error);
      return [];
    }
  }

  /**
   * Get recent transactions for an address
   */
  async getRecentTransactions(address: string, limit: number = 10): Promise<Transaction[]> {
    try {
      const response = await fetch(
        `${this.config.baseUrl}/recent-transactions/${address}?limit=${limit}`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch transactions: ${response.statusText}`);
      }

      const data = await response.json();
      return data.map((tx: any) => this.formatTransaction(tx)) || [];
    } catch (error) {
      console.error('Error fetching recent transactions:', error);
      return [];
    }
  }

  /**
   * Start polling for transaction status updates
   */
  startPolling(txHash: string, callback: (transaction: Transaction) => void, interval: number = 5000): void {
    this.stopPolling();

    this.pollingInterval = setInterval(async () => {
      const transaction = await this.getTransaction(txHash);
      if (transaction) {
        callback(transaction);
        
        // Stop polling if transaction is confirmed or failed
        if (transaction.status === 'confirmed' || transaction.status === 'failed') {
          this.stopPolling();
        }
      }
    }, interval);
  }

  /**
   * Stop polling for transaction updates
   */
  stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Get explorer URL for a transaction
   */
  getTransactionUrl(txHash: string): string {
    return `https://eth-sepolia.blockscout.com/tx/${txHash}`;
  }

  /**
   * Get explorer URL for a token
   */
  getTokenUrl(tokenAddress: string): string {
    return `https://eth-sepolia.blockscout.com/token/${tokenAddress}`;
  }

  /**
   * Get explorer URL for an NFT
   */
  getNFTUrl(contractAddress: string, tokenId: string): string {
    return `https://eth-sepolia.blockscout.com/token/${contractAddress}/instance/${tokenId}`;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    return headers;
  }

  private formatTransaction(data: any): Transaction {
    return {
      hash: data.hash,
      from: data.from,
      to: data.to || '',
      value: data.value,
      gasUsed: data.gas_used,
      gasPrice: data.gas_price,
      blockNumber: data.block_number,
      timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
      status: data.status,
      confirmations: data.confirmations || 0,
      explorerUrl: data.explorer_url,
    };
  }

  private formatTokenBalance(data: any): TokenBalance {
    return {
      address: data.address,
      symbol: data.symbol,
      name: data.name,
      decimals: data.decimals,
      balance: data.balance,
      balanceFormatted: data.balance_formatted,
    };
  }

  private formatNFTs(data: any): NFT[] {
    return data.map((item: any) => ({
      contractAddress: item.contract_address,
      tokenId: item.token_id,
      owner: item.owner,
      metadata: item.metadata,
      transactionHash: item.transaction_hash,
      blockNumber: item.block_number,
    })) || [];
  }

}

// Default configuration for EcoChain
const defaultConfig: BlockscoutConfig = {
  baseUrl: import.meta.env.VITE_BLOCKSCOUT_PROXY_URL || 'http://localhost:8002/api/blockscout', // Backend proxy to avoid CORS
  chainId: 11155111,
};

// Create singleton instance
export const blockscoutService = new BlockscoutService(defaultConfig);

// Export types and service
export { BlockscoutService };
export default blockscoutService;
