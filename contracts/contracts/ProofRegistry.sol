// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title ProofRegistry
 * @dev Central registry for all sustainability proofs and verifications
 * @notice This contract manages the registration and verification of sustainability proofs
 */
contract ProofRegistry is AccessControl, Pausable, ReentrancyGuard {
    using Strings for uint256;

    // Role definitions
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    
    // Counters
    uint256 private _proofCounter;
    uint256 private _verificationCounter;
    
    // Events
    event ProofRegistered(
        uint256 indexed proofId,
        address indexed user,
        string proofType,
        uint256 carbonImpact,
        string metadataURI,
        string ipfsCID,
        uint256 timestamp
    );
    
    event ProofVerified(
        uint256 indexed proofId,
        address indexed verifier,
        bool verified,
        string verificationNotes,
        uint256 timestamp
    );
    
    event ProofUpdated(
        uint256 indexed proofId,
        string newMetadataURI,
        uint256 newCarbonImpact,
        uint256 timestamp
    );
    
    // Struct for proof registration
    struct Proof {
        uint256 proofId;            // Unique proof ID
        address user;               // User who submitted the proof
        string proofType;           // Type of sustainability proof
        uint256 carbonImpact;       // Carbon impact in kg CO2
        string metadataURI;         // IPFS URI for detailed metadata
        string ipfsCID;            // IPFS Content ID
        uint256 timestamp;          // When the proof was registered
        bool verified;              // Whether the proof is verified
        address verifier;           // Address that verified the proof
        string verificationNotes;   // Notes from verification
        uint256 verificationTimestamp; // When verification occurred
        bool exists;                // Whether the proof exists
    }
    
    // Struct for verification record
    struct VerificationRecord {
        uint256 proofId;
        address verifier;
        bool verified;
        string verificationNotes;
        uint256 timestamp;
        bool exists;
    }
    
    // Storage
    mapping(uint256 => Proof) public proofs;
    mapping(uint256 => VerificationRecord) public verificationRecords;
    mapping(address => uint256[]) public userProofs;
    mapping(string => uint256[]) public proofsByType;
    mapping(string => bool) public validProofTypes;
    
    // Arrays for enumeration
    string[] public proofTypes;
    uint256[] public allProofIds;
    
    // Contract addresses for integration
    address public ecoCreditToken;
    address public sustainabilityProofNFT;
    
    /**
     * @dev Constructor
     * @param initialOwner The address that will receive admin roles
     */
    constructor(address initialOwner) {
        require(initialOwner != address(0), "ProofRegistry: initial owner cannot be zero address");
        
        // Grant roles
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(REGISTRAR_ROLE, initialOwner);
        _grantRole(VERIFIER_ROLE, initialOwner);
        _grantRole(PAUSER_ROLE, initialOwner);
        
        // Initialize valid proof types
        _addProofType("carbon_footprint");
        _addProofType("renewable_energy");
        _addProofType("waste_reduction");
        _addProofType("sustainable_transport");
        _addProofType("energy_efficiency");
        _addProofType("water_conservation");
        _addProofType("sustainable_agriculture");
        _addProofType("forest_conservation");
    }
    
    /**
     * @dev Register a new sustainability proof
     * @param user The user submitting the proof
     * @param proofType The type of sustainability proof
     * @param carbonImpact The carbon impact in kg CO2
     * @param metadataURI The IPFS URI for detailed metadata
     * @param ipfsCID The IPFS Content ID
     */
    function registerProof(
        address user,
        string memory proofType,
        uint256 carbonImpact,
        string memory metadataURI,
        string memory ipfsCID
    ) 
        external 
        onlyRole(REGISTRAR_ROLE) 
        whenNotPaused 
        nonReentrant
        returns (uint256)
    {
        require(user != address(0), "ProofRegistry: user cannot be zero address");
        require(bytes(proofType).length > 0, "ProofRegistry: proof type cannot be empty");
        require(validProofTypes[proofType], "ProofRegistry: invalid proof type");
        require(carbonImpact > 0, "ProofRegistry: carbon impact must be greater than 0");
        require(bytes(metadataURI).length > 0, "ProofRegistry: metadata URI cannot be empty");
        require(bytes(ipfsCID).length > 0, "ProofRegistry: IPFS CID cannot be empty");
        
        // Increment proof counter
        _proofCounter++;
        uint256 proofId = _proofCounter;
        
        // Create proof record
        proofs[proofId] = Proof({
            proofId: proofId,
            user: user,
            proofType: proofType,
            carbonImpact: carbonImpact,
            metadataURI: metadataURI,
            ipfsCID: ipfsCID,
            timestamp: block.timestamp,
            verified: false,
            verifier: address(0),
            verificationNotes: "",
            verificationTimestamp: 0,
            exists: true
        });
        
        // Update mappings
        userProofs[user].push(proofId);
        proofsByType[proofType].push(proofId);
        allProofIds.push(proofId);
        
        emit ProofRegistered(
            proofId,
            user,
            proofType,
            carbonImpact,
            metadataURI,
            ipfsCID,
            block.timestamp
        );
        
        return proofId;
    }
    
    /**
     * @dev Verify a sustainability proof
     * @param proofId The proof ID to verify
     * @param verified Whether the proof is verified
     * @param verificationNotes Notes from verification
     */
    function verifyProof(
        uint256 proofId,
        bool verified,
        string memory verificationNotes
    ) 
        external 
        onlyRole(VERIFIER_ROLE) 
        whenNotPaused 
        nonReentrant
    {
        require(proofs[proofId].exists, "ProofRegistry: proof does not exist");
        require(!proofs[proofId].verified, "ProofRegistry: proof already verified");
        
        // Update proof verification status
        proofs[proofId].verified = verified;
        proofs[proofId].verifier = msg.sender;
        proofs[proofId].verificationNotes = verificationNotes;
        proofs[proofId].verificationTimestamp = block.timestamp;
        
        // Create verification record
        _verificationCounter++;
        uint256 verificationId = _verificationCounter;
        
        verificationRecords[verificationId] = VerificationRecord({
            proofId: proofId,
            verifier: msg.sender,
            verified: verified,
            verificationNotes: verificationNotes,
            timestamp: block.timestamp,
            exists: true
        });
        
        emit ProofVerified(proofId, msg.sender, verified, verificationNotes, block.timestamp);
    }
    
    /**
     * @dev Update proof metadata
     * @param proofId The proof ID
     * @param newMetadataURI The new metadata URI
     * @param newCarbonImpact The new carbon impact
     */
    function updateProof(
        uint256 proofId,
        string memory newMetadataURI,
        uint256 newCarbonImpact
    ) 
        external 
        onlyRole(REGISTRAR_ROLE) 
        whenNotPaused 
        nonReentrant
    {
        require(proofs[proofId].exists, "ProofRegistry: proof does not exist");
        require(!proofs[proofId].verified, "ProofRegistry: cannot update verified proof");
        require(bytes(newMetadataURI).length > 0, "ProofRegistry: metadata URI cannot be empty");
        require(newCarbonImpact > 0, "ProofRegistry: carbon impact must be greater than 0");
        
        proofs[proofId].metadataURI = newMetadataURI;
        proofs[proofId].carbonImpact = newCarbonImpact;
        
        emit ProofUpdated(proofId, newMetadataURI, newCarbonImpact, block.timestamp);
    }
    
    /**
     * @dev Add a new valid proof type
     * @param proofType The new proof type
     */
    function addProofType(string memory proofType) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(bytes(proofType).length > 0, "ProofRegistry: proof type cannot be empty");
        require(!validProofTypes[proofType], "ProofRegistry: proof type already exists");
        
        _addProofType(proofType);
    }
    
    /**
     * @dev Internal function to add proof type
     * @param proofType The proof type to add
     */
    function _addProofType(string memory proofType) internal {
        validProofTypes[proofType] = true;
        proofTypes.push(proofType);
    }
    
    /**
     * @dev Set contract addresses for integration
     * @param _ecoCreditToken The EcoCreditToken contract address
     * @param _sustainabilityProofNFT The SustainabilityProof NFT contract address
     */
    function setContractAddresses(
        address _ecoCreditToken,
        address _sustainabilityProofNFT
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_ecoCreditToken != address(0), "ProofRegistry: EcoCredit token address cannot be zero");
        require(_sustainabilityProofNFT != address(0), "ProofRegistry: NFT address cannot be zero");
        
        ecoCreditToken = _ecoCreditToken;
        sustainabilityProofNFT = _sustainabilityProofNFT;
    }
    
    /**
     * @dev Pause the contract
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause the contract
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Get proof information
     * @param proofId The proof ID
     * @return The proof information
     */
    function getProof(uint256 proofId) external view returns (Proof memory) {
        require(proofs[proofId].exists, "ProofRegistry: proof does not exist");
        return proofs[proofId];
    }
    
    /**
     * @dev Get all proofs for a user
     * @param user The user address
     * @return Array of proof IDs
     */
    function getUserProofs(address user) external view returns (uint256[] memory) {
        return userProofs[user];
    }
    
    /**
     * @dev Get proofs by type
     * @param proofType The proof type
     * @return Array of proof IDs
     */
    function getProofsByType(string memory proofType) external view returns (uint256[] memory) {
        return proofsByType[proofType];
    }
    
    /**
     * @dev Get all proof IDs
     * @return Array of all proof IDs
     */
    function getAllProofIds() external view returns (uint256[] memory) {
        return allProofIds;
    }
    
    /**
     * @dev Get total carbon impact for a user
     * @param user The user address
     * @return Total carbon impact in kg CO2
     */
    function getUserTotalCarbonImpact(address user) external view returns (uint256) {
        uint256[] memory userProofIds = userProofs[user];
        uint256 totalImpact = 0;
        
        for (uint256 i = 0; i < userProofIds.length; i++) {
            if (proofs[userProofIds[i]].verified) {
                totalImpact += proofs[userProofIds[i]].carbonImpact;
            }
        }
        
        return totalImpact;
    }
    
    /**
     * @dev Get total carbon impact by proof type
     * @param proofType The proof type
     * @return Total carbon impact in kg CO2
     */
    function getTotalCarbonImpactByType(string memory proofType) external view returns (uint256) {
        uint256[] memory proofIds = proofsByType[proofType];
        uint256 totalImpact = 0;
        
        for (uint256 i = 0; i < proofIds.length; i++) {
            if (proofs[proofIds[i]].verified) {
                totalImpact += proofs[proofIds[i]].carbonImpact;
            }
        }
        
        return totalImpact;
    }
    
    /**
     * @dev Get verification record
     * @param verificationId The verification ID
     * @return The verification record
     */
    function getVerificationRecord(uint256 verificationId) external view returns (VerificationRecord memory) {
        require(verificationRecords[verificationId].exists, "ProofRegistry: verification record does not exist");
        return verificationRecords[verificationId];
    }
    
    /**
     * @dev Get all valid proof types
     * @return Array of valid proof types
     */
    function getValidProofTypes() external view returns (string[] memory) {
        return proofTypes;
    }
    
    /**
     * @dev Get total number of proofs
     * @return The total number of proofs
     */
    function getTotalProofs() external view returns (uint256) {
        return _proofCounter;
    }
    
    /**
     * @dev Get total number of verifications
     * @return The total number of verifications
     */
    function getTotalVerifications() external view returns (uint256) {
        return _verificationCounter;
    }
    
    /**
     * @dev Check if a proof type is valid
     * @param proofType The proof type to check
     * @return Whether the proof type is valid
     */
    function isValidProofType(string memory proofType) external view returns (bool) {
        return validProofTypes[proofType];
    }
    
    /**
     * @dev Get contract information
     * @return _ecoCreditToken The EcoCreditToken contract address
     * @return _sustainabilityProofNFT The SustainabilityProof NFT contract address
     * @return totalProofs The total number of proofs
     * @return totalVerifications The total number of verifications
     */
    function getContractInfo() external view returns (
        address _ecoCreditToken,
        address _sustainabilityProofNFT,
        uint256 totalProofs,
        uint256 totalVerifications
    ) {
        return (
            ecoCreditToken,
            sustainabilityProofNFT,
            _proofCounter,
            _verificationCounter
        );
    }
}
