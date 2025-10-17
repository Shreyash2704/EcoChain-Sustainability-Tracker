// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title EcoCreditToken
 * @dev ERC-20 token for carbon credits and sustainability rewards
 * @notice This contract manages the minting and burning of EcoCredit tokens
 *         based on verified sustainability actions
 */
contract EcoCreditToken is ERC20, AccessControl, Pausable, ReentrancyGuard {

    // Role definitions
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    
    // Token configuration
    uint256 public constant MAX_SUPPLY = 1000000000 * 10**18; // 1 billion tokens
    uint256 public constant INITIAL_SUPPLY = 10000000 * 10**18; // 10 million initial supply
    
    // Tracking
    uint256 private _mintCounter;
    uint256 private _burnCounter;
    
    // Events
    event TokensMinted(
        address indexed to, 
        uint256 amount, 
        string reason,
        uint256 mintId,
        uint256 timestamp
    );
    
    event TokensBurned(
        address indexed from, 
        uint256 amount, 
        string reason,
        uint256 burnId,
        uint256 timestamp
    );
    
    event MintingPaused(address indexed account, uint256 timestamp);
    event MintingUnpaused(address indexed account, uint256 timestamp);
    
    // Struct for minting records
    struct MintRecord {
        address to;
        uint256 amount;
        string reason;
        uint256 timestamp;
        bool exists;
    }
    
    struct BurnRecord {
        address from;
        uint256 amount;
        string reason;
        uint256 timestamp;
        bool exists;
    }
    
    // Storage for records
    mapping(uint256 => MintRecord) public mintRecords;
    mapping(uint256 => BurnRecord) public burnRecords;
    
    /**
     * @dev Constructor that initializes the token
     * @param initialOwner The address that will receive admin roles
     */
    constructor(address initialOwner) ERC20("EcoCredit", "ECO") {
        require(initialOwner != address(0), "EcoCreditToken: initial owner cannot be zero address");
        
        // Grant roles
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(MINTER_ROLE, initialOwner);
        _grantRole(BURNER_ROLE, initialOwner);
        _grantRole(PAUSER_ROLE, initialOwner);
        
        // Mint initial supply to the owner
        _mint(initialOwner, INITIAL_SUPPLY);
        
        emit TokensMinted(initialOwner, INITIAL_SUPPLY, "Initial supply", 0, block.timestamp);
    }
    
    /**
     * @dev Mint tokens to a specified address
     * @param to The address to mint tokens to
     * @param amount The amount of tokens to mint
     * @param reason The reason for minting (e.g., "Carbon offset", "Sustainability reward")
     */
    function mint(
        address to, 
        uint256 amount, 
        string memory reason
    ) 
        external 
        onlyRole(MINTER_ROLE) 
        whenNotPaused 
        nonReentrant
        returns (uint256 mintId)
    {
        require(to != address(0), "EcoCreditToken: mint to zero address");
        require(amount > 0, "EcoCreditToken: amount must be greater than 0");
        require(bytes(reason).length > 0, "EcoCreditToken: reason cannot be empty");
        require(totalSupply() + amount <= MAX_SUPPLY, "EcoCreditToken: exceeds max supply");
        
        // Increment mint counter and get mint ID
        _mintCounter++;
        mintId = _mintCounter;
        
        // Record the mint
        mintRecords[mintId] = MintRecord({
            to: to,
            amount: amount,
            reason: reason,
            timestamp: block.timestamp,
            exists: true
        });
        
        // Mint the tokens
        _mint(to, amount);
        
        emit TokensMinted(to, amount, reason, mintId, block.timestamp);
        
        return mintId;
    }
    
    /**
     * @dev Burn tokens from the caller's balance
     * @param amount The amount of tokens to burn
     * @param reason The reason for burning (e.g., "Carbon offset purchase", "Token retirement")
     */
    function burn(
        uint256 amount, 
        string memory reason
    ) 
        external 
        onlyRole(BURNER_ROLE) 
        whenNotPaused 
        nonReentrant
        returns (uint256 burnId)
    {
        require(amount > 0, "EcoCreditToken: amount must be greater than 0");
        require(bytes(reason).length > 0, "EcoCreditToken: reason cannot be empty");
        require(balanceOf(msg.sender) >= amount, "EcoCreditToken: insufficient balance");
        
        // Increment burn counter and get burn ID
        _burnCounter++;
        burnId = _burnCounter;
        
        // Record the burn
        burnRecords[burnId] = BurnRecord({
            from: msg.sender,
            amount: amount,
            reason: reason,
            timestamp: block.timestamp,
            exists: true
        });
        
        // Burn the tokens
        _burn(msg.sender, amount);
        
        emit TokensBurned(msg.sender, amount, reason, burnId, block.timestamp);
        
        return burnId;
    }
    
    /**
     * @dev Batch mint tokens to multiple addresses
     * @param recipients Array of recipient addresses
     * @param amounts Array of amounts to mint
     * @param reason The reason for minting
     */
    function batchMint(
        address[] memory recipients,
        uint256[] memory amounts,
        string memory reason
    ) 
        external 
        onlyRole(MINTER_ROLE) 
        whenNotPaused 
        nonReentrant
    {
        require(recipients.length == amounts.length, "EcoCreditToken: arrays length mismatch");
        require(recipients.length > 0, "EcoCreditToken: empty arrays");
        require(bytes(reason).length > 0, "EcoCreditToken: reason cannot be empty");
        
        uint256 totalAmount = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            totalAmount += amounts[i];
        }
        
        require(totalSupply() + totalAmount <= MAX_SUPPLY, "EcoCreditToken: exceeds max supply");
        
        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "EcoCreditToken: mint to zero address");
            require(amounts[i] > 0, "EcoCreditToken: amount must be greater than 0");
            
            _mint(recipients[i], amounts[i]);
        }
        
        emit TokensMinted(address(0), totalAmount, reason, 0, block.timestamp);
    }
    
    /**
     * @dev Pause minting functionality
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
        emit MintingPaused(msg.sender, block.timestamp);
    }
    
    /**
     * @dev Unpause minting functionality
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
        emit MintingUnpaused(msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get the total number of mints performed
     * @return The total number of mints
     */
    function getTotalMints() external view returns (uint256) {
        return _mintCounter;
    }
    
    /**
     * @dev Get the total number of burns performed
     * @return The total number of burns
     */
    function getTotalBurns() external view returns (uint256) {
        return _burnCounter;
    }
    
    /**
     * @dev Get mint record by ID
     * @param mintId The mint ID
     * @return The mint record
     */
    function getMintRecord(uint256 mintId) external view returns (MintRecord memory) {
        require(mintRecords[mintId].exists, "EcoCreditToken: mint record does not exist");
        return mintRecords[mintId];
    }
    
    /**
     * @dev Get burn record by ID
     * @param burnId The burn ID
     * @return The burn record
     */
    function getBurnRecord(uint256 burnId) external view returns (BurnRecord memory) {
        require(burnRecords[burnId].exists, "EcoCreditToken: burn record does not exist");
        return burnRecords[burnId];
    }
    
    /**
     * @dev Override transfer to include pausable functionality
     */
    function _update(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._update(from, to, amount);
    }
    
    /**
     * @dev Get token information
     * @return name The token name
     * @return symbol The token symbol
     * @return decimals The token decimals
     * @return totalSupply The total supply
     * @return maxSupply The maximum supply
     */
    function getTokenInfo() external view returns (
        string memory name,
        string memory symbol,
        uint8 decimals,
        uint256 totalSupply,
        uint256 maxSupply
    ) {
        return (
            "EcoCredit",
            "ECO",
            18,
            totalSupply,
            MAX_SUPPLY
        );
    }
}
