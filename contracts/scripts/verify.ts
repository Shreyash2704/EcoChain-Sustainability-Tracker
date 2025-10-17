import { ethers } from "ethers";
import hre from "hardhat";
import * as dotenv from "dotenv";
import * as fs from "fs";

// Load environment variables
dotenv.config();

async function main() {
  console.log("🔍 Starting Contract Verification...\n");

  // Get network info
  const [deployer] = await hre.ethers.getSigners();
  const network = await deployer.provider.getNetwork();
  const networkName = network.name;
  const chainId = network.chainId;

  console.log(`📋 Verification Configuration:`);
  console.log(`   Network: ${networkName} (Chain ID: ${chainId})`);
  console.log(`   Deployer: ${deployer.address}\n`);

  // Load deployment info
  const deploymentFile = `deployments/${networkName}-${chainId}.json`;
  
  if (!fs.existsSync(deploymentFile)) {
    console.error(`❌ Deployment file not found: ${deploymentFile}`);
    console.log("Please run deployment first: npx hardhat run scripts/deploy.ts --network <network>");
    process.exit(1);
  }

  const deploymentInfo = JSON.parse(fs.readFileSync(deploymentFile, 'utf8'));
  console.log("📦 Found deployment info:");
  console.log(`   EcoCreditToken: ${deploymentInfo.contracts.EcoCreditToken}`);
  console.log(`   SustainabilityProof: ${deploymentInfo.contracts.SustainabilityProof}`);
  console.log(`   ProofRegistry: ${deploymentInfo.contracts.ProofRegistry}\n`);

  // Get configuration
  const baseTokenURI = process.env.BASE_TOKEN_URI || "https://gateway.lighthouse.storage/ipfs/";

  try {
    // Verify EcoCreditToken
    console.log("1️⃣ Verifying EcoCreditToken...");
    try {
      await hre.run("verify:verify", {
        address: deploymentInfo.contracts.EcoCreditToken,
        constructorArguments: [deploymentInfo.deployer],
      });
      console.log("   ✅ EcoCreditToken verified successfully");
    } catch (error) {
      console.log("   ⚠️ EcoCreditToken verification failed (might already be verified)");
      console.log(`   Error: ${error}`);
    }

    // Verify SustainabilityProof
    console.log("\n2️⃣ Verifying SustainabilityProof...");
    try {
      await hre.run("verify:verify", {
        address: deploymentInfo.contracts.SustainabilityProof,
        constructorArguments: [
          "EcoChain Sustainability Proofs",
          "ECOSP",
          baseTokenURI,
          deploymentInfo.deployer
        ],
      });
      console.log("   ✅ SustainabilityProof verified successfully");
    } catch (error) {
      console.log("   ⚠️ SustainabilityProof verification failed (might already be verified)");
      console.log(`   Error: ${error}`);
    }

    // Verify ProofRegistry
    console.log("\n3️⃣ Verifying ProofRegistry...");
    try {
      await hre.run("verify:verify", {
        address: deploymentInfo.contracts.ProofRegistry,
        constructorArguments: [deploymentInfo.deployer],
      });
      console.log("   ✅ ProofRegistry verified successfully");
    } catch (error) {
      console.log("   ⚠️ ProofRegistry verification failed (might already be verified)");
      console.log(`   Error: ${error}`);
    }

    console.log("\n🎉 Verification process completed!");
    console.log("\n🔗 Contract Links:");
    if (chainId === 11155111n) { // Sepolia
      console.log(`EcoCreditToken: https://sepolia.etherscan.io/address/${deploymentInfo.contracts.EcoCreditToken}`);
      console.log(`SustainabilityProof: https://sepolia.etherscan.io/address/${deploymentInfo.contracts.SustainabilityProof}`);
      console.log(`ProofRegistry: https://sepolia.etherscan.io/address/${deploymentInfo.contracts.ProofRegistry}`);
    } else if (chainId === 5n) { // Goerli
      console.log(`EcoCreditToken: https://goerli.etherscan.io/address/${deploymentInfo.contracts.EcoCreditToken}`);
      console.log(`SustainabilityProof: https://goerli.etherscan.io/address/${deploymentInfo.contracts.SustainabilityProof}`);
      console.log(`ProofRegistry: https://goerli.etherscan.io/address/${deploymentInfo.contracts.ProofRegistry}`);
    } else if (chainId === 1n) { // Mainnet
      console.log(`EcoCreditToken: https://etherscan.io/address/${deploymentInfo.contracts.EcoCreditToken}`);
      console.log(`SustainabilityProof: https://etherscan.io/address/${deploymentInfo.contracts.SustainabilityProof}`);
      console.log(`ProofRegistry: https://etherscan.io/address/${deploymentInfo.contracts.ProofRegistry}`);
    } else {
      console.log("Contract addresses:");
      console.log(`EcoCreditToken: ${deploymentInfo.contracts.EcoCreditToken}`);
      console.log(`SustainabilityProof: ${deploymentInfo.contracts.SustainabilityProof}`);
      console.log(`ProofRegistry: ${deploymentInfo.contracts.ProofRegistry}`);
    }

  } catch (error) {
    console.error("❌ Verification failed:");
    console.error(error);
    process.exit(1);
  }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error("❌ Verification script failed:");
  console.error(error);
  process.exitCode = 1;
});
