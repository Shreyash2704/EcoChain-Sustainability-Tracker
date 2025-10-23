import { task } from "hardhat/config";
import { HardhatRuntimeEnvironment } from "hardhat/types";

task("mint-nft", "Mint a SustainabilityProof NFT")
  .addParam("to", "Address to mint NFT to")
  .addParam("carbonImpact", "Carbon impact amount (in kg CO2)")
  .addParam("proofType", "Type of sustainability proof")
  .addParam("metadataUri", "IPFS hash for metadata")
  .setAction(async (taskArgs, hre: HardhatRuntimeEnvironment) => {
    const { ethers } = hre;
    const [deployer] = await ethers.getSigners();
    
    console.log("🎨 Minting SustainabilityProof NFT...");
    console.log("📝 To:", taskArgs.to);
    console.log("🌱 Carbon Impact:", taskArgs.carbonImpact, "kg CO2");
    console.log("📄 Proof Type:", taskArgs.proofType);
    console.log("🔗 Metadata URI:", taskArgs.metadataUri);
    
    // Get the SustainabilityProof contract
    const sustainabilityProofAddress = process.env.SUSTAINABILITY_PROOF_ADDRESS;
    if (!sustainabilityProofAddress) {
      throw new Error("SUSTAINABILITY_PROOF_ADDRESS not set in environment");
    }
    
    const SustainabilityProof = await ethers.getContractFactory("SustainabilityProof");
    const sustainabilityProof = SustainabilityProof.attach(sustainabilityProofAddress);
    
    // Check if deployer has MINTER_ROLE
    const MINTER_ROLE = await sustainabilityProof.MINTER_ROLE();
    const hasMinterRole = await sustainabilityProof.hasRole(MINTER_ROLE, deployer.address);
    
    if (!hasMinterRole) {
      throw new Error("Deployer does not have MINTER_ROLE");
    }
    
    // Convert carbon impact to wei
    const carbonImpact = ethers.parseEther(taskArgs.carbonImpact);
    
    // Mint NFT
    const tx = await sustainabilityProof.mintSustainabilityProof(
      taskArgs.to,
      carbonImpact,
      taskArgs.proofType,
      taskArgs.metadataUri
    );
    console.log("⏳ Transaction submitted:", tx.hash);
    
    const receipt = await tx.wait();
    console.log("✅ NFT minted successfully!");
    console.log("📊 Gas used:", receipt!.gasUsed.toString());
    
    // Get token ID from events
    const mintEvent = receipt!.logs.find(log => {
      try {
        const parsed = sustainabilityProof.interface.parseLog(log);
        return parsed?.name === "Mint";
      } catch {
        return false;
      }
    });
    
    if (mintEvent) {
      const parsed = sustainabilityProof.interface.parseLog(mintEvent);
      const tokenId = parsed?.args.tokenId;
      console.log("🆔 Token ID:", tokenId?.toString());
    }
    
    // Check new balance
    const balance = await sustainabilityProof.balanceOf(taskArgs.to);
    console.log("🎨 NFT Balance:", balance.toString());
  });
