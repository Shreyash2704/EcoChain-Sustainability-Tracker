import { ethers } from "hardhat";
import { EcoCreditToken, SustainabilityProof, ProofRegistry } from "../typechain-types";

async function main() {
  console.log("🚀 Starting comprehensive deployment of EcoChain contracts...");
  
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH");

  const deploymentInfo: any = {
    network: await ethers.provider.getNetwork(),
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {}
  };

  try {
    // 1. Deploy EcoCreditToken
    console.log("\n📄 Deploying EcoCreditToken...");
    const EcoCreditToken = await ethers.getContractFactory("EcoCreditToken");
    const ecoCreditToken = await EcoCreditToken.deploy();
    await ecoCreditToken.waitForDeployment();
    
    const ecoCreditTokenAddress = await ecoCreditToken.getAddress();
    console.log("✅ EcoCreditToken deployed to:", ecoCreditTokenAddress);
    
    deploymentInfo.contracts.ecoCreditToken = {
      address: ecoCreditTokenAddress,
      name: "EcoCreditToken",
      symbol: "ECO"
    };

    // 2. Deploy SustainabilityProof
    console.log("\n🎨 Deploying SustainabilityProof...");
    const SustainabilityProof = await ethers.getContractFactory("SustainabilityProof");
    const sustainabilityProof = await SustainabilityProof.deploy();
    await sustainabilityProof.waitForDeployment();
    
    const sustainabilityProofAddress = await sustainabilityProof.getAddress();
    console.log("✅ SustainabilityProof deployed to:", sustainabilityProofAddress);
    
    deploymentInfo.contracts.sustainabilityProof = {
      address: sustainabilityProofAddress,
      name: "SustainabilityProof",
      symbol: "SP"
    };

    // 3. Deploy ProofRegistry
    console.log("\n📋 Deploying ProofRegistry...");
    const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
    const proofRegistry = await ProofRegistry.deploy();
    await proofRegistry.waitForDeployment();
    
    const proofRegistryAddress = await proofRegistry.getAddress();
    console.log("✅ ProofRegistry deployed to:", proofRegistryAddress);
    
    deploymentInfo.contracts.proofRegistry = {
      address: proofRegistryAddress,
      name: "ProofRegistry"
    };

    // 4. Setup roles and permissions
    console.log("\n🔐 Setting up roles and permissions...");
    
    // Grant MINTER_ROLE to deployer for EcoCreditToken
    const MINTER_ROLE = await ecoCreditToken.MINTER_ROLE();
    await ecoCreditToken.grantRole(MINTER_ROLE, deployer.address);
    console.log("✅ Granted MINTER_ROLE to deployer for EcoCreditToken");

    // Grant MINTER_ROLE to deployer for SustainabilityProof
    const SP_MINTER_ROLE = await sustainabilityProof.MINTER_ROLE();
    await sustainabilityProof.grantRole(SP_MINTER_ROLE, deployer.address);
    console.log("✅ Granted MINTER_ROLE to deployer for SustainabilityProof");

    // Grant REGISTRAR_ROLE to deployer for ProofRegistry
    const REGISTRAR_ROLE = await proofRegistry.REGISTRAR_ROLE();
    await proofRegistry.grantRole(REGISTRAR_ROLE, deployer.address);
    console.log("✅ Granted REGISTRAR_ROLE to deployer for ProofRegistry");

    // 5. Add proof types to ProofRegistry
    console.log("\n📝 Adding proof types to ProofRegistry...");
    const proofTypes = [
      "sustainability_document",
      "sustainability_report", 
      "proof_of_impact",
      "carbon_footprint_report",
      "energy_efficiency_report"
    ];

    for (const proofType of proofTypes) {
      await proofRegistry.addProofType(proofType);
      console.log(`✅ Added proof type: ${proofType}`);
    }

    // 6. Verify contracts (if on supported network)
    console.log("\n🔍 Verifying contracts...");
    try {
      // Note: Contract verification would go here
      // This requires network-specific configuration
      console.log("ℹ️ Contract verification requires network-specific setup");
    } catch (error) {
      console.log("⚠️ Contract verification failed:", error);
    }

    // 7. Test basic functionality
    console.log("\n🧪 Testing basic functionality...");
    
    // Test minting ECO tokens
    const mintAmount = ethers.parseEther("1000");
    await ecoCreditToken.mint(deployer.address, mintAmount);
    console.log("✅ Minted 1000 ECO tokens to deployer");

    // Test minting SustainabilityProof NFT
    const carbonImpact = ethers.parseEther("2.5");
    await sustainabilityProof.mintSustainabilityProof(
      deployer.address,
      carbonImpact,
      "sustainability_document",
      "QmTestHash123"
    );
    console.log("✅ Minted SustainabilityProof NFT to deployer");

    // Test registering proof
    await proofRegistry.registerProof(
      deployer.address,
      "sustainability_document",
      carbonImpact,
      "QmTestHash123"
    );
    console.log("✅ Registered proof in ProofRegistry");

    // 8. Generate deployment summary
    console.log("\n📊 Deployment Summary:");
    console.log("=" * 50);
    console.log(`🌐 Network: ${deploymentInfo.network.name} (${deploymentInfo.network.chainId})`);
    console.log(`👤 Deployer: ${deploymentInfo.deployer}`);
    console.log(`⏰ Timestamp: ${deploymentInfo.timestamp}`);
    console.log("\n📄 Contracts:");
    console.log(`  • EcoCreditToken: ${ecoCreditTokenAddress}`);
    console.log(`  • SustainabilityProof: ${sustainabilityProofAddress}`);
    console.log(`  • ProofRegistry: ${proofRegistryAddress}`);
    console.log("\n🔐 Roles Configured:");
    console.log(`  • MINTER_ROLE granted to deployer for ECO tokens`);
    console.log(`  • MINTER_ROLE granted to deployer for SP NFTs`);
    console.log(`  • REGISTRAR_ROLE granted to deployer for ProofRegistry`);
    console.log("\n📝 Proof Types Added:");
    proofTypes.forEach(type => console.log(`  • ${type}`));

    // 9. Save deployment info to file
    const fs = require('fs');
    const deploymentFile = `deployments/deployment-${Date.now()}.json`;
    
    // Create deployments directory if it doesn't exist
    if (!fs.existsSync('deployments')) {
      fs.mkdirSync('deployments');
    }
    
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
    console.log(`\n💾 Deployment info saved to: ${deploymentFile}`);

    // 10. Generate environment variables
    console.log("\n🔧 Environment Variables for .env file:");
    console.log("=" * 50);
    console.log(`ECO_CREDIT_TOKEN_ADDRESS=${ecoCreditTokenAddress}`);
    console.log(`SUSTAINABILITY_PROOF_ADDRESS=${sustainabilityProofAddress}`);
    console.log(`PROOF_REGISTRY_ADDRESS=${proofRegistryAddress}`);

    console.log("\n🎉 Deployment completed successfully!");
    console.log("\n📋 Next Steps:");
    console.log("1. Update your .env file with the contract addresses above");
    console.log("2. Update your frontend configuration");
    console.log("3. Test the contracts with your application");
    console.log("4. Consider verifying contracts on block explorer");

  } catch (error) {
    console.error("❌ Deployment failed:", error);
    throw error;
  }
}

// Execute deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
