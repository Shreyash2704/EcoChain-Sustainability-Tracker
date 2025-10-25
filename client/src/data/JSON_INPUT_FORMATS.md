# EcoChain JSON Input Formats

This document explains the JSON input formats for EcoChain sustainability document analysis.

## ⚠️ Important Notice

**File Reading Functionality**: The file reading functionality is not yet implemented in the current version. Please use the sample JSON documents provided in the application to test the system. This feature will be added in the next development phase.

## 📋 Overview

EcoChain accepts JSON documents containing sustainability metrics and analyzes them using MeTTa reasoning to calculate:
- **Impact Score** (0-100)
- **ECO Token Rewards** (based on impact)
- **NFT Minting** (for verified documents)
- **Blockchain Transactions** (token and NFT minting)

## 🏗️ Basic Document Structure

```json
{
  "name": "Document Name",
  "description": "Brief description",
  "organization": "Organization Name",
  "reporting_period": "2024",
  "document_type": "sustainability_document",
  "sustainability_metrics": {
    "carbon_footprint": 150.5,
    "energy_consumption": 2500,
    "waste_reduction": 15.2,
    "renewable_energy_percentage": 85.0
  }
}
```

## 📊 Document Types

### 1. Sustainability Document
```json
{
  "name": "Corporate Sustainability Report",
  "description": "Annual sustainability report with comprehensive environmental metrics",
  "sustainability_metrics": {
    "carbon_footprint": 150.5,
    "energy_consumption": 2500,
    "waste_reduction": 15.2,
    "renewable_energy_percentage": 85.0,
    "water_usage": 1200,
    "recycling_rate": 78.5
  },
  "document_type": "sustainability_document",
  "organization": "EcoCorp Inc.",
  "reporting_period": "2024",
  "certifications": ["ISO 14001", "LEED Gold"],
  "goals_achieved": [
    "25% reduction in carbon emissions",
    "40% increase in renewable energy usage",
    "Zero waste to landfill"
  ]
}
```

### 2. Carbon Report
```json
{
  "name": "Carbon Footprint Assessment",
  "description": "Detailed carbon footprint analysis for manufacturing operations",
  "sustainability_metrics": {
    "carbon_footprint": 320.8,
    "energy_consumption": 4500,
    "waste_reduction": 22.1,
    "renewable_energy_percentage": 92.0,
    "scope_1_emissions": 180.2,
    "scope_2_emissions": 140.6,
    "scope_3_emissions": 85.4
  },
  "document_type": "carbon_report",
  "organization": "Green Manufacturing Ltd.",
  "reporting_period": "Q4 2024",
  "methodology": "GHG Protocol",
  "verification": "Third-party verified"
}
```

### 3. Energy Audit
```json
{
  "name": "Energy Efficiency Audit",
  "description": "Comprehensive energy audit with efficiency recommendations",
  "sustainability_metrics": {
    "carbon_footprint": 95.3,
    "energy_consumption": 1800,
    "waste_reduction": 8.7,
    "renewable_energy_percentage": 65.0,
    "energy_savings": 25.5,
    "efficiency_improvements": 18.2
  },
  "document_type": "energy_audit",
  "organization": "Energy Solutions Co.",
  "reporting_period": "2024",
  "audit_scope": "Building energy systems",
  "recommendations": [
    "LED lighting upgrade",
    "HVAC optimization",
    "Smart metering implementation"
  ]
}
```

### 4. Waste Management
```json
{
  "name": "Waste Management Report",
  "description": "Comprehensive waste reduction and recycling program results",
  "sustainability_metrics": {
    "carbon_footprint": 45.2,
    "energy_consumption": 800,
    "waste_reduction": 35.8,
    "renewable_energy_percentage": 45.0,
    "waste_diverted": 85.2,
    "recycling_rate": 92.5
  },
  "document_type": "waste_management",
  "organization": "Waste Solutions Inc.",
  "reporting_period": "2024",
  "programs": [
    "Composting initiative",
    "Electronic waste recycling",
    "Paper reduction program"
  ]
}
```

### 5. Green Certification
```json
{
  "name": "Green Building Certification",
  "description": "LEED Platinum certification for sustainable building design",
  "sustainability_metrics": {
    "carbon_footprint": 25.1,
    "energy_consumption": 1200,
    "waste_reduction": 45.3,
    "renewable_energy_percentage": 100.0,
    "water_efficiency": 95.0,
    "indoor_air_quality": 98.5
  },
  "document_type": "green_certification",
  "organization": "Sustainable Architecture Group",
  "reporting_period": "2024",
  "certification": "LEED Platinum",
  "score": 95,
  "features": [
    "Solar panel installation",
    "Rainwater harvesting",
    "Green roof system",
    "Energy-efficient HVAC"
  ]
}
```

## 🎯 Required Fields

### Core Fields (Required)
- `name`: Document name
- `document_type`: One of the supported types
- `sustainability_metrics`: Object containing metrics

### Sustainability Metrics (Required)
- `carbon_footprint`: Carbon footprint in kg CO2
- `energy_consumption`: Energy consumption in kWh
- `waste_reduction`: Waste reduction percentage
- `renewable_energy_percentage`: Renewable energy percentage

## 🔧 Optional Fields

### Additional Metrics
- `water_usage`: Water usage in liters
- `recycling_rate`: Recycling rate percentage
- `scope_1_emissions`: Scope 1 emissions
- `scope_2_emissions`: Scope 2 emissions
- `scope_3_emissions`: Scope 3 emissions
- `energy_savings`: Energy savings percentage
- `efficiency_improvements`: Efficiency improvements percentage
- `waste_diverted`: Waste diverted percentage
- `water_efficiency`: Water efficiency percentage
- `indoor_air_quality`: Indoor air quality score

### Metadata
- `description`: Document description
- `organization`: Organization name
- `reporting_period`: Reporting period
- `certifications`: Array of certifications
- `goals_achieved`: Array of achieved goals
- `methodology`: Analysis methodology
- `verification`: Verification status
- `audit_scope`: Audit scope
- `recommendations`: Array of recommendations
- `programs`: Array of programs
- `certification`: Certification type
- `score`: Certification score
- `features`: Array of features

## 🧠 MeTTa Analysis Process

### 1. Document Classification
MeTTa analyzes the document type and applies appropriate multipliers:
- `sustainability_document`: 1.0x
- `carbon_report`: 1.2x
- `energy_audit`: 1.1x
- `waste_management`: 1.0x
- `green_certification`: 1.5x

### 2. Impact Score Calculation
```metta
(= (impact-score $carbon $waste $renewable $doc-type)
   (let* 
       ($base-score (+ (carbon-credit $carbon) (waste-bonus $waste) (renewable-bonus $renewable)))
       (* $base-score (document-multiplier $doc-type))))
```

### 3. Token Calculation
```metta
(= (token-amount $impact-score)
   (if (> $impact-score 80)
       100
       (if (> $impact-score 60)
           75
           (if (> $impact-score 40)
               50
               (if (> $impact-score 20)
                   25
                   0)))))
```

### 4. Minting Decision
```metta
(= (should-mint $impact-score)
   (> $impact-score 10))
```

## 🚀 Getting Started

### 1. Download Sample Documents
Use the sample documents provided in the Upload page to understand the format.

### 2. Create Custom Template
Use the JSON Template Generator to create your own documents.

### 3. Upload and Analyze
Upload your JSON document to get:
- Impact score analysis
- ECO token rewards
- NFT minting (if eligible)
- Blockchain transactions

## 📝 Best Practices

1. **Use Realistic Values**: Ensure your metrics are realistic and verifiable
2. **Include Context**: Add descriptions and organizational information
3. **Verify Data**: Use third-party verification when possible
4. **Regular Updates**: Submit updated reports regularly
5. **Document Types**: Choose the appropriate document type for your use case

## 🔍 Example Analysis Results

```json
{
  "upload_id": "uuid-here",
  "status": "completed",
  "impact_score": 85.5,
  "should_mint": true,
  "token_amount": 100,
  "reasoning": "Excellent sustainability performance with high renewable energy adoption and significant waste reduction achievements.",
  "blockchain_transactions": {
    "eco_token_minting": {
      "tx_hash": "0x...",
      "amount": 100
    },
    "nft_minting": {
      "tx_hash": "0x...",
      "token_id": 42
    }
  }
}
```

## 🆘 Troubleshooting

### Common Issues
1. **Invalid JSON**: Ensure proper JSON formatting
2. **Missing Fields**: Include all required fields
3. **Invalid Values**: Use appropriate data types
4. **Document Type**: Choose from supported types

### Validation
- JSON must be valid
- Required fields must be present
- Numeric values must be numbers
- Arrays must be properly formatted

## 📞 Support

For questions about JSON input formats, contact the EcoChain support team or check the documentation.
