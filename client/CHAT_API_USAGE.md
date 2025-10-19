# Chat API Usage Guide

## Overview
The EcoChain chat API now supports both text messages and file uploads. Here's how to use it:

## 1. Text-Only Messages

### Frontend Usage
```typescript
import { chatApi } from '../services/api';

// Send a text message
const response = await chatApi.sendMessage(
  walletAddress, 
  "How much credits do I have?"
);
```

### API Request
```bash
curl -X POST "http://localhost:8002/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "0x...",
    "message": "How much credits do I have?",
    "context": {},
    "message_id": "msg_123"
  }'
```

### API Response
```json
{
  "response": "🌱 You have 0 ECO tokens in your account. Upload sustainability documents to start earning credits!",
  "data": {
    "total_credits": 0,
    "total_tokens": "0",
    "wallet_address": "0x..."
  },
  "agent_name": "analytics_agent",
  "success": true,
  "error": null,
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## 2. File Upload with Message

### Frontend Usage
```typescript
import { chatApi } from '../services/api';

// Send a message with file attachment
const file = new File([jsonContent], 'sustainability-report.json', { type: 'application/json' });
const response = await chatApi.sendMessage(
  walletAddress, 
  "Please analyze this sustainability report",
  file
);
```

### API Request
```bash
curl -X POST "http://localhost:8002/chat/query-with-file" \
  -F "wallet_address=0x..." \
  -F "message=Please analyze this sustainability report" \
  -F "file=@sustainability-report.json"
```

**Note:** The backend automatically adds the required `upload_type=sustainability_document` field when processing files.

### API Response
```json
{
  "response": "🎉 **File Upload Successful!**\n\n📄 **File**: sustainability-report.json\n✅ **Tokens Earned**: 75 ECO\n📈 **Impact Score**: 85/100\n\nYour sustainability document has been analyzed and tokens have been minted to your wallet!",
  "data": {
    "upload_id": "upload_123",
    "status": "completed",
    "cid": "QmMock...",
    "analysis": {
      "should_mint": true,
      "token_amount": 75,
      "impact_score": 85,
      "reasoning": "High impact sustainability metrics detected..."
    },
    "blockchain_transactions": {
      "eco_tokens": {
        "success": true,
        "tx_hash": "0x...",
        "explorer_url": "https://eth-sepolia.blockscout.com/tx/0x..."
      },
      "sustainability_nft": {
        "success": true,
        "tx_hash": "0x...",
        "token_id": "123",
        "explorer_url": "https://eth-sepolia.blockscout.com/tx/0x..."
      }
    }
  },
  "agent_name": "upload_agent",
  "success": true,
  "error": null,
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## 3. React Hook Usage

### Using the useSendMessage Hook
```typescript
import { useSendMessage } from '../hooks/useApi';

function ChatComponent() {
  const sendMessageMutation = useSendMessage();
  
  const handleSendText = async () => {
    await sendMessageMutation.mutateAsync({
      walletAddress: "0x...",
      message: "How can I improve my sustainability score?"
    });
  };
  
  const handleSendFile = async (file: File) => {
    await sendMessageMutation.mutateAsync({
      walletAddress: "0x...",
      message: "Please analyze this document",
      file: file
    });
  };
  
  return (
    <div>
      <button onClick={handleSendText}>Send Text</button>
      <input 
        type="file" 
        accept=".json" 
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleSendFile(file);
        }}
      />
    </div>
  );
}
```

## 4. Chat Interface Integration

The ChatPage component now supports both text and file uploads:

```typescript
// Text message
const handleSendMessage = async () => {
  await sendMessageMutation.mutateAsync({
    walletAddress,
    message: input.trim(),
  });
};

// File upload
const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (file) {
    handleSendMessage(file); // Automatically sends the file
  }
};
```

## 5. Example JSON File Format

Create a JSON file with sustainability data:

```json
{
  "document_type": "sustainability_report",
  "carbon_footprint": 150.5,
  "waste_reduction_percentage": 25.0,
  "renewable_energy_percentage": 40.0,
  "energy_consumption": 1200.0,
  "waste_reduction": 15.0
}
```

## 6. Error Handling

The API returns structured error responses:

```json
{
  "response": "❌ **Upload Failed**\n\n📄 **File**: invalid-file.txt\n\nError: Only JSON files are supported\n\nPlease check your file format and try again.",
  "data": {
    "success": false,
    "error": "Only JSON files are supported"
  },
  "agent_name": "upload_agent",
  "success": false,
  "error": "Only JSON files are supported",
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## 7. Chat History

Retrieve chat history for a wallet:

```bash
curl -X GET "http://localhost:8002/chat/history/0x...?limit=10"
```

## 8. Agent Status

Check the status of all agents:

```bash
curl -X GET "http://localhost:8002/chat/agents/status"
```

## Summary

The enhanced chat API provides:
- ✅ Text-only messages for general queries
- ✅ File upload with automatic analysis
- ✅ Integrated blockchain transactions
- ✅ Rich response formatting
- ✅ Error handling and validation
- ✅ Chat history tracking
- ✅ Agent status monitoring

This creates a seamless experience where users can chat with the AI assistant and upload files directly through the chat interface!
