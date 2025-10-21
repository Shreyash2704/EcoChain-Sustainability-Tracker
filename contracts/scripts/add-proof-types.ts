import { ethers } from "hardhat";
import { network } from "hardhat";

async function main() {
    console.log("🔐 Adding Proof Types to Proof Registry...");
    
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
    
    // Proof types we need to add
    const proofTypesToAdd = [
        "sustainability_document",
        "sustainability_report", 
        "proof_of_impact",
        "carbon_footprint_report",
        "energy_efficiency_report"
    ];
    
    console.log("\n🔐 Adding proof types...");
    
    for (const proofType of proofTypesToAdd) {
        try {
            console.log(`📝 Adding proof type: ${proofType}`);
            
            // Check if it already exists by trying to add it
            const tx = await proofRegistry.addProofType(proofType);
            console.log("📝 Transaction hash:", tx.hash);
            
            console.log("⏳ Waiting for confirmation...");
            const receipt = await tx.wait();
            console.log("✅ Transaction confirmed in block:", receipt?.blockNumber);
            console.log(`✅ Successfully added: ${proofType}`);
            
        } catch (error: any) {
            if (error.message.includes("proof type already exists")) {
                console.log(`✅ ${proofType} already exists`);
            } else {
                console.error(`❌ Failed to add ${proofType}:`, error.message);
            }
        }
    }
    
    console.log("\n🎉 Proof types setup complete!");
    console.log("📋 Next Steps:");
    console.log("1. Test proof registration in the backend");
    console.log("2. Verify transactions on Blockscout");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Error:", error);
        process.exit(1);
    });
