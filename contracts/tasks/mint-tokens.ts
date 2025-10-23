import { task } from "hardhat/config";
import { HardhatRuntimeEnvironment } from "hardhat/types";

task("mint-tokens", "Mint ECO tokens to a specified address")
  .addParam("to", "Address to mint tokens to")
  .addParam("amount", "Amount of tokens to mint (in ECO)")
  .setAction(async (taskArgs, hre: HardhatRuntimeEnvironment) => {
    const { ethers } = hre;
    const [deployer] = await ethers.getSigners();
    
    console.log("🪙 Minting ECO tokens...");
    console.log("📝 To:", taskArgs.to);
    console.log("💰 Amount:", taskArgs.amount, "ECO");
    
    // Get the EcoCreditToken contract
    const ecoCreditTokenAddress = process.env.ECO_CREDIT_TOKEN_ADDRESS;
    if (!ecoCreditTokenAddress) {
      throw new Error("ECO_CREDIT_TOKEN_ADDRESS not set in environment");
    }
    
    const EcoCreditToken = await ethers.getContractFactory("EcoCreditToken");
    const ecoCreditToken = EcoCreditToken.attach(ecoCreditTokenAddress);
    
    // Check if deployer has MINTER_ROLE
    const MINTER_ROLE = await ecoCreditToken.MINTER_ROLE();
    const hasMinterRole = await ecoCreditToken.hasRole(MINTER_ROLE, deployer.address);
    
    if (!hasMinterRole) {
      throw new Error("Deployer does not have MINTER_ROLE");
    }
    
    // Convert amount to wei
    const amount = ethers.parseEther(taskArgs.amount);
    
    // Mint tokens
    const tx = await ecoCreditToken.mint(taskArgs.to, amount);
    console.log("⏳ Transaction submitted:", tx.hash);
    
    const receipt = await tx.wait();
    console.log("✅ Tokens minted successfully!");
    console.log("📊 Gas used:", receipt!.gasUsed.toString());
    
    // Check new balance
    const balance = await ecoCreditToken.balanceOf(taskArgs.to);
    console.log("💰 New balance:", ethers.formatEther(balance), "ECO");
  });
