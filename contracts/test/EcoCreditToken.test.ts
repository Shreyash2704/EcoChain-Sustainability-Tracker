import { expect } from "chai";
import { ethers } from "hardhat";
import { EcoCreditToken } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("EcoCreditToken", function () {
  let ecoCreditToken: EcoCreditToken;
  let owner: SignerWithAddress;
  let minter: SignerWithAddress;
  let user1: SignerWithAddress;
  let user2: SignerWithAddress;
  let addrs: SignerWithAddress[];

  const MINTER_ROLE = ethers.keccak256(ethers.toUtf8Bytes("MINTER_ROLE"));
  const BURNER_ROLE = ethers.keccak256(ethers.toUtf8Bytes("BURNER_ROLE"));

  beforeEach(async function () {
    [owner, minter, user1, user2, ...addrs] = await ethers.getSigners();

    const EcoCreditToken = await ethers.getContractFactory("EcoCreditToken");
    ecoCreditToken = await EcoCreditToken.deploy();
    await ecoCreditToken.waitForDeployment();

    // Grant minter role to minter address
    await ecoCreditToken.grantRole(MINTER_ROLE, minter.address);
    await ecoCreditToken.grantRole(BURNER_ROLE, minter.address);
  });

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      expect(await ecoCreditToken.name()).to.equal("EcoCredit Token");
      expect(await ecoCreditToken.symbol()).to.equal("ECO");
    });

    it("Should set the correct decimals", async function () {
      expect(await ecoCreditToken.decimals()).to.equal(18);
    });

    it("Should set the correct initial supply", async function () {
      const initialSupply = await ecoCreditToken.totalSupply();
      expect(initialSupply).to.equal(ethers.parseEther("10000000")); // 10M tokens
    });

    it("Should assign the total supply to the owner", async function () {
      const ownerBalance = await ecoCreditToken.balanceOf(owner.address);
      expect(await ecoCreditToken.totalSupply()).to.equal(ownerBalance);
    });

    it("Should set the correct roles", async function () {
      const DEFAULT_ADMIN_ROLE = await ecoCreditToken.DEFAULT_ADMIN_ROLE();
      expect(await ecoCreditToken.hasRole(DEFAULT_ADMIN_ROLE, owner.address)).to.be.true;
    });
  });

  describe("Role Management", function () {
    it("Should allow admin to grant minter role", async function () {
      await ecoCreditToken.grantRole(MINTER_ROLE, user1.address);
      expect(await ecoCreditToken.hasRole(MINTER_ROLE, user1.address)).to.be.true;
    });

    it("Should allow admin to revoke minter role", async function () {
      await ecoCreditToken.grantRole(MINTER_ROLE, user1.address);
      await ecoCreditToken.revokeRole(MINTER_ROLE, user1.address);
      expect(await ecoCreditToken.hasRole(MINTER_ROLE, user1.address)).to.be.false;
    });

    it("Should not allow non-admin to grant roles", async function () {
      await expect(
        ecoCreditToken.connect(user1).grantRole(MINTER_ROLE, user2.address)
      ).to.be.revertedWithCustomError(ecoCreditToken, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow non-admin to revoke roles", async function () {
      await expect(
        ecoCreditToken.connect(user1).revokeRole(MINTER_ROLE, minter.address)
      ).to.be.revertedWithCustomError(ecoCreditToken, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Minting", function () {
    it("Should allow minter to mint tokens", async function () {
      const mintAmount = ethers.parseEther("1000");
      await ecoCreditToken.connect(minter).mint(user1.address, mintAmount);
      
      expect(await ecoCreditToken.balanceOf(user1.address)).to.equal(mintAmount);
    });

    it("Should not allow non-minter to mint tokens", async function () {
      const mintAmount = ethers.parseEther("1000");
      await expect(
        ecoCreditToken.connect(user1).mint(user2.address, mintAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow minting to zero address", async function () {
      const mintAmount = ethers.parseEther("1000");
      await expect(
        ecoCreditToken.connect(minter).mint(ethers.ZeroAddress, mintAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "ERC20InvalidReceiver");
    });

    it("Should emit Mint event", async function () {
      const mintAmount = ethers.parseEther("1000");
      await expect(ecoCreditToken.connect(minter).mint(user1.address, mintAmount))
        .to.emit(ecoCreditToken, "Mint")
        .withArgs(user1.address, mintAmount);
    });

    it("Should update total supply when minting", async function () {
      const initialSupply = await ecoCreditToken.totalSupply();
      const mintAmount = ethers.parseEther("1000");
      
      await ecoCreditToken.connect(minter).mint(user1.address, mintAmount);
      
      const newSupply = await ecoCreditToken.totalSupply();
      expect(newSupply).to.equal(initialSupply + mintAmount);
    });
  });

  describe("Burning", function () {
    beforeEach(async function () {
      // Mint some tokens to user1 for burning tests
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("1000"));
    });

    it("Should allow minter to burn tokens", async function () {
      const burnAmount = ethers.parseEther("100");
      const initialBalance = await ecoCreditToken.balanceOf(user1.address);
      
      await ecoCreditToken.connect(minter).burn(user1.address, burnAmount);
      
      expect(await ecoCreditToken.balanceOf(user1.address)).to.equal(initialBalance - burnAmount);
    });

    it("Should not allow non-minter to burn tokens", async function () {
      const burnAmount = ethers.parseEther("100");
      await expect(
        ecoCreditToken.connect(user1).burn(user1.address, burnAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow burning from zero address", async function () {
      const burnAmount = ethers.parseEther("100");
      await expect(
        ecoCreditToken.connect(minter).burn(ethers.ZeroAddress, burnAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "ERC20InvalidSender");
    });

    it("Should not allow burning more than balance", async function () {
      const balance = await ecoCreditToken.balanceOf(user1.address);
      const burnAmount = balance + ethers.parseEther("1");
      
      await expect(
        ecoCreditToken.connect(minter).burn(user1.address, burnAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "ERC20InsufficientBalance");
    });

    it("Should emit Burn event", async function () {
      const burnAmount = ethers.parseEther("100");
      await expect(ecoCreditToken.connect(minter).burn(user1.address, burnAmount))
        .to.emit(ecoCreditToken, "Burn")
        .withArgs(user1.address, burnAmount);
    });

    it("Should update total supply when burning", async function () {
      const initialSupply = await ecoCreditToken.totalSupply();
      const burnAmount = ethers.parseEther("100");
      
      await ecoCreditToken.connect(minter).burn(user1.address, burnAmount);
      
      const newSupply = await ecoCreditToken.totalSupply();
      expect(newSupply).to.equal(initialSupply - burnAmount);
    });
  });

  describe("Transfers", function () {
    beforeEach(async function () {
      // Mint some tokens to user1 for transfer tests
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("1000"));
    });

    it("Should allow users to transfer tokens", async function () {
      const transferAmount = ethers.parseEther("100");
      await ecoCreditToken.connect(user1).transfer(user2.address, transferAmount);
      
      expect(await ecoCreditToken.balanceOf(user2.address)).to.equal(transferAmount);
    });

    it("Should not allow transferring more than balance", async function () {
      const balance = await ecoCreditToken.balanceOf(user1.address);
      const transferAmount = balance + ethers.parseEther("1");
      
      await expect(
        ecoCreditToken.connect(user1).transfer(user2.address, transferAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "ERC20InsufficientBalance");
    });

    it("Should not allow transferring to zero address", async function () {
      const transferAmount = ethers.parseEther("100");
      await expect(
        ecoCreditToken.connect(user1).transfer(ethers.ZeroAddress, transferAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "ERC20InvalidReceiver");
    });

    it("Should emit Transfer event", async function () {
      const transferAmount = ethers.parseEther("100");
      await expect(ecoCreditToken.connect(user1).transfer(user2.address, transferAmount))
        .to.emit(ecoCreditToken, "Transfer")
        .withArgs(user1.address, user2.address, transferAmount);
    });
  });

  describe("Approvals", function () {
    beforeEach(async function () {
      // Mint some tokens to user1 for approval tests
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("1000"));
    });

    it("Should allow users to approve spending", async function () {
      const approveAmount = ethers.parseEther("100");
      await ecoCreditToken.connect(user1).approve(user2.address, approveAmount);
      
      expect(await ecoCreditToken.allowance(user1.address, user2.address)).to.equal(approveAmount);
    });

    it("Should emit Approval event", async function () {
      const approveAmount = ethers.parseEther("100");
      await expect(ecoCreditToken.connect(user1).approve(user2.address, approveAmount))
        .to.emit(ecoCreditToken, "Approval")
        .withArgs(user1.address, user2.address, approveAmount);
    });

    it("Should allow approved spender to transfer tokens", async function () {
      const approveAmount = ethers.parseEther("100");
      await ecoCreditToken.connect(user1).approve(user2.address, approveAmount);
      
      await ecoCreditToken.connect(user2).transferFrom(user1.address, user2.address, approveAmount);
      
      expect(await ecoCreditToken.balanceOf(user2.address)).to.equal(approveAmount);
    });

    it("Should not allow transferring more than approved amount", async function () {
      const approveAmount = ethers.parseEther("100");
      const transferAmount = ethers.parseEther("200");
      
      await ecoCreditToken.connect(user1).approve(user2.address, approveAmount);
      
      await expect(
        ecoCreditToken.connect(user2).transferFrom(user1.address, user2.address, transferAmount)
      ).to.be.revertedWithCustomError(ecoCreditToken, "ERC20InsufficientAllowance");
    });
  });

  describe("Edge Cases", function () {
    it("Should handle zero amount minting", async function () {
      await ecoCreditToken.connect(minter).mint(user1.address, 0);
      expect(await ecoCreditToken.balanceOf(user1.address)).to.equal(0);
    });

    it("Should handle zero amount burning", async function () {
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("100"));
      await ecoCreditToken.connect(minter).burn(user1.address, 0);
      expect(await ecoCreditToken.balanceOf(user1.address)).to.equal(ethers.parseEther("100"));
    });

    it("Should handle zero amount transfers", async function () {
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("100"));
      await ecoCreditToken.connect(user1).transfer(user2.address, 0);
      expect(await ecoCreditToken.balanceOf(user2.address)).to.equal(0);
    });

    it("Should handle self-transfer", async function () {
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("100"));
      await ecoCreditToken.connect(user1).transfer(user1.address, ethers.parseEther("50"));
      expect(await ecoCreditToken.balanceOf(user1.address)).to.equal(ethers.parseEther("100"));
    });
  });

  describe("Gas Optimization", function () {
    it("Should have reasonable gas costs for minting", async function () {
      const mintAmount = ethers.parseEther("1000");
      const tx = await ecoCreditToken.connect(minter).mint(user1.address, mintAmount);
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 100k gas)
      expect(receipt!.gasUsed).to.be.lessThan(100000);
    });

    it("Should have reasonable gas costs for burning", async function () {
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("1000"));
      const burnAmount = ethers.parseEther("100");
      const tx = await ecoCreditToken.connect(minter).burn(user1.address, burnAmount);
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 100k gas)
      expect(receipt!.gasUsed).to.be.lessThan(100000);
    });

    it("Should have reasonable gas costs for transfers", async function () {
      await ecoCreditToken.connect(minter).mint(user1.address, ethers.parseEther("1000"));
      const transferAmount = ethers.parseEther("100");
      const tx = await ecoCreditToken.connect(user1).transfer(user2.address, transferAmount);
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 100k gas)
      expect(receipt!.gasUsed).to.be.lessThan(100000);
    });
  });
});