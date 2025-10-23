import { expect } from "chai";
import { ethers } from "hardhat";
import { SustainabilityProof } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("SustainabilityProof", function () {
  let sustainabilityProof: SustainabilityProof;
  let owner: SignerWithAddress;
  let minter: SignerWithAddress;
  let user1: SignerWithAddress;
  let user2: SignerWithAddress;
  let addrs: SignerWithAddress[];

  const MINTER_ROLE = ethers.keccak256(ethers.toUtf8Bytes("MINTER_ROLE"));

  beforeEach(async function () {
    [owner, minter, user1, user2, ...addrs] = await ethers.getSigners();

    const SustainabilityProof = await ethers.getContractFactory("SustainabilityProof");
    sustainabilityProof = await SustainabilityProof.deploy();
    await sustainabilityProof.waitForDeployment();

    // Grant minter role to minter address
    await sustainabilityProof.grantRole(MINTER_ROLE, minter.address);
  });

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      expect(await sustainabilityProof.name()).to.equal("Sustainability Proof");
      expect(await sustainabilityProof.symbol()).to.equal("SP");
    });

    it("Should set the correct base URI", async function () {
      expect(await sustainabilityProof.baseURI()).to.equal("https://gateway.lighthouse.storage/ipfs/");
    });

    it("Should set the correct roles", async function () {
      const DEFAULT_ADMIN_ROLE = await sustainabilityProof.DEFAULT_ADMIN_ROLE();
      expect(await sustainabilityProof.hasRole(DEFAULT_ADMIN_ROLE, owner.address)).to.be.true;
    });

    it("Should start with zero total supply", async function () {
      expect(await sustainabilityProof.totalSupply()).to.equal(0);
    });
  });

  describe("Role Management", function () {
    it("Should allow admin to grant minter role", async function () {
      await sustainabilityProof.grantRole(MINTER_ROLE, user1.address);
      expect(await sustainabilityProof.hasRole(MINTER_ROLE, user1.address)).to.be.true;
    });

    it("Should allow admin to revoke minter role", async function () {
      await sustainabilityProof.grantRole(MINTER_ROLE, user1.address);
      await sustainabilityProof.revokeRole(MINTER_ROLE, user1.address);
      expect(await sustainabilityProof.hasRole(MINTER_ROLE, user1.address)).to.be.false;
    });

    it("Should not allow non-admin to grant roles", async function () {
      await expect(
        sustainabilityProof.connect(user1).grantRole(MINTER_ROLE, user2.address)
      ).to.be.revertedWithCustomError(sustainabilityProof, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Minting", function () {
    const carbonImpact = ethers.parseEther("2.5"); // 2.5 kg CO2
    const proofType = "sustainability_document";
    const metadataURI = "QmTestHash123";

    it("Should allow minter to mint NFT", async function () {
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        proofType,
        metadataURI
      );

      expect(await sustainabilityProof.balanceOf(user1.address)).to.equal(1);
      expect(await sustainabilityProof.totalSupply()).to.equal(1);
    });

    it("Should not allow non-minter to mint NFT", async function () {
      await expect(
        sustainabilityProof.connect(user1).mintSustainabilityProof(
          user2.address,
          carbonImpact,
          proofType,
          metadataURI
        )
      ).to.be.revertedWithCustomError(sustainabilityProof, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow minting to zero address", async function () {
      await expect(
        sustainabilityProof.connect(minter).mintSustainabilityProof(
          ethers.ZeroAddress,
          carbonImpact,
          proofType,
          metadataURI
        )
      ).to.be.revertedWithCustomError(sustainabilityProof, "ERC721InvalidReceiver");
    });

    it("Should not allow minting with zero carbon impact", async function () {
      await expect(
        sustainabilityProof.connect(minter).mintSustainabilityProof(
          user1.address,
          0,
          proofType,
          metadataURI
        )
      ).to.be.revertedWith("SustainabilityProof: carbon impact must be greater than 0");
    });

    it("Should emit Mint event", async function () {
      await expect(
        sustainabilityProof.connect(minter).mintSustainabilityProof(
          user1.address,
          carbonImpact,
          proofType,
          metadataURI
        )
      ).to.emit(sustainabilityProof, "Mint")
      .withArgs(user1.address, 1, carbonImpact, proofType, metadataURI);
    });

    it("Should emit Transfer event", async function () {
      await expect(
        sustainabilityProof.connect(minter).mintSustainabilityProof(
          user1.address,
          carbonImpact,
          proofType,
          metadataURI
        )
      ).to.emit(sustainabilityProof, "Transfer")
      .withArgs(ethers.ZeroAddress, user1.address, 1);
    });

    it("Should store correct token data", async function () {
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        proofType,
        metadataURI
      );

      const tokenData = await sustainabilityProof.getTokenData(1);
      expect(tokenData.carbonImpact).to.equal(carbonImpact);
      expect(tokenData.proofType).to.equal(proofType);
      expect(tokenData.metadataURI).to.equal(metadataURI);
    });

    it("Should return correct token URI", async function () {
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        proofType,
        metadataURI
      );

      const tokenURI = await sustainabilityProof.tokenURI(1);
      expect(tokenURI).to.equal(`https://gateway.lighthouse.storage/ipfs/${metadataURI}`);
    });
  });

  describe("Token Data Management", function () {
    const carbonImpact = ethers.parseEther("2.5");
    const proofType = "sustainability_document";
    const metadataURI = "QmTestHash123";

    beforeEach(async function () {
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        proofType,
        metadataURI
      );
    });

    it("Should return correct token data", async function () {
      const tokenData = await sustainabilityProof.getTokenData(1);
      expect(tokenData.carbonImpact).to.equal(carbonImpact);
      expect(tokenData.proofType).to.equal(proofType);
      expect(tokenData.metadataURI).to.equal(metadataURI);
    });

    it("Should revert for non-existent token", async function () {
      await expect(sustainabilityProof.getTokenData(999))
        .to.be.revertedWith("SustainabilityProof: token does not exist");
    });

    it("Should return correct token count for user", async function () {
      expect(await sustainabilityProof.getTokenCount(user1.address)).to.equal(1);
      expect(await sustainabilityProof.getTokenCount(user2.address)).to.equal(0);
    });

    it("Should return correct token IDs for user", async function () {
      const tokenIds = await sustainabilityProof.getTokenIds(user1.address);
      expect(tokenIds).to.deep.equal([1]);
    });
  });

  describe("Transfers", function () {
    const carbonImpact = ethers.parseEther("2.5");
    const proofType = "sustainability_document";
    const metadataURI = "QmTestHash123";

    beforeEach(async function () {
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        proofType,
        metadataURI
      );
    });

    it("Should allow users to transfer NFTs", async function () {
      await sustainabilityProof.connect(user1).transferFrom(user1.address, user2.address, 1);
      
      expect(await sustainabilityProof.balanceOf(user1.address)).to.equal(0);
      expect(await sustainabilityProof.balanceOf(user2.address)).to.equal(1);
      expect(await sustainabilityProof.ownerOf(1)).to.equal(user2.address);
    });

    it("Should not allow transferring to zero address", async function () {
      await expect(
        sustainabilityProof.connect(user1).transferFrom(user1.address, ethers.ZeroAddress, 1)
      ).to.be.revertedWithCustomError(sustainabilityProof, "ERC721InvalidReceiver");
    });

    it("Should not allow transferring from zero address", async function () {
      await expect(
        sustainabilityProof.connect(user1).transferFrom(ethers.ZeroAddress, user2.address, 1)
      ).to.be.revertedWithCustomError(sustainabilityProof, "ERC721InvalidSender");
    });

    it("Should not allow transferring non-existent token", async function () {
      await expect(
        sustainabilityProof.connect(user1).transferFrom(user1.address, user2.address, 999)
      ).to.be.revertedWithCustomError(sustainabilityProof, "ERC721NonexistentToken");
    });

    it("Should not allow unauthorized transfers", async function () {
      await expect(
        sustainabilityProof.connect(user2).transferFrom(user1.address, user2.address, 1)
      ).to.be.revertedWithCustomError(sustainabilityProof, "ERC721InsufficientApproval");
    });

    it("Should emit Transfer event", async function () {
      await expect(
        sustainabilityProof.connect(user1).transferFrom(user1.address, user2.address, 1)
      ).to.emit(sustainabilityProof, "Transfer")
      .withArgs(user1.address, user2.address, 1);
    });
  });

  describe("Approvals", function () {
    const carbonImpact = ethers.parseEther("2.5");
    const proofType = "sustainability_document";
    const metadataURI = "QmTestHash123";

    beforeEach(async function () {
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        proofType,
        metadataURI
      );
    });

    it("Should allow users to approve spending", async function () {
      await sustainabilityProof.connect(user1).approve(user2.address, 1);
      expect(await sustainabilityProof.getApproved(1)).to.equal(user2.address);
    });

    it("Should emit Approval event", async function () {
      await expect(sustainabilityProof.connect(user1).approve(user2.address, 1))
        .to.emit(sustainabilityProof, "Approval")
        .withArgs(user1.address, user2.address, 1);
    });

    it("Should allow approved spender to transfer NFT", async function () {
      await sustainabilityProof.connect(user1).approve(user2.address, 1);
      await sustainabilityProof.connect(user2).transferFrom(user1.address, user2.address, 1);
      
      expect(await sustainabilityProof.ownerOf(1)).to.equal(user2.address);
    });

    it("Should not allow transferring more than approved", async function () {
      await sustainabilityProof.connect(user1).approve(user2.address, 1);
      await sustainabilityProof.connect(user2).transferFrom(user1.address, user2.address, 1);
      
      // Token 1 is now owned by user2, so user2 can't transfer it again
      await expect(
        sustainabilityProof.connect(user2).transferFrom(user1.address, user2.address, 1)
      ).to.be.revertedWithCustomError(sustainabilityProof, "ERC721InsufficientApproval");
    });
  });

  describe("Base URI Management", function () {
    it("Should allow admin to update base URI", async function () {
      const newBaseURI = "https://new-gateway.com/ipfs/";
      await sustainabilityProof.setBaseURI(newBaseURI);
      expect(await sustainabilityProof.baseURI()).to.equal(newBaseURI);
    });

    it("Should not allow non-admin to update base URI", async function () {
      const newBaseURI = "https://new-gateway.com/ipfs/";
      await expect(
        sustainabilityProof.connect(user1).setBaseURI(newBaseURI)
      ).to.be.revertedWithCustomError(sustainabilityProof, "AccessControlUnauthorizedAccount");
    });

    it("Should emit BaseURIUpdated event", async function () {
      const newBaseURI = "https://new-gateway.com/ipfs/";
      await expect(sustainabilityProof.setBaseURI(newBaseURI))
        .to.emit(sustainabilityProof, "BaseURIUpdated")
        .withArgs(newBaseURI);
    });
  });

  describe("Edge Cases", function () {
    it("Should handle multiple mints to same user", async function () {
      const carbonImpact1 = ethers.parseEther("2.5");
      const carbonImpact2 = ethers.parseEther("3.0");
      
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact1,
        "type1",
        "hash1"
      );
      
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact2,
        "type2",
        "hash2"
      );

      expect(await sustainabilityProof.balanceOf(user1.address)).to.equal(2);
      expect(await sustainabilityProof.totalSupply()).to.equal(2);
    });

    it("Should handle minting with different proof types", async function () {
      const proofTypes = ["sustainability_document", "carbon_footprint_report", "energy_audit"];
      
      for (let i = 0; i < proofTypes.length; i++) {
        await sustainabilityProof.connect(minter).mintSustainabilityProof(
          user1.address,
          ethers.parseEther("1.0"),
          proofTypes[i],
          `hash${i}`
        );
      }

      expect(await sustainabilityProof.balanceOf(user1.address)).to.equal(3);
    });

    it("Should handle large carbon impact values", async function () {
      const largeCarbonImpact = ethers.parseEther("1000000"); // 1M kg CO2
      
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        largeCarbonImpact,
        "large_impact",
        "hash"
      );

      const tokenData = await sustainabilityProof.getTokenData(1);
      expect(tokenData.carbonImpact).to.equal(largeCarbonImpact);
    });
  });

  describe("Gas Optimization", function () {
    it("Should have reasonable gas costs for minting", async function () {
      const carbonImpact = ethers.parseEther("2.5");
      const tx = await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        "test_type",
        "test_hash"
      );
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 200k gas)
      expect(receipt!.gasUsed).to.be.lessThan(200000);
    });

    it("Should have reasonable gas costs for transfers", async function () {
      const carbonImpact = ethers.parseEther("2.5");
      await sustainabilityProof.connect(minter).mintSustainabilityProof(
        user1.address,
        carbonImpact,
        "test_type",
        "test_hash"
      );

      const tx = await sustainabilityProof.connect(user1).transferFrom(user1.address, user2.address, 1);
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 100k gas)
      expect(receipt!.gasUsed).to.be.lessThan(100000);
    });
  });
});
