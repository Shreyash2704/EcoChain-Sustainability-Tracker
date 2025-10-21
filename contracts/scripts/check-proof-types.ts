import { ethers } from "hardhat";
import { network } from "hardhat";

async function main() {
    console.log("🔍 Checking Proof Registry Valid Proof Types...");
    
    // Get the network connection
    const { ethers } = await network.connect();
    
    // Contract addresses
    const PROOF_REGISTRY_ADDRESS = "0xc3f19798eC4aB47734209f99cAF63B6Fd9a04081";
    
    // Get the deployer account
    const [deployer] = await ethers.getSigners();
    console.log("📝 Using account:", deployer.address);
    console.log("📝 Account balance:", ethers.formatEther(await deployer.provider.getBalance(deployer.address)), "ETH");
    
    // Get the ProofRegistry contract
    const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
    const proofRegistry = ProofRegistry.attach(PROOF_REGISTRY_ADDRESS);
    
    console.log("📋 Proof Registry Address:", PROOF_REGISTRY_ADDRESS);
    
    // Check current proof types
    console.log("\n🔍 Checking current proof types...");
    
    try {
        // Get all proof types
        const proofTypesCount = await proofRegistry.getProofTypesCount();
        console.log("📊 Total proof types registered:", proofTypesCount.toString());
        
        // Check specific proof types we use
        const proofTypesToCheck = [
            "sustainability_document",
            "sustainability_report", 
            "proof_of_impact",
            "carbon_footprint_report",
            "energy_efficiency_report"
        ];
        
        console.log("\n🔍 Checking proof types we use:");
        for (const proofType of proofTypesToCheck) {
            const isValid = await proofRegistry.isValidProofType(proofType);
            console.log(`   ${proofType}: ${isValid ? '✅ Valid' : '❌ Invalid'}`);
        }
        
        // If any are invalid, add them
        console.log("\n🔐 Adding missing proof types...");
        for (const proofType of proofTypesToCheck) {
            const isValid = await proofRegistry.isValidProofType(proofType);
            if (!isValid) {
                console.log(`📝 Adding proof type: ${proofType}`);
                try {
                    const tx = await proofRegistry.addProofType(proofType);
                    console.log("📝 Transaction hash:", tx.hash);
                    
                    console.log("⏳ Waiting for confirmation...");
                    const receipt = await tx.wait();
                    console.log("✅ Transaction confirmed in block:", receipt?.blockNumber);
                    
                    // Verify it was added
                    const nowValid = await proofRegistry.isValidProofType(proofType);
                    console.log(`✅ ${proofType} is now valid:`, nowValid);
                } catch (error) {
                    console.error(`❌ Failed to add ${proofType}:`, error);
                }
            } else {
                console.log(`✅ ${proofType} is already valid`);
            }
        }
        
        // Final verification
        console.log("\n🔍 Final verification:");
        for (const proofType of proofTypesToCheck) {
            const isValid = await proofRegistry.isValidProofType(proofType);
            console.log(`   ${proofType}: ${isValid ? '✅ Valid' : '❌ Invalid'}`);
        }
        
    } catch (error) {
        console.error("❌ Error checking proof types:", error);
    }
    
    console.log("\n📋 Next Steps:");
    console.log("1. Test proof registration with valid proof types");
    console.log("2. Verify transactions on Blockscout");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Error:", error);
        process.exit(1);
    });
