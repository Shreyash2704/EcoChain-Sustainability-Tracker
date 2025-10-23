# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying EcoChain smart contracts to various networks, including testnets and mainnet.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Git
- MetaMask or compatible wallet
- Testnet ETH (for testnet deployments)
- Mainnet ETH (for mainnet deployments)

## Environment Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the contracts directory:

```bash
# Network RPC URLs
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
POLYGON_RPC_URL=https://polygon-rpc.com

# Private Keys (for deployment)
PRIVATE_KEY=your_private_key_here

# API Keys (for verification)
ETHERSCAN_API_KEY=your_etherscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Gas Reporting
REPORT_GAS=true
```

### 3. Get Testnet ETH

For testnet deployments, you'll need testnet ETH:

- **Sepolia**: [Sepolia Faucet](https://sepoliafaucet.com/)
- **Goerli**: [Goerli Faucet](https://goerlifaucet.com/)
- **Polygon Mumbai**: [Polygon Faucet](https://faucet.polygon.technology/)

## Deployment Process

### Step 1: Compile Contracts

```bash
npx hardhat compile
```

### Step 2: Run Tests

```bash
npx hardhat test
```

### Step 3: Deploy Contracts

#### Quick Deployment (Recommended)

```bash
# Deploy to Sepolia testnet
npx hardhat run scripts/deploy-all.ts --network sepolia

# Deploy to mainnet
npx hardhat run scripts/deploy-all.ts --network mainnet
```

#### Manual Deployment

```bash
# Deploy individual contracts
npx hardhat run scripts/deploy.ts --network sepolia
```

### Step 4: Verify Contracts

```bash
# Verify on Etherscan
npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS

# Verify on Polygonscan
npx hardhat verify --network polygon DEPLOYED_CONTRACT_ADDRESS
```

## Network-Specific Instructions

### Sepolia Testnet

1. **Get Sepolia ETH**:
   - Visit [Sepolia Faucet](https://sepoliafaucet.com/)
   - Request testnet ETH

2. **Deploy Contracts**:
   ```bash
   npx hardhat run scripts/deploy-all.ts --network sepolia
   ```

3. **Verify Contracts**:
   ```bash
   npx hardhat verify --network sepolia ECO_CREDIT_TOKEN_ADDRESS
   npx hardhat verify --network sepolia SUSTAINABILITY_PROOF_ADDRESS
   npx hardhat verify --network sepolia PROOF_REGISTRY_ADDRESS
   ```

### Polygon Mumbai

1. **Get Mumbai MATIC**:
   - Visit [Polygon Faucet](https://faucet.polygon.technology/)
   - Request testnet MATIC

2. **Deploy Contracts**:
   ```bash
   npx hardhat run scripts/deploy-all.ts --network polygonMumbai
   ```

3. **Verify Contracts**:
   ```bash
   npx hardhat verify --network polygonMumbai DEPLOYED_CONTRACT_ADDRESS
   ```

### Ethereum Mainnet

1. **Prepare for Mainnet**:
   - Ensure sufficient ETH for gas
   - Test thoroughly on testnets
   - Review contract code

2. **Deploy Contracts**:
   ```bash
   npx hardhat run scripts/deploy-all.ts --network mainnet
   ```

3. **Verify Contracts**:
   ```bash
   npx hardhat verify --network mainnet DEPLOYED_CONTRACT_ADDRESS
   ```

## Post-Deployment Setup

### 1. Update Environment Variables

Update your application's environment variables with the deployed contract addresses:

```bash
# Backend .env
ECO_CREDIT_TOKEN_ADDRESS=0x...
SUSTAINABILITY_PROOF_ADDRESS=0x...
PROOF_REGISTRY_ADDRESS=0x...
```

### 2. Grant Roles

Grant necessary roles to your application:

```bash
# Grant MINTER_ROLE to your application address
npx hardhat mint-tokens --to APPLICATION_ADDRESS --amount 0 --network sepolia
```

### 3. Test Contract Interactions

```bash
# Test minting tokens
npx hardhat mint-tokens --to USER_ADDRESS --amount 1000 --network sepolia

# Test minting NFT
npx hardhat mint-nft --to USER_ADDRESS --carbon-impact 2.5 --proof-type sustainability_document --metadata-uri QmHash123 --network sepolia

# Test registering proof
npx hardhat register-proof --user USER_ADDRESS --proof-type sustainability_document --carbon-impact 2.5 --metadata-uri QmHash123 --network sepolia
```

## Deployment Verification

### 1. Check Contract Deployment

```bash
# Check contract code on explorer
# Visit: https://sepolia.etherscan.io/address/CONTRACT_ADDRESS
```

### 2. Verify Contract Functions

```bash
# Test contract functions
npx hardhat console --network sepolia
```

### 3. Monitor Gas Usage

```bash
# Generate gas report
REPORT_GAS=true npx hardhat test
```

## Troubleshooting

### Common Issues

1. **Insufficient Funds**
   - Error: "insufficient funds for gas"
   - Solution: Get more testnet ETH or reduce gas limit

2. **Gas Estimation Failed**
   - Error: "gas estimation failed"
   - Solution: Check contract logic, test with smaller values

3. **Verification Failed**
   - Error: "verification failed"
   - Solution: Check API key, verify constructor parameters

4. **Network Connection Issues**
   - Error: "network connection failed"
   - Solution: Check RPC URL, try different provider

### Debug Commands

```bash
# Check network connection
npx hardhat console --network sepolia

# Compile contracts
npx hardhat compile

# Clean artifacts
npx hardhat clean

# Check deployment status
npx hardhat run scripts/deploy-all.ts --network sepolia --verbose
```

## Security Considerations

### 1. Private Key Security

- Never commit private keys to version control
- Use environment variables
- Consider using hardware wallets for mainnet

### 2. Contract Security

- Audit contracts before mainnet deployment
- Test thoroughly on testnets
- Use established libraries (OpenZeppelin)

### 3. Access Control

- Grant minimal necessary roles
- Use multi-signature wallets for admin functions
- Implement role management

## Production Deployment

### 1. Pre-Deployment Checklist

- [ ] Contracts audited
- [ ] Tests passing
- [ ] Gas costs optimized
- [ ] Access control configured
- [ ] Documentation updated

### 2. Deployment Steps

1. **Deploy to Testnet**:
   ```bash
   npx hardhat run scripts/deploy-all.ts --network sepolia
   ```

2. **Test Thoroughly**:
   - Test all functions
   - Verify gas costs
   - Check access control

3. **Deploy to Mainnet**:
   ```bash
   npx hardhat run scripts/deploy-all.ts --network mainnet
   ```

4. **Verify Contracts**:
   ```bash
   npx hardhat verify --network mainnet DEPLOYED_CONTRACT_ADDRESS
   ```

### 3. Post-Deployment

1. **Monitor Contracts**:
   - Check transaction logs
   - Monitor gas usage
   - Track contract interactions

2. **Update Documentation**:
   - Record contract addresses
   - Update configuration files
   - Document deployment process

## Maintenance

### 1. Regular Updates

- Monitor contract performance
- Update dependencies
- Apply security patches

### 2. Role Management

- Review role assignments
- Update access control
- Monitor admin functions

### 3. Gas Optimization

- Monitor gas costs
- Optimize functions
- Update gas limits

## Support

### Documentation

- [Hardhat Documentation](https://hardhat.org/docs)
- [Ethereum Development](https://ethereum.org/developers/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)

### Community

- [Hardhat Discord](https://discord.gg/hardhat)
- [Ethereum Stack Exchange](https://ethereum.stackexchange.com/)
- [OpenZeppelin Forum](https://forum.openzeppelin.com/)

## Conclusion

This deployment guide provides comprehensive instructions for deploying EcoChain smart contracts to various networks. Follow the steps carefully, test thoroughly, and maintain security best practices throughout the deployment process.
