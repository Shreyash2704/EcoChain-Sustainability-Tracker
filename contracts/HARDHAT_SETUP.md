# Hardhat Setup Guide

## Overview

This guide covers the complete setup and usage of Hardhat for the EcoChain Sustainability Tracker smart contracts. The project includes comprehensive testing, deployment scripts, and custom tasks for professional smart contract development.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Git

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Install additional development dependencies:**
   ```bash
   npm install --save-dev hardhat-gas-reporter
   ```

## Configuration

### Environment Variables

Create a `.env` file in the contracts directory:

```bash
# Network RPC URLs
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY

# Private Keys (for deployment)
PRIVATE_KEY=your_private_key_here

# API Keys (for verification)
ETHERSCAN_API_KEY=your_etherscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Gas Reporting
REPORT_GAS=true
```

### Network Configuration

The project is configured for multiple networks:

- **Hardhat**: Local development network
- **Localhost**: Local node (Ganache, etc.)
- **Sepolia**: Ethereum testnet
- **Mainnet**: Ethereum mainnet
- **Polygon**: Polygon mainnet
- **Polygon Mumbai**: Polygon testnet

## Smart Contracts

### EcoCreditToken (ERC-20)

- **Purpose**: ECO tokens for sustainability rewards
- **Features**: Minting, burning, role-based access control
- **Roles**: MINTER_ROLE, BURNER_ROLE

### SustainabilityProof (ERC-721)

- **Purpose**: NFTs representing sustainability proofs
- **Features**: Carbon impact tracking, metadata storage
- **Roles**: MINTER_ROLE

### ProofRegistry

- **Purpose**: Registry for sustainability proof verification
- **Features**: Proof type management, carbon impact tracking
- **Roles**: REGISTRAR_ROLE

## Testing

### Running Tests

```bash
# Run all tests
npx hardhat test

# Run specific test file
npx hardhat test test/EcoCreditToken.test.ts

# Run tests with gas reporting
REPORT_GAS=true npx hardhat test

# Run tests with coverage
npx hardhat coverage
```

### Test Coverage

The test suite includes:

- **Unit Tests**: Individual function testing
- **Integration Tests**: Contract interaction testing
- **Edge Cases**: Boundary condition testing
- **Gas Optimization**: Gas cost analysis
- **Access Control**: Role-based permission testing

### Test Structure

```
test/
├── EcoCreditToken.test.ts      # ECO token tests
├── SustainabilityProof.test.ts # NFT contract tests
└── ProofRegistry.test.ts       # Registry tests
```

## Deployment

### Quick Deployment

```bash
# Deploy all contracts with automatic setup
npx hardhat run scripts/deploy-all.ts --network sepolia
```

### Manual Deployment

```bash
# Deploy individual contracts
npx hardhat run scripts/deploy.ts --network sepolia
```

### Deployment Features

- **Automatic Role Assignment**: Grants necessary roles to deployer
- **Proof Type Setup**: Adds standard proof types to registry
- **Contract Verification**: Optional automatic verification
- **Deployment Tracking**: Saves deployment info to JSON files

## Custom Tasks

### Mint Tokens

```bash
npx hardhat mint-tokens --to 0x123... --amount 1000 --network sepolia
```

### Mint NFT

```bash
npx hardhat mint-nft --to 0x123... --carbon-impact 2.5 --proof-type sustainability_document --metadata-uri QmHash123 --network sepolia
```

### Register Proof

```bash
npx hardhat register-proof --user 0x123... --proof-type sustainability_document --carbon-impact 2.5 --metadata-uri QmHash123 --network sepolia
```

## Gas Optimization

### Gas Reporting

```bash
# Generate gas report
REPORT_GAS=true npx hardhat test

# Gas report includes:
# - Function gas costs
# - Optimization suggestions
# - Cost comparisons
```

### Optimization Strategies

1. **Batch Operations**: Group multiple operations
2. **Storage Optimization**: Minimize storage writes
3. **Function Optimization**: Use efficient algorithms
4. **Event Optimization**: Minimize event data

## Contract Verification

### Automatic Verification

```bash
# Verify contracts after deployment
npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS
```

### Manual Verification

1. **Etherscan**: Upload source code manually
2. **Blockscout**: Use verification API
3. **Sourcify**: Automatic verification service

## Development Workflow

### 1. Local Development

```bash
# Start local node
npx hardhat node

# Deploy to local network
npx hardhat run scripts/deploy-all.ts --network localhost
```

### 2. Testing

```bash
# Run tests
npx hardhat test

# Run specific test
npx hardhat test test/EcoCreditToken.test.ts --grep "minting"
```

### 3. Deployment

```bash
# Deploy to testnet
npx hardhat run scripts/deploy-all.ts --network sepolia

# Verify contracts
npx hardhat verify --network sepolia
```

### 4. Production

```bash
# Deploy to mainnet
npx hardhat run scripts/deploy-all.ts --network mainnet

# Verify contracts
npx hardhat verify --network mainnet
```

## Troubleshooting

### Common Issues

1. **Gas Estimation Failed**
   - Check contract logic for reverts
   - Verify function parameters
   - Test with smaller values

2. **Verification Failed**
   - Check API key configuration
   - Verify contract source code
   - Ensure correct constructor parameters

3. **Network Connection Issues**
   - Verify RPC URL configuration
   - Check network status
   - Try different RPC providers

### Debug Commands

```bash
# Compile contracts
npx hardhat compile

# Clean artifacts
npx hardhat clean

# Check network connection
npx hardhat console --network sepolia
```

## Best Practices

### Security

1. **Access Control**: Use role-based permissions
2. **Input Validation**: Validate all inputs
3. **Reentrancy Protection**: Use proper patterns
4. **Upgradeability**: Consider proxy patterns

### Gas Optimization

1. **Batch Operations**: Group related operations
2. **Storage Layout**: Optimize storage structure
3. **Function Efficiency**: Minimize computation
4. **Event Optimization**: Reduce event data

### Testing

1. **Comprehensive Coverage**: Test all functions
2. **Edge Cases**: Test boundary conditions
3. **Integration Testing**: Test contract interactions
4. **Gas Testing**: Monitor gas costs

## Advanced Features

### Custom Networks

Add custom networks to `hardhat.config.ts`:

```typescript
networks: {
  customNetwork: {
    url: "https://custom-rpc-url.com",
    accounts: [process.env.PRIVATE_KEY],
    chainId: 12345,
  },
}
```

### Plugin Configuration

Configure additional plugins:

```typescript
plugins: [
  hardhatToolboxMochaEthersPlugin,
  "hardhat-gas-reporter",
  "@nomicfoundation/hardhat-verify",
]
```

## Support

### Documentation

- [Hardhat Documentation](https://hardhat.org/docs)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Ethereum Development](https://ethereum.org/developers/)

### Community

- [Hardhat Discord](https://discord.gg/hardhat)
- [Ethereum Stack Exchange](https://ethereum.stackexchange.com/)
- [OpenZeppelin Forum](https://forum.openzeppelin.com/)

## Conclusion

This Hardhat setup provides a professional development environment for smart contract development with comprehensive testing, deployment automation, and gas optimization. The custom tasks and deployment scripts streamline the development workflow while maintaining security and efficiency best practices.
