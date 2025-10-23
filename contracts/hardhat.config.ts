import type { HardhatUserConfig } from "hardhat/config";
import * as dotenv from "dotenv";

import hardhatToolboxMochaEthersPlugin from "@nomicfoundation/hardhat-toolbox-mocha-ethers";
import "hardhat-gas-reporter";
import { configVariable } from "hardhat/config";

// Import custom tasks
import "./tasks/mint-tokens";
import "./tasks/mint-nft";
import "./tasks/register-proof";

// Load environment variables
dotenv.config();

const config: HardhatUserConfig = {
  plugins: [hardhatToolboxMochaEthersPlugin],
  solidity: {
    profiles: {
      default: {
        version: "0.8.20",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      production: {
        version: "0.8.20",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    },
  },
  networks: {
    // Local development networks
    hardhat: {
      type: "edr-simulated",
      chainType: "l1",
    },
    localhost: {
      type: "http",
      chainType: "l1",
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
    
    // Ethereum testnets
    sepolia: {
      type: "http",
      chainType: "l1",
      url: process.env.SEPOLIA_RPC_URL || configVariable("SEPOLIA_RPC_URL"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [configVariable("SEPOLIA_PRIVATE_KEY")],
      chainId: 11155111,
    },
    goerli: {
      type: "http",
      chainType: "l1",
      url: process.env.GOERLI_RPC_URL || configVariable("GOERLI_RPC_URL"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [configVariable("GOERLI_PRIVATE_KEY")],
      chainId: 5,
    },
    
    // Ethereum mainnet (for production)
    mainnet: {
      type: "http",
      chainType: "l1",
      url: process.env.MAINNET_RPC_URL || configVariable("MAINNET_RPC_URL"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [configVariable("MAINNET_PRIVATE_KEY")],
      chainId: 1,
    },
    
    // Polygon networks
    polygon: {
      type: "http",
      chainType: "l1",
      url: process.env.POLYGON_RPC_URL || configVariable("POLYGON_RPC_URL"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [configVariable("POLYGON_PRIVATE_KEY")],
      chainId: 137,
    },
    polygonMumbai: {
      type: "http",
      chainType: "l1",
      url: process.env.POLYGON_MUMBAI_RPC_URL || configVariable("POLYGON_MUMBAI_RPC_URL"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [configVariable("POLYGON_MUMBAI_PRIVATE_KEY")],
      chainId: 80001,
    },
  },
  
  // Gas reporting
  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: "USD",
    gasPrice: 20,
  },
  
  // Etherscan verification
  etherscan: {
    apiKey: {
      mainnet: process.env.ETHERSCAN_API_KEY || "",
      sepolia: process.env.ETHERSCAN_API_KEY || "",
      goerli: process.env.ETHERSCAN_API_KEY || "",
      polygon: process.env.POLYGONSCAN_API_KEY || "",
      polygonMumbai: process.env.POLYGONSCAN_API_KEY || "",
    },
  },
  
  // Paths
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};

export default config;
