import { expect } from "chai";
import { ethers } from "hardhat";
import { EcoCreditToken } from "../typechain-types";

describe("EcoCreditToken", function () {
  let ecoCreditToken: EcoCreditToken;
  let owner: any;
  let minter: any;
  let user: any;
  let otherUser: any;

  beforeEach(async function () {
    [owner, minter, user, otherUser] = await ethers.getSigners();
    
    const EcoCreditToken = await ethers.getContractFactory("EcoCreditToken");
    ecoCreditToken = await EcoCreditToken.deploy(owner.address);
    await ecoCreditToken.waitForDeployment();
    
    // Grant minter role to minter account
    const MINTER_ROLE = await ecoCreditToken.MINTER_ROLE();
    await ecoCreditToken.grantRole(MINTER_ROLE, minter.address);
  });

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      expect(await ecoCreditToken.name()).to.equal("EcoCredit");
      expect(await ecoCreditToken.symbol()).to.equal("ECO");
    });

    it("Should set the correct decimals", async function () {
      expect(await ecoCreditToken.decimals()).to.equal(18);
    });

    it("Should mint initial supply to owner", async function () {
      const initialSupply = ethers.parseEther("10000000"); // 10M tokens
      expect(await ecoCreditToken.balanceOf(owner.address)).to.equal(initialSupply);
    });

    it("Should set the correct max supply", async function () {
      const maxSupply = ethers.parseEther("1000000000"); // 1B tokens
      const tokenInfo = await ecoCreditToken.getTokenInfo();
      expect(tokenInfo.maxSupply).to.equal(maxSupply);
    });

    it("Should grant admin roles to owner", async function () {
      const DEFAULT_ADMIN_ROLE = await ecoCreditToken.DEFAULT_ADMIN_ROLE();
      const MINTER_ROLE = await ecoCreditToken.MINTER_ROLE();
      const BURNER_ROLE = await ecoCreditToken.BURNER_ROLE();
      const PAUSER_ROLE = await ecoCreditToken.PAUSER_ROLE();

      expect(await ecoCreditToken.hasRole(DEFAULT_ADMIN_ROLE, owner.address)).to.be.true;
      expect(await ecoCreditToken.hasRole(MINTER_ROLE, owner.address)).to.be.true;
      expect(await ecoCreditToken.hasRole(BURNER_ROLE, owner.address)).to.be.true;
      expect(await ecoCreditToken.hasRole(PAUSER_ROLE, owner.address)).to.be.true;
    });
  });

  describe("Minting", function () {
    it("Should allow minter to mint tokens", async function () {
      const amount = ethers.parseEther("1000");
      const reason = "Sustainability reward";
      
      await expect(ecoCreditToken.connect(minter).mint(user.address, amount, reason))
        .to.emit(ecoCreditToken, "TokensMinted")
        .withArgs(user.address, amount, reason, 1, await getBlockTimestamp());
      
      expect(await ecoCreditToken.balanceOf(user.address)).to.equal(amount);
    });

    it("Should not allow non-minters to mint", async function () {
      const amount = ethers.parseEther("1000");
      const reason = "Test mint";
      
      await expect(
        ecoCreditToken.connect(user).mint(user.address, amount, reason)
      ).to.be.revertedWith("AccessControl: account");
    });

    it("Should not mint to zero address", async function () {
      const amount = ethers.parseEther("1000");
      const reason = "Test mint";
      
      await expect(
        ecoCreditToken.connect(minter).mint(ethers.ZeroAddress, amount, reason)
      ).to.be.revertedWith("EcoCreditToken: mint to zero address");
    });

    it("Should not mint zero amount", async function () {
      const amount = 0;
      const reason = "Test mint";
      
      await expect(
        ecoCreditToken.connect(minter).mint(user.address, amount, reason)
      ).to.be.revertedWith("EcoCreditToken: amount must be greater than 0");
    });

    it("Should not mint with empty reason", async function () {
      const amount = ethers.parseEther("1000");
      const reason = "";
      
      await expect(
        ecoCreditToken.connect(minter).mint(user.address, amount, reason)
      ).to.be.revertedWith("EcoCreditToken: reason cannot be empty");
    });

    it("Should not exceed max supply", async function () {
      const maxSupply = ethers.parseEther("1000000000"); // 1B tokens
      const currentSupply = await ecoCreditToken.totalSupply();
      const excessAmount = maxSupply - currentSupply + ethers.parseEther("1");
      const reason = "Test excess mint";
      
      await expect(
        ecoCreditToken.connect(minter).mint(user.address, excessAmount, reason)
      ).to.be.revertedWith("EcoCreditToken: exceeds max supply");
    });

    it("Should increment mint counter", async function () {
      const amount = ethers.parseEther("1000");
      const reason = "Test mint";
      
      const initialCount = await ecoCreditToken.getTotalMints();
      await ecoCreditToken.connect(minter).mint(user.address, amount, reason);
      const finalCount = await ecoCreditToken.getTotalMints();
      
      expect(finalCount).to.equal(initialCount + 1n);
    });

    it("Should store mint record", async function () {
      const amount = ethers.parseEther("1000");
      const reason = "Test mint";
      
      await ecoCreditToken.connect(minter).mint(user.address, amount, reason);
      const mintRecord = await ecoCreditToken.getMintRecord(1);
      
      expect(mintRecord.to).to.equal(user.address);
      expect(mintRecord.amount).to.equal(amount);
      expect(mintRecord.reason).to.equal(reason);
      expect(mintRecord.exists).to.be.true;
    });
  });

  describe("Burning", function () {
    beforeEach(async function () {
      // Mint some tokens to user for burning tests
      const amount = ethers.parseEther("1000");
      const reason = "Test mint for burning";
      await ecoCreditToken.connect(minter).mint(user.address, amount, reason);
    });

    it("Should allow burner to burn tokens", async function () {
      const BURNER_ROLE = await ecoCreditToken.BURNER_ROLE();
      await ecoCreditToken.grantRole(BURNER_ROLE, user.address);
      
      const amount = ethers.parseEther("100");
      const reason = "Carbon offset purchase";
      
      await expect(ecoCreditToken.connect(user).burn(amount, reason))
        .to.emit(ecoCreditToken, "TokensBurned")
        .withArgs(user.address, amount, reason, 1, await getBlockTimestamp());
      
      expect(await ecoCreditToken.balanceOf(user.address)).to.equal(ethers.parseEther("900"));
    });

    it("Should not allow non-burners to burn", async function () {
      const amount = ethers.parseEther("100");
      const reason = "Test burn";
      
      await expect(
        ecoCreditToken.connect(otherUser).burn(amount, reason)
      ).to.be.revertedWith("AccessControl: account");
    });

    it("Should not burn zero amount", async function () {
      const BURNER_ROLE = await ecoCreditToken.BURNER_ROLE();
      await ecoCreditToken.grantRole(BURNER_ROLE, user.address);
      
      const amount = 0;
      const reason = "Test burn";
      
      await expect(
        ecoCreditToken.connect(user).burn(amount, reason)
      ).to.be.revertedWith("EcoCreditToken: amount must be greater than 0");
    });

    it("Should not burn with empty reason", async function () {
      const BURNER_ROLE = await ecoCreditToken.BURNER_ROLE();
      await ecoCreditToken.grantRole(BURNER_ROLE, user.address);
      
      const amount = ethers.parseEther("100");
      const reason = "";
      
      await expect(
        ecoCreditToken.connect(user).burn(amount, reason)
      ).to.be.revertedWith("EcoCreditToken: reason cannot be empty");
    });

    it("Should not burn more than balance", async function () {
      const BURNER_ROLE = await ecoCreditToken.BURNER_ROLE();
      await ecoCreditToken.grantRole(BURNER_ROLE, user.address);
      
      const amount = ethers.parseEther("2000"); // More than user's balance
      const reason = "Test burn";
      
      await expect(
        ecoCreditToken.connect(user).burn(amount, reason)
      ).to.be.revertedWith("EcoCreditToken: insufficient balance");
    });
  });

  describe("Batch Minting", function () {
    it("Should allow batch minting", async function () {
      const recipients = [user.address, otherUser.address];
      const amounts = [ethers.parseEther("500"), ethers.parseEther("300")];
      const reason = "Batch sustainability rewards";
      
      await ecoCreditToken.connect(minter).batchMint(recipients, amounts, reason);
      
      expect(await ecoCreditToken.balanceOf(user.address)).to.equal(ethers.parseEther("500"));
      expect(await ecoCreditToken.balanceOf(otherUser.address)).to.equal(ethers.parseEther("300"));
    });

    it("Should not batch mint with mismatched arrays", async function () {
      const recipients = [user.address, otherUser.address];
      const amounts = [ethers.parseEther("500")]; // Different length
      const reason = "Batch test";
      
      await expect(
        ecoCreditToken.connect(minter).batchMint(recipients, amounts, reason)
      ).to.be.revertedWith("EcoCreditToken: arrays length mismatch");
    });

    it("Should not batch mint with empty arrays", async function () {
      const recipients: string[] = [];
      const amounts: bigint[] = [];
      const reason = "Batch test";
      
      await expect(
        ecoCreditToken.connect(minter).batchMint(recipients, amounts, reason)
      ).to.be.revertedWith("EcoCreditToken: empty arrays");
    });
  });

  describe("Pausing", function () {
    it("Should allow pauser to pause", async function () {
      await expect(ecoCreditToken.pause())
        .to.emit(ecoCreditToken, "MintingPaused")
        .withArgs(owner.address, await getBlockTimestamp());
    });

    it("Should allow pauser to unpause", async function () {
      await ecoCreditToken.pause();
      await expect(ecoCreditToken.unpause())
        .to.emit(ecoCreditToken, "MintingUnpaused")
        .withArgs(owner.address, await getBlockTimestamp());
    });

    it("Should not allow non-pausers to pause", async function () {
      await expect(
        ecoCreditToken.connect(user).pause()
      ).to.be.revertedWith("AccessControl: account");
    });

    it("Should not mint when paused", async function () {
      await ecoCreditToken.pause();
      
      const amount = ethers.parseEther("1000");
      const reason = "Test mint";
      
      await expect(
        ecoCreditToken.connect(minter).mint(user.address, amount, reason)
      ).to.be.revertedWith("Pausable: paused");
    });
  });

  describe("Token Info", function () {
    it("Should return correct token info", async function () {
      const tokenInfo = await ecoCreditToken.getTokenInfo();
      
      expect(tokenInfo.name).to.equal("EcoCredit");
      expect(tokenInfo.symbol).to.equal("ECO");
      expect(tokenInfo.decimals).to.equal(18);
      expect(tokenInfo.totalSupply).to.equal(await ecoCreditToken.totalSupply());
      expect(tokenInfo.maxSupply).to.equal(ethers.parseEther("1000000000"));
    });
  });

  // Helper function to get block timestamp
  async function getBlockTimestamp(): Promise<number> {
    const block = await ethers.provider.getBlock('latest');
    return block!.timestamp;
  }
});
