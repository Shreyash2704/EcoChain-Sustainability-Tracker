import React, { useState, useEffect } from 'react';
import { ExternalLink, Copy, Image as ImageIcon, Leaf } from 'lucide-react';
import { blockscoutService, type NFT } from '../services/blockscout';

interface NFTGalleryProps {
  walletAddress: string;
  contractAddress: string;
  analyticsData?: any;
  className?: string;
}

export const NFTGallery: React.FC<NFTGalleryProps> = ({
  walletAddress,
  contractAddress,
  analyticsData,
  className = '',
}) => {
  const [nfts, setNFTs] = useState<NFT[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    if (!walletAddress || !contractAddress) return;
    
    // Use analytics data if available, otherwise fetch from Blockscout
    if (analyticsData?.upload_history) {
      loadNFTsFromAnalytics();
    } else {
      fetchNFTs();
    }
  }, [walletAddress, contractAddress, analyticsData]);

  const loadNFTsFromAnalytics = () => {
    try {
      setLoading(true);
      setError(null);
      
      const nftList: NFT[] = [];
      
      // Extract NFTs from upload history
      analyticsData.upload_history.forEach((upload: any) => {
        if (upload.blockchain_transactions?.nft_token_id) {
          nftList.push({
            contractAddress: contractAddress,
            tokenId: upload.blockchain_transactions.nft_token_id,
            owner: walletAddress,
            transactionHash: upload.blockchain_transactions.nft_tx,
            blockNumber: upload.blockchain_transactions.nft_block_number || 0,
            metadata: {
              tokenId: upload.blockchain_transactions.nft_token_id,
              name: `Sustainability Proof #${upload.blockchain_transactions.nft_token_id}`,
              description: `Sustainability proof for ${upload.filename}`,
              image: '/api/placeholder/300/300', // Placeholder image
              attributes: [
                {
                  trait_type: "Document Type",
                  value: upload.analysis?.document_type || "Sustainability Document"
                },
                {
                  trait_type: "Carbon Impact",
                  value: upload.analysis?.carbon_footprint || "0"
                },
                {
                  trait_type: "Upload Date",
                  value: upload.upload_timestamp || "Unknown"
                }
              ]
            }
          });
        }
      });
      
      setNFTs(nftList);
    } catch (err) {
      console.error('Error loading NFTs from analytics:', err);
      setError('Failed to load NFTs from analytics data');
    } finally {
      setLoading(false);
    }
  };

  const fetchNFTs = async () => {
    try {
      setLoading(true);
      setError(null);
      const nftData = await blockscoutService.getNFTs(walletAddress, contractAddress);
      setNFTs(nftData);
    } catch (err) {
      setError('Failed to fetch NFTs');
      console.error('NFT fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(id);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getCarbonImpact = (nft: NFT): string | null => {
    // For NFTs from analytics data, we don't have metadata attributes
    // Return null or extract from description if available
    if (nft.metadata?.attributes) {
      const carbonAttr = nft.metadata.attributes.find(
        attr => attr.trait_type.toLowerCase().includes('carbon') || 
                attr.trait_type.toLowerCase().includes('impact')
      );
      return carbonAttr?.value || null;
    }
    return null;
  };

  const getSustainabilityScore = (nft: NFT): number | null => {
    // For NFTs from analytics data, we don't have metadata attributes
    // Return null or extract from description if available
    if (nft.metadata?.attributes) {
      const scoreAttr = nft.metadata.attributes.find(
        attr => attr.trait_type.toLowerCase().includes('score') ||
                attr.trait_type.toLowerCase().includes('sustainability')
      );
      return scoreAttr ? parseInt(scoreAttr.value) : null;
    }
    return null;
  };

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-500"></div>
          <span className="text-sm text-gray-600">Loading NFTs...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center space-x-2 text-red-600 ${className}`}>
        <span className="text-sm">{error}</span>
        <button
          onClick={fetchNFTs}
          className="text-xs underline hover:no-underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (nfts.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <Leaf className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No NFTs Found</h3>
        <p className="text-sm text-gray-600">
          Upload sustainability documents to mint your first SustainabilityProof NFT
        </p>
      </div>
    );
  }

  // Filter out NFTs without proper data
  const validNFTs = nfts.filter(nft => nft.tokenId && nft.contractAddress);
  
  if (validNFTs.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <Leaf className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Valid NFTs Found</h3>
        <p className="text-sm text-gray-600">
          Your NFTs are still being processed. Please wait a moment and refresh.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          SustainabilityProof NFTs ({validNFTs.length})
        </h3>
        <button
          onClick={fetchNFTs}
          className="text-sm text-green-600 hover:text-green-700 underline"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {validNFTs.map((nft) => {
          const carbonImpact = getCarbonImpact(nft);
          const sustainabilityScore = getSustainabilityScore(nft);

          return (
            <div
              key={`${nft.contractAddress}-${nft.tokenId}`}
              className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* NFT Image */}
              <div className="aspect-square bg-gray-100 flex items-center justify-center">
                {nft.metadata?.image && nft.metadata.image !== '/api/placeholder/300/300' ? (
                  <img
                    src={nft.metadata.image}
                    alt={nft.metadata.name || 'NFT'}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.nextElementSibling?.classList.remove('hidden');
                    }}
                  />
                ) : null}
                <div className={`${nft.metadata?.image && nft.metadata.image !== '/api/placeholder/300/300' ? 'hidden' : ''} flex-col items-center justify-center text-gray-400`}>
                  <ImageIcon className="w-8 h-8 mb-2" />
                  <span className="text-sm">Sustainability Proof</span>
                </div>
              </div>

              {/* NFT Details */}
              <div className="p-4 space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900 truncate">
                    {nft.metadata?.name || `Sustainability Proof #${nft.tokenId}`}
                  </h4>
                  <p className="text-sm text-gray-600 truncate">
                    Token ID: {nft.tokenId}
                  </p>
                </div>

                {/* Sustainability Metrics */}
                <div className="space-y-2">
                  {carbonImpact && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Carbon Impact:</span>
                      <span className="font-medium text-green-600">
                        {carbonImpact}
                      </span>
                    </div>
                  )}

                  {sustainabilityScore && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Sustainability Score:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${sustainabilityScore}%` }}
                          ></div>
                        </div>
                        <span className="font-medium text-green-600">
                          {sustainabilityScore}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Attributes */}
                {nft.metadata.attributes.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-xs text-gray-500">Attributes:</span>
                    <div className="flex flex-wrap gap-1">
                      {nft.metadata.attributes.slice(0, 3).map((attr, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-100 text-xs rounded-full text-gray-700"
                        >
                          {attr.trait_type}: {attr.value}
                        </span>
                      ))}
                      {nft.metadata.attributes.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-xs rounded-full text-gray-700">
                          +{nft.metadata.attributes.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                  <button
                    onClick={() => copyToClipboard(nft.tokenId, nft.tokenId)}
                    className="flex items-center space-x-1 text-xs text-gray-600 hover:text-gray-800"
                  >
                    <Copy className="w-3 h-3" />
                    <span>{copied === nft.tokenId ? 'Copied!' : 'Copy ID'}</span>
                  </button>

                  <a
                    href={blockscoutService.getNFTUrl(nft.contractAddress, nft.tokenId)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-xs text-green-600 hover:text-green-700"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span>View</span>
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NFTGallery;
