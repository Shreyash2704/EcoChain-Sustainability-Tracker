import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, XCircle, ExternalLink, Copy } from 'lucide-react';
import { blockscoutService, type Transaction } from '../services/blockscout';

interface TransactionStatusProps {
  txHash: string;
  onStatusChange?: (status: Transaction['status']) => void;
  showDetails?: boolean;
  className?: string;
}

export const TransactionStatus: React.FC<TransactionStatusProps> = ({
  txHash,
  onStatusChange,
  showDetails = true,
  className = '',
}) => {
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!txHash) return;

    // Initial fetch
    fetchTransaction();

    // Start polling for updates
    blockscoutService.startPolling(txHash, (tx) => {
      setTransaction(tx);
      setLoading(false);
      onStatusChange?.(tx.status);
    });

    return () => {
      blockscoutService.stopPolling();
    };
  }, [txHash, onStatusChange]);

  const fetchTransaction = async () => {
    try {
      setLoading(true);
      setError(null);
      const tx = await blockscoutService.getTransaction(txHash);
      setTransaction(tx);
    } catch (err) {
      setError('Failed to fetch transaction status');
      console.error('Transaction fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getStatusIcon = (status: Transaction['status']) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500 animate-pulse" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: Transaction['status']) => {
    switch (status) {
      case 'confirmed':
        return 'Confirmed';
      case 'pending':
        return 'Pending';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status: Transaction['status']) => {
    switch (status) {
      case 'confirmed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (loading && !transaction) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
        <span className="text-sm text-gray-600">Loading transaction...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center space-x-2 text-red-600 ${className}`}>
        <XCircle className="w-5 h-5" />
        <span className="text-sm">{error}</span>
      </div>
    );
  }

  if (!transaction) {
    return (
      <div className={`flex items-center space-x-2 text-gray-600 ${className}`}>
        <Clock className="w-5 h-5" />
        <span className="text-sm">Transaction not found</span>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Status Badge */}
      <div className={`inline-flex items-center space-x-2 px-3 py-2 rounded-lg border ${getStatusColor(transaction.status)}`}>
        {getStatusIcon(transaction.status)}
        <span className="text-sm font-medium">{getStatusText(transaction.status)}</span>
        {transaction.confirmations > 0 && (
          <span className="text-xs opacity-75">
            ({transaction.confirmations} confirmations)
          </span>
        )}
      </div>

      {/* Transaction Hash */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600">Hash:</span>
        <code className="text-sm bg-gray-100 px-2 py-1 rounded font-mono">
          {transaction.hash.slice(0, 10)}...{transaction.hash.slice(-8)}
        </code>
        <button
          onClick={() => copyToClipboard(transaction.hash)}
          className="p-1 hover:bg-gray-200 rounded transition-colors"
          title="Copy hash"
        >
          <Copy className="w-4 h-4 text-gray-500" />
        </button>
        <a
          href={transaction.explorerUrl || blockscoutService.getTransactionUrl(transaction.hash)}
          target="_blank"
          rel="noopener noreferrer"
          className="p-1 hover:bg-gray-200 rounded transition-colors"
          title="View on explorer"
        >
          <ExternalLink className="w-4 h-4 text-gray-500" />
        </a>
        {copied && (
          <span className="text-xs text-green-600">Copied!</span>
        )}
      </div>

      {/* Transaction Details */}
      {showDetails && (
        <div className="space-y-2 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-gray-600">From:</span>
              <div className="font-mono text-xs break-all">
                {transaction.from.slice(0, 10)}...{transaction.from.slice(-8)}
              </div>
            </div>
            <div>
              <span className="text-gray-600">To:</span>
              <div className="font-mono text-xs break-all">
                {transaction.to ? `${transaction.to.slice(0, 10)}...${transaction.to.slice(-8)}` : 'Contract Creation'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-gray-600">Gas Used:</span>
              <div className="font-mono text-xs">
                {parseInt(transaction.gasUsed).toLocaleString()}
              </div>
            </div>
            <div>
              <span className="text-gray-600">Block:</span>
              <div className="font-mono text-xs">
                #{transaction.blockNumber.toLocaleString()}
              </div>
            </div>
          </div>

          <div>
            <span className="text-gray-600">Value:</span>
            <div className="font-mono text-xs">
              {(parseInt(transaction.value) / 1e18).toFixed(6)} ETH
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionStatus;
