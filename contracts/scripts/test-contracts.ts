import { network as hardhatNetwork } from "hardhat";
import * as dotenv from "dotenv";
import * as fs from "fs";

// Load environment variables
dotenv.config();

async function main() {
  console.log("🧪 Testing Deployed EcoChain Contracts...\n");

  // Get ethers instance
  const { ethers } = await hardhatNetwork.connect();
  
  // Get network info
  const [deployer, testUser] = await ethers.getSigners();
  const network = await deployer.provider.getNetwork();
  const networkName = network.name;
  const chainId = network.chainId;

  console.log(`📋 Test Configuration:`);
  console.log(`   Network: ${networkName} (Chain ID: ${chainId})`);
  console.log(`   Deployer: ${deployer.address}`);
  console.log(`   Test User: ${testUser.address}\n`);

  // Deploy fresh contracts for testing
  console.log("📦 Deploying fresh contracts for testing...\n");
  
  // Get contract instances
  const EcoCreditToken = await ethers.getContractFactory("EcoCreditToken");
  const SustainabilityProof = await ethers.getContractFactory("SustainabilityProof");
  const ProofRegistry = await ethers.getContractFactory("ProofRegistry");

  // Deploy contracts
  const ecoCreditToken = await EcoCreditToken.deploy(deployer.address);
  await ecoCreditToken.waitForDeployment();
  const ecoCreditTokenAddress = await ecoCreditToken.getAddress();
  console.log(`   ✅ EcoCreditToken deployed to: ${ecoCreditTokenAddress}`);

  const sustainabilityProof = await SustainabilityProof.deploy(
    "EcoChain Sustainability Proofs",
    "ECOSP",
    "https://gateway.lighthouse.storage/ipfs/",
    deployer.address
  );
  await sustainabilityProof.waitForDeployment();
  const sustainabilityProofAddress = await sustainabilityProof.getAddress();
  console.log(`   ✅ SustainabilityProof deployed to: ${sustainabilityProofAddress}`);

  const proofRegistry = await ProofRegistry.deploy(deployer.address);
  await proofRegistry.waitForDeployment();
  const proofRegistryAddress = await proofRegistry.getAddress();
  console.log(`   ✅ ProofRegistry deployed to: ${proofRegistryAddress}\n`);

  // Configure contracts
  await proofRegistry.setContractAddresses(ecoCreditTokenAddress, sustainabilityProofAddress);
  console.log("   ✅ Contract addresses configured\n");

  try {
    // Test 1: Check token info
    console.log("1️⃣ Testing EcoCreditToken Info...");
    const tokenName = await ecoCreditToken.name();
    const tokenSymbol = await ecoCreditToken.symbol();
    const tokenDecimals = await ecoCreditToken.decimals();
    const tokenTotalSupply = await ecoCreditToken.totalSupply();
    console.log(`   Name: ${tokenName}`);
    console.log(`   Symbol: ${tokenSymbol}`);
    console.log(`   Decimals: ${tokenDecimals}`);
    console.log(`   Total Supply: ${ethers.formatEther(tokenTotalSupply)} ECO`);

    // Test 2: Check NFT info
    console.log("\n2️⃣ Testing SustainabilityProof NFT Info...");
    const nftName = await sustainabilityProof.name();
    const nftSymbol = await sustainabilityProof.symbol();
    const totalSupply = await sustainabilityProof.totalSupply();
    console.log(`   Name: ${nftName}`);
    console.log(`   Symbol: ${nftSymbol}`);
    console.log(`   Total Supply: ${totalSupply}`);

    // Test 3: Check registry info
    console.log("\n3️⃣ Testing ProofRegistry Info...");
    const registryInfo = await proofRegistry.getContractInfo();
    console.log(`   EcoCredit Token: ${registryInfo.ecoCreditToken}`);
    console.log(`   Sustainability Proof NFT: ${registryInfo.sustainabilityProofNFT}`);
    console.log(`   Total Proofs: ${registryInfo.totalProofs}`);
    console.log(`   Total Verifications: ${registryInfo.totalVerifications}`);

    // Test 4: Check valid proof types
    console.log("\n4️⃣ Testing Valid Proof Types...");
    const validProofTypes = await proofRegistry.getValidProofTypes();
    console.log(`   Valid Proof Types: ${validProofTypes.join(", ")}`);

    // Test 5: Register a test proof
    console.log("\n5️⃣ Testing Proof Registration...");
    const testProofType = "carbon_footprint";
    const testCarbonImpact = ethers.parseEther("100"); // 100 kg CO2
    const testMetadataURI = "https://gateway.lighthouse.storage/ipfs/QmTest123";
    const testIPFSCID = "QmTest123";

    const tx1 = await proofRegistry.registerProof(
      testUser.address,
      testProofType,
      testCarbonImpact,
      testMetadataURI,
      testIPFSCID
    );
    await tx1.wait();
    console.log(`   ✅ Proof registered successfully`);

    // Test 6: Verify the proof
    console.log("\n6️⃣ Testing Proof Verification...");
    const proofId = await proofRegistry.getTotalProofs();
    const tx2 = await proofRegistry.verifyProof(
      proofId,
      true,
      "Test verification - proof looks good"
    );
    await tx2.wait();
    console.log(`   ✅ Proof verified successfully`);

    // Test 7: Mint tokens based on verified proof
    console.log("\n7️⃣ Testing Token Minting...");
    const mintAmount = ethers.parseEther("1000"); // 1000 ECO tokens
    const tx3 = await ecoCreditToken.mint(
      testUser.address,
      mintAmount,
      "Carbon footprint reduction reward"
    );
    await tx3.wait();
    console.log(`   ✅ ${ethers.formatEther(mintAmount)} ECO tokens minted to ${testUser.address}`);

    // Test 8: Mint NFT for the proof
    console.log("\n8️⃣ Testing NFT Minting...");
    const tx4 = await sustainabilityProof.mintSustainabilityProof(
      testUser.address,
      testProofType,
      testCarbonImpact,
      testMetadataURI
    );
    await tx4.wait();
    console.log(`   ✅ Sustainability Proof NFT minted to ${testUser.address}`);

    // Test 9: Check balances
    console.log("\n9️⃣ Checking Balances...");
    const userTokenBalance = await ecoCreditToken.balanceOf(testUser.address);
    const userNFTBalance = await sustainabilityProof.balanceOf(testUser.address);
    console.log(`   Test User ECO Balance: ${ethers.formatEther(userTokenBalance)} ECO`);
    console.log(`   Test User NFT Balance: ${userNFTBalance}`);

    // Test 10: Get user's total carbon impact
    console.log("\n🔟 Testing Carbon Impact Calculation...");
    const totalCarbonImpact = await proofRegistry.getUserTotalCarbonImpact(testUser.address);
    console.log(`   Test User Total Carbon Impact: ${ethers.formatEther(totalCarbonImpact)} kg CO2`);

    console.log("\n🎉 All tests completed successfully!");
    console.log("\n📊 Test Summary:");
    console.log("=" * 50);
    console.log(`✅ Token Info: Working`);
    console.log(`✅ NFT Info: Working`);
    console.log(`✅ Registry Info: Working`);
    console.log(`✅ Proof Types: Working`);
    console.log(`✅ Proof Registration: Working`);
    console.log(`✅ Proof Verification: Working`);
    console.log(`✅ Token Minting: Working`);
    console.log(`✅ NFT Minting: Working`);
    console.log(`✅ Balance Checks: Working`);
    console.log(`✅ Carbon Impact: Working`);
    console.log("=" * 50);

  } catch (error) {
    console.error("❌ Test failed:");
    console.error(error);
    process.exit(1);
  }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error("❌ Test script failed:");
  console.error(error);
  process.exitCode = 1;
});
