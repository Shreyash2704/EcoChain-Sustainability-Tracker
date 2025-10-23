import { task } from "hardhat/config";
import { HardhatRuntimeEnvironment } from "hardhat/types";

task("register-proof", "Register a sustainability proof in the ProofRegistry")
  .addParam("user", "Address of the user")
  .addParam("proofType", "Type of sustainability proof")
  .addParam("carbonImpact", "Carbon impact amount (in kg CO2)")
  .addParam("metadataUri", "IPFS hash for metadata")
  .setAction(async (taskArgs, hre: HardhatRuntimeEnvironment) => {
    const { ethers } = hre;
    const [deployer] = await ethers.getSigners();
    
    console.log("📋 Registering sustainability proof...");
    console.log("👤 User:", taskArgs.user);
    console.log("📄 Proof Type:", taskArgs.proofType);
    console.log("🌱 Carbon Impact:", taskArgs.carbonImpact, "kg CO2");
    console.log("🔗 Metadata URI:", taskArgs.metadataUri);
    
    // Get the ProofRegistry contract
    const proofRegistryAddress = process.env.PROOF_REGISTRY_ADDRESS;
    if (!proofRegistryAddress) {
      throw new Error("PROOF_REGISTRY_ADDRESS not set in environment");
    }
    
    const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
    const proofRegistry = ProofRegistry.attach(proofRegistryAddress);
    
    // Check if deployer has REGISTRAR_ROLE
    const REGISTRAR_ROLE = await proofRegistry.REGISTRAR_ROLE();
    const hasRegistrarRole = await proofRegistry.hasRole(REGISTRAR_ROLE, deployer.address);
    
    if (!hasRegistrarRole) {
      throw new Error("Deployer does not have REGISTRAR_ROLE");
    }
    
    // Check if proof type is valid
    const isValidProofType = await proofRegistry.isValidProofType(taskArgs.proofType);
    if (!isValidProofType) {
      console.log("⚠️ Proof type is not valid. Available proof types:");
      const allProofTypes = await proofRegistry.getAllProofTypes();
      allProofTypes.forEach(type => console.log(`  • ${type}`));
      throw new Error(`Invalid proof type: ${taskArgs.proofType}`);
    }
    
    // Convert carbon impact to wei
    const carbonImpact = ethers.parseEther(taskArgs.carbonImpact);
    
    // Register proof
    const tx = await proofRegistry.registerProof(
      taskArgs.user,
      taskArgs.proofType,
      carbonImpact,
      taskArgs.metadataUri
    );
    console.log("⏳ Transaction submitted:", tx.hash);
    
    const receipt = await tx.wait();
    console.log("✅ Proof registered successfully!");
    console.log("📊 Gas used:", receipt!.gasUsed.toString());
    
    // Get proof ID from events
    const proofRegisteredEvent = receipt!.logs.find(log => {
      try {
        const parsed = proofRegistry.interface.parseLog(log);
        return parsed?.name === "ProofRegistered";
      } catch {
        return false;
      }
    });
    
    if (proofRegisteredEvent) {
      const parsed = proofRegistry.interface.parseLog(proofRegisteredEvent);
      const proofId = parsed?.args.proofId;
      console.log("🆔 Proof ID:", proofId?.toString());
    }
    
    // Check new proof count
    const proofCount = await proofRegistry.getProofCount();
    const userProofCount = await proofRegistry.getUserProofCount(taskArgs.user);
    console.log("📊 Total proofs:", proofCount.toString());
    console.log("👤 User proofs:", userProofCount.toString());
  });
