import { useState, useCallback } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { useUploadFile } from '../hooks/useApi';
import TransactionStatus from '../components/TransactionStatus';
import SampleDocuments from '../components/SampleDocuments';
import JSONTemplateGenerator from '../components/JSONTemplateGenerator';
import { 
  Upload, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Download,
  Leaf,
  Coins,
  Award
} from 'lucide-react';

interface UploadResult {
  upload_id: string;
  status: string;
  cid: string;
  should_mint: boolean;
  token_amount: number;
  impact_score: number;
  reasoning: string;
  blockchain_transactions: {
    eco_token_minting: {
      tx_hash: string;
      explorer_url: string;
      amount: number;
    };
    nft_minting: {
      tx_hash: string;
      token_id: string;
      explorer_url: string;
      nft_contract: string;
    };
    proof_registration: {
      tx_hash: string | null;
      proof_id: string | null;
      explorer_url: string | null;
      registry_contract: string;
    };
  };
  wallet_info: {
    user_wallet: string;
    wallet_explorer: string;
    eco_token_balance: string;
    nft_collection: string;
  };
}

export default function UploadPage() {
  const { authenticated, user } = usePrivy();
  const [dragActive, setDragActive] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const uploadMutation = useUploadFile();
  const walletAddress = user?.wallet?.address || '';

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    if (!authenticated || !walletAddress) {
      alert('Please connect your wallet first');
      return;
    }

    if (!file.name.endsWith('.json')) {
      alert('Please upload a JSON file');
      return;
    }

    setIsUploading(true);
    setUploadResult(null);

    try {
      const result = await uploadMutation.mutateAsync({
        file,
        walletAddress,
      });
      setUploadResult(result);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };


  if (!authenticated) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center">
          <Upload className="w-16 h-16 text-eco-600 dark:text-eco-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Connect Your Wallet to Upload Documents
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Connect your wallet to upload sustainability documents and earn carbon credits.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Upload Sustainability Document
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Upload your sustainability report to get AI analysis and earn carbon credits
        </p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
            dragActive
              ? 'border-eco-500 bg-eco-50 dark:bg-eco-900/10'
              : 'border-gray-300 dark:border-gray-600 hover:border-eco-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".json"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          {isUploading ? (
            <div className="space-y-4">
              <Loader2 className="w-12 h-12 text-eco-600 animate-spin mx-auto" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Processing Your Document
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Our AI is analyzing your sustainability data...
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="w-12 h-12 text-gray-400 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Drop your JSON file here
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  or click to browse files
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Supported format: JSON files only
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* File Reading Notice */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-amber-800 mb-1">
              File Reading Functionality Notice
            </h3>
            <p className="text-sm text-amber-700">
              <strong>Important:</strong> File reading functionality is not yet implemented in this version. 
              Please use the sample JSON documents provided below to test the system. 
              This feature will be added in the next development phase.
            </p>
          </div>
        </div>
      </div>

      {/* Sample Documents */}
      <SampleDocuments />

      {/* JSON Template Generator */}
      <JSONTemplateGenerator />

      {/* Upload Result */}
      {uploadResult && (
        <div className="space-y-6">
          {/* Analysis Results */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Analysis Complete
              </h2>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Impact Score */}
              <div className="bg-eco-50 dark:bg-eco-900/10 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Leaf className="w-5 h-5 text-eco-600" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">Impact Score</h3>
                </div>
                <p className="text-3xl font-bold text-eco-600">
                  {uploadResult.impact_score}/100
                </p>
              </div>

              {/* Token Amount */}
              <div className="bg-blue-50 dark:bg-blue-900/10 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Coins className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">Tokens Earned</h3>
                </div>
                <p className="text-3xl font-bold text-blue-600">
                  {uploadResult.should_mint ? uploadResult.token_amount : 0} ECO
                </p>
              </div>
            </div>

            {/* Reasoning */}
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Analysis Reasoning</h3>
              <p className="text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                {uploadResult.reasoning}
              </p>
            </div>
          </div>

          {/* Blockchain Transactions */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <Award className="w-8 h-8 text-purple-600" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Blockchain Transactions
              </h2>
            </div>

            <div className="space-y-4">
              {/* ECO Tokens */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white">ECO Tokens</h3>
                  {uploadResult.blockchain_transactions.eco_token_minting.tx_hash ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>
                {uploadResult.blockchain_transactions.eco_token_minting.tx_hash ? (
                  <div className="space-y-3">
                    <TransactionStatus
                      txHash={uploadResult.blockchain_transactions.eco_token_minting.tx_hash}
                      showDetails={true}
                    />
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      Amount: {uploadResult.blockchain_transactions.eco_token_minting.amount} ECO tokens
                    </div>
                  </div>
                ) : (
                  <p className="text-red-600 text-sm">Token minting failed</p>
                )}
              </div>

              {/* Sustainability NFT */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Sustainability NFT</h3>
                  {uploadResult.blockchain_transactions.nft_minting.tx_hash ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>
                {uploadResult.blockchain_transactions.nft_minting.tx_hash ? (
                  <div className="space-y-3">
                    <TransactionStatus
                      txHash={uploadResult.blockchain_transactions.nft_minting.tx_hash}
                      showDetails={true}
                    />
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      Token ID: #{uploadResult.blockchain_transactions.nft_minting.token_id}
                    </div>
                  </div>
                ) : (
                  <p className="text-red-600 text-sm">NFT minting failed</p>
                )}
              </div>
            </div>
          </div>

          {/* Upload Details */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Upload Details</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-300">Upload ID:</span>
                <code className="ml-2 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                  {uploadResult.upload_id}
                </code>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-300">IPFS CID:</span>
                <code className="ml-2 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                  {uploadResult.cid}
                </code>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-300">Status:</span>
                <span className="ml-2 text-green-600 font-medium">{uploadResult.status}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Example JSON */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Example JSON Format</h3>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 overflow-x-auto">
          <pre className="text-sm text-gray-700 dark:text-gray-300">
{`{
  "document_type": "sustainability_report",
  "carbon_footprint": 150.5,
  "waste_reduction_percentage": 25.0,
  "renewable_energy_percentage": 40.0,
  "energy_consumption": 1200.0,
  "waste_reduction": 15.0
}`}
          </pre>
        </div>
        <button
          onClick={() => {
            const exampleData = {
              document_type: "sustainability_report",
              carbon_footprint: 150.5,
              waste_reduction_percentage: 25.0,
              renewable_energy_percentage: 40.0,
              energy_consumption: 1200.0,
              waste_reduction: 15.0
            };
            const blob = new Blob([JSON.stringify(exampleData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'example-sustainability-report.json';
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="btn-secondary mt-4"
        >
          <Download className="w-4 h-4 mr-2" />
          Download Example
        </button>
      </div>
    </div>
  );
}
