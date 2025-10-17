import { network } from "hardhat";
import * as dotenv from "dotenv";
import * as fs from "fs";

// Load environment variables
dotenv.config();

async function main() {
  console.log("🚀 Starting EcoChain Smart Contracts Deployment...\n");

  // Get ethers instance
  const { ethers } = await network.connect();
  
  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📋 Deployment Configuration:");
  console.log(`   Deployer: ${deployer.address}`);
  console.log(`   Balance: ${ethers.formatEther(await deployer.provider.getBalance(deployer.address))} ETH`);
  console.log(`   Network: ${await deployer.provider.getNetwork().then(n => n.name)} (Chain ID: ${await deployer.provider.getNetwork().then(n => n.chainId)})\n`);

  // Get agent address from environment or use deployer
  const agentAddress = process.env.AGENT_ADDRESS || deployer.address;
  console.log(`   Agent Address: ${agentAddress}\n`);

  // Get configuration from environment
  const baseTokenURI = process.env.BASE_TOKEN_URI || "https://gateway.lighthouse.storage/ipfs/";
  const initialSupply = process.env.INITIAL_SUPPLY || "10000000000000000000000000"; // 10M tokens

  console.log("📦 Deploying Contracts...\n");

  // 1. Deploy EcoCreditToken
  console.log("1️⃣ Deploying EcoCreditToken...");
  const EcoCreditToken = await ethers.getContractFactory("EcoCreditToken");
  const ecoCreditToken = await EcoCreditToken.deploy(deployer.address);
  await ecoCreditToken.waitForDeployment();
  const ecoCreditTokenAddress = await ecoCreditToken.getAddress();
  console.log(`   ✅ EcoCreditToken deployed to: ${ecoCreditTokenAddress}`);

  // 2. Deploy SustainabilityProof NFT
  console.log("\n2️⃣ Deploying SustainabilityProof NFT...");
  const SustainabilityProof = await ethers.getContractFactory("SustainabilityProof");
  const sustainabilityProof = await SustainabilityProof.deploy(
    "EcoChain Sustainability Proofs",
    "ECOSP",
    baseTokenURI,
    deployer.address
  );
  await sustainabilityProof.waitForDeployment();
  const sustainabilityProofAddress = await sustainabilityProof.getAddress();
  console.log(`   ✅ SustainabilityProof deployed to: ${sustainabilityProofAddress}`);

  // 3. Deploy ProofRegistry
  console.log("\n3️⃣ Deploying ProofRegistry...");
  const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
  const proofRegistry = await ProofRegistry.deploy(deployer.address);
  await proofRegistry.waitForDeployment();
  const proofRegistryAddress = await proofRegistry.getAddress();
  console.log(`   ✅ ProofRegistry deployed to: ${proofRegistryAddress}`);

  // 4. Configure contract addresses
  console.log("\n4️⃣ Configuring Contract Addresses...");
  await proofRegistry.setContractAddresses(ecoCreditTokenAddress, sustainabilityProofAddress);
  console.log("   ✅ Contract addresses configured in ProofRegistry");

  // 5. Grant roles to agent
  console.log("\n5️⃣ Granting Roles to Agent...");
  
  // Grant MINTER_ROLE to agent for EcoCreditToken
  const MINTER_ROLE = await ecoCreditToken.MINTER_ROLE();
  await ecoCreditToken.grantRole(MINTER_ROLE, agentAddress);
  console.log(`   ✅ MINTER_ROLE granted to agent for EcoCreditToken`);

  // Grant MINTER_ROLE to agent for SustainabilityProof
  const NFT_MINTER_ROLE = await sustainabilityProof.MINTER_ROLE();
  await sustainabilityProof.grantRole(NFT_MINTER_ROLE, agentAddress);
  console.log(`   ✅ MINTER_ROLE granted to agent for SustainabilityProof`);

  // Grant REGISTRAR_ROLE and VERIFIER_ROLE to agent for ProofRegistry
  const REGISTRAR_ROLE = await proofRegistry.REGISTRAR_ROLE();
  const VERIFIER_ROLE = await proofRegistry.VERIFIER_ROLE();
  await proofRegistry.grantRole(REGISTRAR_ROLE, agentAddress);
  await proofRegistry.grantRole(VERIFIER_ROLE, agentAddress);
  console.log(`   ✅ REGISTRAR_ROLE and VERIFIER_ROLE granted to agent for ProofRegistry`);

  // 6. Display deployment summary
  console.log("\n🎉 Deployment Summary:");
  console.log("=".repeat(60));
  console.log(`EcoCreditToken:     ${ecoCreditTokenAddress}`);
  console.log(`SustainabilityProof: ${sustainabilityProofAddress}`);
  console.log(`ProofRegistry:      ${proofRegistryAddress}`);
  console.log(`Agent Address:      ${agentAddress}`);
  console.log("=".repeat(60));

  // 7. Save deployment info
  const deploymentInfo = {
    network: await deployer.provider.getNetwork().then(n => n.name),
    chainId: await deployer.provider.getNetwork().then(n => n.chainId),
    deployer: deployer.address,
    agent: agentAddress,
    contracts: {
      EcoCreditToken: ecoCreditTokenAddress,
      SustainabilityProof: sustainabilityProofAddress,
      ProofRegistry: proofRegistryAddress
    },
    timestamp: new Date().toISOString(),
    blockNumber: await deployer.provider.getBlockNumber()
  };

  // Write deployment info to file
  const deploymentFile = `deployments/${deploymentInfo.network}-${deploymentInfo.chainId}.json`;
  fs.mkdirSync('deployments', { recursive: true });
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, (key, value) =>
    typeof value === 'bigint' ? value.toString() : value, 2));
  console.log(`\n📄 Deployment info saved to: ${deploymentFile}`);

  // 8. Display next steps
  console.log("\n📋 Next Steps:");
  console.log("1. Update your .env file with the contract addresses");
  console.log("2. Update your backend Web3Service with the new addresses");
  console.log("3. Test the contracts with the test scripts");
  console.log("4. Verify contracts on Etherscan (optional)");
  console.log("\n🔗 Contract Verification Commands:");
  console.log(`npx hardhat verify --network ${deploymentInfo.network} ${ecoCreditTokenAddress} "${deployer.address}"`);
  console.log(`npx hardhat verify --network ${deploymentInfo.network} ${sustainabilityProofAddress} "EcoChain Sustainability Proofs" "ECOSP" "${baseTokenURI}" "${deployer.address}"`);
  console.log(`npx hardhat verify --network ${deploymentInfo.network} ${proofRegistryAddress} "${deployer.address}"`);

  console.log("\n✅ Deployment completed successfully!");
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error("❌ Deployment failed:");
  console.error(error);
  process.exitCode = 1;
});
