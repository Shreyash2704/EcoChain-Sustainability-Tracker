import { expect } from "chai";
import { ethers } from "hardhat";
import { ProofRegistry } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("ProofRegistry", function () {
  let proofRegistry: ProofRegistry;
  let owner: SignerWithAddress;
  let registrar: SignerWithAddress;
  let user1: SignerWithAddress;
  let user2: SignerWithAddress;
  let addrs: SignerWithAddress[];

  const REGISTRAR_ROLE = ethers.keccak256(ethers.toUtf8Bytes("REGISTRAR_ROLE"));

  beforeEach(async function () {
    [owner, registrar, user1, user2, ...addrs] = await ethers.getSigners();

    const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
    proofRegistry = await ProofRegistry.deploy();
    await proofRegistry.waitForDeployment();

    // Grant registrar role to registrar address
    await proofRegistry.grantRole(REGISTRAR_ROLE, registrar.address);
  });

  describe("Deployment", function () {
    it("Should set the correct roles", async function () {
      const DEFAULT_ADMIN_ROLE = await proofRegistry.DEFAULT_ADMIN_ROLE();
      expect(await proofRegistry.hasRole(DEFAULT_ADMIN_ROLE, owner.address)).to.be.true;
    });

    it("Should start with zero proof count", async function () {
      expect(await proofRegistry.getProofCount()).to.equal(0);
    });
  });

  describe("Role Management", function () {
    it("Should allow admin to grant registrar role", async function () {
      await proofRegistry.grantRole(REGISTRAR_ROLE, user1.address);
      expect(await proofRegistry.hasRole(REGISTRAR_ROLE, user1.address)).to.be.true;
    });

    it("Should allow admin to revoke registrar role", async function () {
      await proofRegistry.grantRole(REGISTRAR_ROLE, user1.address);
      await proofRegistry.revokeRole(REGISTRAR_ROLE, user1.address);
      expect(await proofRegistry.hasRole(REGISTRAR_ROLE, user1.address)).to.be.false;
    });

    it("Should not allow non-admin to grant roles", async function () {
      await expect(
        proofRegistry.connect(user1).grantRole(REGISTRAR_ROLE, user2.address)
      ).to.be.revertedWithCustomError(proofRegistry, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Proof Type Management", function () {
    it("Should allow admin to add proof types", async function () {
      const proofType = "sustainability_document";
      await proofRegistry.addProofType(proofType);
      expect(await proofRegistry.isValidProofType(proofType)).to.be.true;
    });

    it("Should not allow non-admin to add proof types", async function () {
      const proofType = "sustainability_document";
      await expect(
        proofRegistry.connect(user1).addProofType(proofType)
      ).to.be.revertedWithCustomError(proofRegistry, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow adding duplicate proof types", async function () {
      const proofType = "sustainability_document";
      await proofRegistry.addProofType(proofType);
      
      await expect(
        proofRegistry.addProofType(proofType)
      ).to.be.revertedWith("ProofRegistry: proof type already exists");
    });

    it("Should emit ProofTypeAdded event", async function () {
      const proofType = "sustainability_document";
      await expect(proofRegistry.addProofType(proofType))
        .to.emit(proofRegistry, "ProofTypeAdded")
        .withArgs(proofType);
    });

    it("Should return correct proof types", async function () {
      const proofTypes = ["sustainability_document", "carbon_footprint_report", "energy_audit"];
      
      for (const proofType of proofTypes) {
        await proofRegistry.addProofType(proofType);
      }

      const allProofTypes = await proofRegistry.getAllProofTypes();
      expect(allProofTypes).to.deep.equal(proofTypes);
    });
  });

  describe("Proof Registration", function () {
    const proofType = "sustainability_document";
    const carbonImpact = ethers.parseEther("2.5");
    const metadataURI = "QmTestHash123";

    beforeEach(async function () {
      await proofRegistry.addProofType(proofType);
    });

    it("Should allow registrar to register proof", async function () {
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        carbonImpact,
        metadataURI
      );

      expect(await proofRegistry.getProofCount()).to.equal(1);
      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(1);
    });

    it("Should not allow non-registrar to register proof", async function () {
      await expect(
        proofRegistry.connect(user1).registerProof(
          user2.address,
          proofType,
          carbonImpact,
          metadataURI
        )
      ).to.be.revertedWithCustomError(proofRegistry, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow registering proof with invalid type", async function () {
      const invalidProofType = "invalid_type";
      
      await expect(
        proofRegistry.connect(registrar).registerProof(
          user1.address,
          invalidProofType,
          carbonImpact,
          metadataURI
        )
      ).to.be.revertedWith("ProofRegistry: invalid proof type");
    });

    it("Should not allow registering proof with zero carbon impact", async function () {
      await expect(
        proofRegistry.connect(registrar).registerProof(
          user1.address,
          proofType,
          0,
          metadataURI
        )
      ).to.be.revertedWith("ProofRegistry: carbon impact must be greater than 0");
    });

    it("Should emit ProofRegistered event", async function () {
      await expect(
        proofRegistry.connect(registrar).registerProof(
          user1.address,
          proofType,
          carbonImpact,
          metadataURI
        )
      ).to.emit(proofRegistry, "ProofRegistered")
      .withArgs(1, user1.address, proofType, carbonImpact, metadataURI);
    });

    it("Should store correct proof data", async function () {
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        carbonImpact,
        metadataURI
      );

      const proofData = await proofRegistry.getProof(1);
      expect(proofData.user).to.equal(user1.address);
      expect(proofData.proofType).to.equal(proofType);
      expect(proofData.carbonImpact).to.equal(carbonImpact);
      expect(proofData.metadataURI).to.equal(metadataURI);
      expect(proofData.timestamp).to.be.greaterThan(0);
    });

    it("Should increment proof count", async function () {
      const initialCount = await proofRegistry.getProofCount();
      
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        carbonImpact,
        metadataURI
      );

      expect(await proofRegistry.getProofCount()).to.equal(initialCount + 1n);
    });

    it("Should increment user proof count", async function () {
      const initialUserCount = await proofRegistry.getUserProofCount(user1.address);
      
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        carbonImpact,
        metadataURI
      );

      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(initialUserCount + 1n);
    });
  });

  describe("Proof Retrieval", function () {
    const proofType = "sustainability_document";
    const carbonImpact = ethers.parseEther("2.5");
    const metadataURI = "QmTestHash123";

    beforeEach(async function () {
      await proofRegistry.addProofType(proofType);
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        carbonImpact,
        metadataURI
      );
    });

    it("Should return correct proof data", async function () {
      const proofData = await proofRegistry.getProof(1);
      expect(proofData.user).to.equal(user1.address);
      expect(proofData.proofType).to.equal(proofType);
      expect(proofData.carbonImpact).to.equal(carbonImpact);
      expect(proofData.metadataURI).to.equal(metadataURI);
    });

    it("Should revert for non-existent proof", async function () {
      await expect(proofRegistry.getProof(999))
        .to.be.revertedWith("ProofRegistry: proof does not exist");
    });

    it("Should return correct user proof count", async function () {
      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(1);
      expect(await proofRegistry.getUserProofCount(user2.address)).to.equal(0);
    });

    it("Should return correct user proof IDs", async function () {
      const userProofIds = await proofRegistry.getUserProofIds(user1.address);
      expect(userProofIds).to.deep.equal([1]);
    });

    it("Should return correct user proofs", async function () {
      const userProofs = await proofRegistry.getUserProofs(user1.address);
      expect(userProofs).to.have.length(1);
      expect(userProofs[0].user).to.equal(user1.address);
      expect(userProofs[0].proofType).to.equal(proofType);
    });
  });

  describe("Multiple Proofs", function () {
    const proofTypes = ["sustainability_document", "carbon_footprint_report"];
    const carbonImpacts = [ethers.parseEther("2.5"), ethers.parseEther("3.0")];
    const metadataURIs = ["QmHash1", "QmHash2"];

    beforeEach(async function () {
      for (const proofType of proofTypes) {
        await proofRegistry.addProofType(proofType);
      }
    });

    it("Should allow registering multiple proofs for same user", async function () {
      for (let i = 0; i < proofTypes.length; i++) {
        await proofRegistry.connect(registrar).registerProof(
          user1.address,
          proofTypes[i],
          carbonImpacts[i],
          metadataURIs[i]
        );
      }

      expect(await proofRegistry.getProofCount()).to.equal(2);
      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(2);
    });

    it("Should allow registering proofs for different users", async function () {
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofTypes[0],
        carbonImpacts[0],
        metadataURIs[0]
      );

      await proofRegistry.connect(registrar).registerProof(
        user2.address,
        proofTypes[1],
        carbonImpacts[1],
        metadataURIs[1]
      );

      expect(await proofRegistry.getProofCount()).to.equal(2);
      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(1);
      expect(await proofRegistry.getUserProofCount(user2.address)).to.equal(1);
    });

    it("Should return correct user proof IDs for multiple proofs", async function () {
      for (let i = 0; i < proofTypes.length; i++) {
        await proofRegistry.connect(registrar).registerProof(
          user1.address,
          proofTypes[i],
          carbonImpacts[i],
          metadataURIs[i]
        );
      }

      const userProofIds = await proofRegistry.getUserProofIds(user1.address);
      expect(userProofIds).to.deep.equal([1, 2]);
    });
  });

  describe("Edge Cases", function () {
    it("Should handle large proof counts", async function () {
      const proofType = "sustainability_document";
      await proofRegistry.addProofType(proofType);

      // Register multiple proofs
      for (let i = 0; i < 10; i++) {
        await proofRegistry.connect(registrar).registerProof(
          user1.address,
          proofType,
          ethers.parseEther("1.0"),
          `hash${i}`
        );
      }

      expect(await proofRegistry.getProofCount()).to.equal(10);
      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(10);
    });

    it("Should handle different proof types for same user", async function () {
      const proofTypes = ["sustainability_document", "carbon_footprint_report", "energy_audit"];
      
      for (const proofType of proofTypes) {
        await proofRegistry.addProofType(proofType);
      }

      for (let i = 0; i < proofTypes.length; i++) {
        await proofRegistry.connect(registrar).registerProof(
          user1.address,
          proofTypes[i],
          ethers.parseEther("1.0"),
          `hash${i}`
        );
      }

      expect(await proofRegistry.getUserProofCount(user1.address)).to.equal(3);
    });

    it("Should handle large carbon impact values", async function () {
      const proofType = "sustainability_document";
      const largeCarbonImpact = ethers.parseEther("1000000"); // 1M kg CO2
      
      await proofRegistry.addProofType(proofType);
      await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        largeCarbonImpact,
        "hash"
      );

      const proofData = await proofRegistry.getProof(1);
      expect(proofData.carbonImpact).to.equal(largeCarbonImpact);
    });
  });

  describe("Gas Optimization", function () {
    it("Should have reasonable gas costs for proof registration", async function () {
      const proofType = "sustainability_document";
      await proofRegistry.addProofType(proofType);

      const tx = await proofRegistry.connect(registrar).registerProof(
        user1.address,
        proofType,
        ethers.parseEther("2.5"),
        "QmHash"
      );
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 150k gas)
      expect(receipt!.gasUsed).to.be.lessThan(150000);
    });

    it("Should have reasonable gas costs for proof type addition", async function () {
      const tx = await proofRegistry.addProofType("sustainability_document");
      const receipt = await tx.wait();
      
      // Gas cost should be reasonable (less than 100k gas)
      expect(receipt!.gasUsed).to.be.lessThan(100000);
    });
  });

  describe("Access Control", function () {
    it("Should not allow non-registrar to register proofs", async function () {
      const proofType = "sustainability_document";
      await proofRegistry.addProofType(proofType);

      await expect(
        proofRegistry.connect(user1).registerProof(
          user2.address,
          proofType,
          ethers.parseEther("2.5"),
          "QmHash"
        )
      ).to.be.revertedWithCustomError(proofRegistry, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow non-admin to add proof types", async function () {
      await expect(
        proofRegistry.connect(user1).addProofType("sustainability_document")
      ).to.be.revertedWithCustomError(proofRegistry, "AccessControlUnauthorizedAccount");
    });
  });
});
