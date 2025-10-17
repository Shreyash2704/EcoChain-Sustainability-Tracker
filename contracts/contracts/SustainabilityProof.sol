// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title SustainabilityProof
 * @dev ERC-721 NFT contract for sustainability proofs and carbon credits
 * @notice This contract manages NFTs that represent verified sustainability actions
 */
contract SustainabilityProof is 
    ERC721, 
    ERC721URIStorage, 
    ERC721Enumerable, 
    AccessControl, 
    Pausable, 
    ReentrancyGuard 
{
    using Strings for uint256;

    // Role definitions
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant METADATA_ROLE = keccak256("METADATA_ROLE");
    
    // Token counter
    uint256 private _tokenIdCounter;
    
    // Base URI for token metadata
    string private _baseTokenURI;
    
    // Events
    event SustainabilityProofMinted(
        uint256 indexed tokenId,
        address indexed to,
        string proofType,
        uint256 carbonImpact,
        string metadataURI,
        uint256 timestamp
    );
    
    event ProofMetadataUpdated(
        uint256 indexed tokenId,
        string newMetadataURI,
        uint256 timestamp
    );
    
    event BaseURIUpdated(string newBaseURI, uint256 timestamp);
    
    // Struct for proof information
    struct ProofInfo {
        string proofType;           // Type of sustainability proof
        uint256 carbonImpact;       // Carbon impact in kg CO2
        string metadataURI;         // IPFS URI for detailed metadata
        uint256 timestamp;          // When the proof was created
        bool verified;              // Whether the proof is verified
        address verifier;           // Address that verified the proof
    }
    
    // Storage for proof information
    mapping(uint256 => ProofInfo) public proofInfo;
    
    // Mapping for proof types
    mapping(string => uint256) public proofTypeCount;
    
    // Array of all proof types
    string[] public proofTypes;
    
    /**
     * @dev Constructor
     * @param name The name of the NFT collection
     * @param symbol The symbol of the NFT collection
     * @param baseTokenURI The base URI for token metadata
     * @param initialOwner The address that will receive admin roles
     */
    constructor(
        string memory name,
        string memory symbol,
        string memory baseTokenURI,
        address initialOwner
    ) ERC721(name, symbol) {
        require(initialOwner != address(0), "SustainabilityProof: initial owner cannot be zero address");
        
        _baseTokenURI = baseTokenURI;
        
        // Grant roles
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(MINTER_ROLE, initialOwner);
        _grantRole(PAUSER_ROLE, initialOwner);
        _grantRole(METADATA_ROLE, initialOwner);
    }
    
    /**
     * @dev Mint a new sustainability proof NFT
     * @param to The address to mint the NFT to
     * @param proofType The type of sustainability proof
     * @param carbonImpact The carbon impact in kg CO2
     * @param metadataURI The IPFS URI for detailed metadata
     */
    function mintSustainabilityProof(
        address to,
        string memory proofType,
        uint256 carbonImpact,
        string memory metadataURI
    ) 
        external 
        onlyRole(MINTER_ROLE) 
        whenNotPaused 
        nonReentrant
        returns (uint256)
    {
        require(to != address(0), "SustainabilityProof: mint to zero address");
        require(bytes(proofType).length > 0, "SustainabilityProof: proof type cannot be empty");
        require(carbonImpact > 0, "SustainabilityProof: carbon impact must be greater than 0");
        require(bytes(metadataURI).length > 0, "SustainabilityProof: metadata URI cannot be empty");
        
        // Increment token counter
        _tokenIdCounter++;
        uint256 tokenId = _tokenIdCounter;
        
        // Store proof information
        proofInfo[tokenId] = ProofInfo({
            proofType: proofType,
            carbonImpact: carbonImpact,
            metadataURI: metadataURI,
            timestamp: block.timestamp,
            verified: true, // Assume verified if minted by authorized minter
            verifier: msg.sender
        });
        
        // Update proof type count
        if (proofTypeCount[proofType] == 0) {
            proofTypes.push(proofType);
        }
        proofTypeCount[proofType]++;
        
        // Mint the NFT
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        
        emit SustainabilityProofMinted(
            tokenId,
            to,
            proofType,
            carbonImpact,
            metadataURI,
            block.timestamp
        );
        
        return tokenId;
    }
    
    /**
     * @dev Batch mint multiple sustainability proof NFTs
     * @param recipients Array of recipient addresses
     * @param _proofTypes Array of proof types
     * @param carbonImpacts Array of carbon impacts
     * @param metadataURIs Array of metadata URIs
     */
    function batchMintSustainabilityProofs(
        address[] memory recipients,
        string[] memory _proofTypes,
        uint256[] memory carbonImpacts,
        string[] memory metadataURIs
    ) 
        external 
        onlyRole(MINTER_ROLE) 
        whenNotPaused 
        nonReentrant
    {
        require(
            recipients.length == _proofTypes.length &&
            _proofTypes.length == carbonImpacts.length &&
            carbonImpacts.length == metadataURIs.length,
            "SustainabilityProof: arrays length mismatch"
        );
        require(recipients.length > 0, "SustainabilityProof: empty arrays");
        
        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "SustainabilityProof: mint to zero address");
            require(bytes(_proofTypes[i]).length > 0, "SustainabilityProof: proof type cannot be empty");
            require(carbonImpacts[i] > 0, "SustainabilityProof: carbon impact must be greater than 0");
            require(bytes(metadataURIs[i]).length > 0, "SustainabilityProof: metadata URI cannot be empty");
            
            // Increment token counter
            _tokenIdCounter++;
            uint256 tokenId = _tokenIdCounter;
            
            // Store proof information
            proofInfo[tokenId] = ProofInfo({
                proofType: _proofTypes[i],
                carbonImpact: carbonImpacts[i],
                metadataURI: metadataURIs[i],
                timestamp: block.timestamp,
                verified: true,
                verifier: msg.sender
            });
            
            // Update proof type count
            if (proofTypeCount[_proofTypes[i]] == 0) {
                proofTypes.push(_proofTypes[i]);
            }
            proofTypeCount[_proofTypes[i]]++;
            
            // Mint the NFT
            _safeMint(recipients[i], tokenId);
            _setTokenURI(tokenId, metadataURIs[i]);
            
            emit SustainabilityProofMinted(
                tokenId,
                recipients[i],
                _proofTypes[i],
                carbonImpacts[i],
                metadataURIs[i],
                block.timestamp
            );
        }
    }
    
    /**
     * @dev Update metadata URI for a token
     * @param tokenId The token ID
     * @param newMetadataURI The new metadata URI
     */
    function updateTokenMetadata(
        uint256 tokenId,
        string memory newMetadataURI
    ) 
        external 
        onlyRole(METADATA_ROLE) 
        whenNotPaused
    {
        require(ownerOf(tokenId) != address(0), "SustainabilityProof: token does not exist");
        require(bytes(newMetadataURI).length > 0, "SustainabilityProof: metadata URI cannot be empty");
        
        proofInfo[tokenId].metadataURI = newMetadataURI;
        _setTokenURI(tokenId, newMetadataURI);
        
        emit ProofMetadataUpdated(tokenId, newMetadataURI, block.timestamp);
    }
    
    /**
     * @dev Set the base URI for token metadata
     * @param newBaseURI The new base URI
     */
    function setBaseURI(string memory newBaseURI) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _baseTokenURI = newBaseURI;
        emit BaseURIUpdated(newBaseURI, block.timestamp);
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
     * @dev Get proof information for a token
     * @param tokenId The token ID
     * @return The proof information
     */
    function getProofInfo(uint256 tokenId) external view returns (ProofInfo memory) {
        require(ownerOf(tokenId) != address(0), "SustainabilityProof: token does not exist");
        return proofInfo[tokenId];
    }
    
    /**
     * @dev Get all tokens owned by an address
     * @param owner The owner address
     * @return Array of token IDs
     */
    function getTokensByOwner(address owner) external view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(owner);
        uint256[] memory tokens = new uint256[](tokenCount);
        
        for (uint256 i = 0; i < tokenCount; i++) {
            tokens[i] = tokenOfOwnerByIndex(owner, i);
        }
        
        return tokens;
    }
    
    /**
     * @dev Get tokens by proof type
     * @param proofType The proof type
     * @param owner The owner address (optional, use address(0) for all)
     * @return Array of token IDs
     */
    function getTokensByProofType(
        string memory proofType,
        address owner
    ) external view returns (uint256[] memory) {
        uint256 totalSupply = totalSupply();
        uint256[] memory tempTokens = new uint256[](totalSupply);
        uint256 count = 0;
        
        for (uint256 i = 1; i <= totalSupply; i++) {
            if (
                keccak256(bytes(proofInfo[i].proofType)) == keccak256(bytes(proofType)) &&
                (owner == address(0) || ownerOf(i) == owner)
            ) {
                tempTokens[count] = i;
                count++;
            }
        }
        
        uint256[] memory tokens = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            tokens[i] = tempTokens[i];
        }
        
        return tokens;
    }
    
    /**
     * @dev Get total carbon impact for an address
     * @param owner The owner address
     * @return Total carbon impact in kg CO2
     */
    function getTotalCarbonImpact(address owner) external view returns (uint256) {
        uint256 tokenCount = balanceOf(owner);
        uint256 totalImpact = 0;
        
        for (uint256 i = 0; i < tokenCount; i++) {
            uint256 tokenId = tokenOfOwnerByIndex(owner, i);
            totalImpact += proofInfo[tokenId].carbonImpact;
        }
        
        return totalImpact;
    }
    
    /**
     * @dev Get all proof types
     * @return Array of proof types
     */
    function getAllProofTypes() external view returns (string[] memory) {
        return proofTypes;
    }
    
    /**
     * @dev Get proof type count
     * @param proofType The proof type
     * @return The count of tokens with this proof type
     */
    function getProofTypeCount(string memory proofType) external view returns (uint256) {
        return proofTypeCount[proofType];
    }
    
    /**
     * @dev Override tokenURI to use base URI
     * @param tokenId The token ID
     * @return The token URI
     */
    function tokenURI(uint256 tokenId) 
        public 
        view 
        override(ERC721, ERC721URIStorage) 
        returns (string memory) 
    {
        require(ownerOf(tokenId) != address(0), "SustainabilityProof: token does not exist");
        
        string memory baseURI = _baseURI();
        string memory metadataURI = proofInfo[tokenId].metadataURI;
        
        if (bytes(metadataURI).length > 0) {
            return metadataURI;
        }
        
        return bytes(baseURI).length > 0 
            ? string(abi.encodePacked(baseURI, tokenId.toString()))
            : "";
    }
    
    /**
     * @dev Get the base URI
     * @return The base URI
     */
    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }
    
    /**
     * @dev Override _beforeTokenTransfer to include pausable functionality
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal override(ERC721, ERC721Enumerable) whenNotPaused returns (address) {
        return super._update(to, tokenId, auth);
    }
    
    /**
     * @dev Override supportsInterface to include all interfaces
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
    
    function _increaseBalance(address account, uint128 amount) internal override(ERC721, ERC721Enumerable) {
        super._increaseBalance(account, amount);
    }
}
