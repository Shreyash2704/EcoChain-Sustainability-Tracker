import { ethers } from "hardhat";
import { network } from "hardhat";

async function main() {
    console.log("🔐 Granting Proof Registry Roles to Agent...");
    
    // Get the network connection
    const { ethers } = await network.connect();
    
    // Contract addresses
    const PROOF_REGISTRY_ADDRESS = "0xc3f19798eC4aB47734209f99cAF63B6Fd9a04081";
    const AGENT_ADDRESS = "0xc90E6B2dD249C97D4408270a8bfD04d383A7c663";
    
    // Get the deployer account
    const [deployer] = await ethers.getSigners();
    console.log("📝 Using account:", deployer.address);
    console.log("📝 Account balance:", ethers.formatEther(await deployer.provider.getBalance(deployer.address)), "ETH");
    
    // Get the ProofRegistry contract
    const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
    const proofRegistry = ProofRegistry.attach(PROOF_REGISTRY_ADDRESS);
    
    console.log("📋 Proof Registry Address:", PROOF_REGISTRY_ADDRESS);
    console.log("🤖 Agent Address:", AGENT_ADDRESS);
    
    // Check current roles
    console.log("\n🔍 Checking current roles...");
    
    const DEFAULT_ADMIN_ROLE = await proofRegistry.DEFAULT_ADMIN_ROLE();
    const REGISTRAR_ROLE = await proofRegistry.REGISTRAR_ROLE();
    const VERIFIER_ROLE = await proofRegistry.VERIFIER_ROLE();
    
    console.log("📋 Role Hashes:");
    console.log("   DEFAULT_ADMIN_ROLE:", DEFAULT_ADMIN_ROLE);
    console.log("   REGISTRAR_ROLE:", REGISTRAR_ROLE);
    console.log("   VERIFIER_ROLE:", VERIFIER_ROLE);
    
    // Check if agent has roles
    const hasAdminRole = await proofRegistry.hasRole(DEFAULT_ADMIN_ROLE, AGENT_ADDRESS);
    const hasRegistrarRole = await proofRegistry.hasRole(REGISTRAR_ROLE, AGENT_ADDRESS);
    const hasVerifierRole = await proofRegistry.hasRole(VERIFIER_ROLE, AGENT_ADDRESS);
    
    console.log("\n🔍 Current Agent Roles:");
    console.log("   DEFAULT_ADMIN_ROLE:", hasAdminRole);
    console.log("   REGISTRAR_ROLE:", hasRegistrarRole);
    console.log("   VERIFIER_ROLE:", hasVerifierRole);
    
    // Grant REGISTRAR_ROLE to agent
    if (!hasRegistrarRole) {
        console.log("\n🔐 Granting REGISTRAR_ROLE to agent...");
        
        const tx = await proofRegistry.grantRole(REGISTRAR_ROLE, AGENT_ADDRESS);
        console.log("📝 Transaction hash:", tx.hash);
        
        console.log("⏳ Waiting for confirmation...");
        const receipt = await tx.wait();
        console.log("✅ Transaction confirmed in block:", receipt?.blockNumber);
        
        // Verify the role was granted
        const newHasRegistrarRole = await proofRegistry.hasRole(REGISTRAR_ROLE, AGENT_ADDRESS);
        console.log("✅ REGISTRAR_ROLE granted:", newHasRegistrarRole);
    } else {
        console.log("✅ Agent already has REGISTRAR_ROLE");
    }
    
    // Grant VERIFIER_ROLE to agent (optional, for future use)
    if (!hasVerifierRole) {
        console.log("\n🔐 Granting VERIFIER_ROLE to agent...");
        
        const tx = await proofRegistry.grantRole(VERIFIER_ROLE, AGENT_ADDRESS);
        console.log("📝 Transaction hash:", tx.hash);
        
        console.log("⏳ Waiting for confirmation...");
        const receipt = await tx.wait();
        console.log("✅ Transaction confirmed in block:", receipt?.blockNumber);
        
        // Verify the role was granted
        const newHasVerifierRole = await proofRegistry.hasRole(VERIFIER_ROLE, AGENT_ADDRESS);
        console.log("✅ VERIFIER_ROLE granted:", newHasVerifierRole);
    } else {
        console.log("✅ Agent already has VERIFIER_ROLE");
    }
    
    // Final verification
    console.log("\n🔍 Final Role Verification:");
    const finalHasRegistrarRole = await proofRegistry.hasRole(REGISTRAR_ROLE, AGENT_ADDRESS);
    const finalHasVerifierRole = await proofRegistry.hasRole(VERIFIER_ROLE, AGENT_ADDRESS);
    
    console.log("   REGISTRAR_ROLE:", finalHasRegistrarRole);
    console.log("   VERIFIER_ROLE:", finalHasVerifierRole);
    
    if (finalHasRegistrarRole && finalHasVerifierRole) {
        console.log("\n🎉 SUCCESS: Agent has all required roles!");
        console.log("✅ Proof Registry integration ready");
    } else {
        console.log("\n❌ ERROR: Some roles were not granted successfully");
    }
    
    console.log("\n📋 Next Steps:");
    console.log("1. Update Web3Service to re-enable proof registry calls");
    console.log("2. Test proof registration in the backend");
    console.log("3. Verify transactions on Blockscout");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Error:", error);
        process.exit(1);
    });
