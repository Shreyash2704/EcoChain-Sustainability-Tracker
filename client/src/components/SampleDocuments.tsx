import React from "react";
import { Download, FileText, Leaf, Zap, Recycle, Award } from "lucide-react";

interface SampleDocument {
  name: string;
  description: string;
  icon: React.ReactNode;
  filename: string;
  data: any;
}

const sampleDocuments: SampleDocument[] = [
  {
    name: "Sustainability Report",
    description: "Corporate sustainability report with comprehensive metrics",
    icon: <FileText className="w-5 h-5" />,
    filename: "sustainability-report.json",
    data: {
      document_type: "sustainability_document",
      title: "Corporate Sustainability Report 2024",
      organization: "EcoTech Solutions",
      reporting_period: "2024",
      sustainability_metrics: {
        carbon_footprint: 150.5,
        energy_consumption: 2500,
        waste_reduction: 15.2,
        renewable_energy_percentage: 85.0,
        waste_reduction_percentage: 25.0,
        water_consumption: 1200,
        recycling_rate: 78.5,
        green_energy_usage: 90.0,
      },
      initiatives: [
        "Solar panel installation",
        "Waste reduction program",
        "Employee carpooling",
        "LED lighting upgrade",
      ],
      certifications: ["ISO 14001", "LEED Gold", "B-Corp Certified"],
      goals: {
        carbon_neutral_by: "2025",
        zero_waste_by: "2026",
        renewable_energy_target: 100,
      },
      impact_measurements: {
        co2_reduced: 45.2,
        energy_saved_kwh: 1500,
        waste_diverted_tons: 12.5,
        water_saved_liters: 8000,
      },
    },
  },
  {
    name: "Carbon Footprint Report",
    description: "Detailed carbon footprint analysis for operations",
    icon: <Leaf className="w-5 h-5" />,
    filename: "carbon-footprint.json",
    data: {
      document_type: "carbon_report",
      title: "Carbon Footprint Assessment",
      organization: "Green Manufacturing Co.",
      assessment_date: "2024-01-15",
      sustainability_metrics: {
        carbon_footprint: 320.8,
        energy_consumption: 4500,
        waste_reduction: 28.5,
        renewable_energy_percentage: 65.0,
        waste_reduction_percentage: 35.0,
        scope_1_emissions: 120.5,
        scope_2_emissions: 85.3,
        scope_3_emissions: 115.0,
      },
      emission_sources: {
        manufacturing: 180.2,
        transportation: 45.6,
        energy_consumption: 95.0,
      },
      reduction_strategies: [
        "Process optimization",
        "Renewable energy adoption",
        "Supply chain optimization",
        "Employee training programs",
      ],
      baseline_year: 2020,
      baseline_emissions: 450.0,
      reduction_achieved: 28.7,
    },
  },
  {
    name: "Energy Audit",
    description: "Energy efficiency audit with recommendations",
    icon: <Zap className="w-5 h-5" />,
    filename: "energy-audit.json",
    data: {
      document_type: "energy_audit",
      title: "Energy Efficiency Audit Report",
      organization: "Sustainable Office Complex",
      audit_date: "2024-02-20",
      sustainability_metrics: {
        carbon_footprint: 95.3,
        energy_consumption: 1800,
        waste_reduction: 22.0,
        renewable_energy_percentage: 95.0,
        waste_reduction_percentage: 40.0,
        energy_efficiency_score: 88.5,
        hvac_efficiency: 92.0,
        lighting_efficiency: 85.0,
      },
      energy_sources: {
        solar: 60.0,
        wind: 25.0,
        grid_renewable: 10.0,
        grid_fossil: 5.0,
      },
      efficiency_measures: [
        "LED lighting retrofit",
        "Smart HVAC controls",
        "Insulation improvements",
        "Energy monitoring systems",
      ],
      savings_achieved: {
        energy_saved_kwh: 2500,
        cost_savings_usd: 15000,
        co2_reduced_kg: 1200,
      },
      recommendations: [
        "Install battery storage",
        "Implement demand response",
        "Upgrade to smart meters",
      ],
    },
  },
  {
    name: "Waste Management",
    description: "Waste reduction and recycling program results",
    icon: <Recycle className="w-5 h-5" />,
    filename: "waste-management.json",
    data: {
      document_type: "waste_management",
      title: "Waste Reduction and Recycling Program",
      organization: "Eco-Friendly Retail Chain",
      program_start_date: "2024-01-01",
      sustainability_metrics: {
        carbon_footprint: 75.2,
        energy_consumption: 1200,
        waste_reduction: 45.8,
        renewable_energy_percentage: 70.0,
        waste_reduction_percentage: 60.0,
        recycling_rate: 85.0,
        composting_rate: 40.0,
        landfill_diversion: 80.0,
      },
      waste_categories: {
        organic_waste: 35.0,
        recyclable_materials: 45.0,
        hazardous_waste: 5.0,
        landfill_waste: 15.0,
      },
      reduction_initiatives: [
        "Composting program",
        "Plastic-free packaging",
        "Donation programs",
        "Supplier waste reduction",
      ],
      achievements: {
        waste_reduced_tons: 25.5,
        recycling_increased: 30.0,
        cost_savings: 12000,
      },
      certifications: ["Zero Waste to Landfill", "Green Business Certified"],
    },
  },
  {
    name: "Green Certification",
    description: "LEED Platinum certification for sustainable building",
    icon: <Award className="w-5 h-5" />,
    filename: "green-certification.json",
    data: {
      document_type: "green_certification",
      title: "LEED Platinum Building Certification",
      organization: "Sustainable Architecture Firm",
      certification_date: "2024-03-10",
      sustainability_metrics: {
        carbon_footprint: 45.8,
        energy_consumption: 800,
        waste_reduction: 35.0,
        renewable_energy_percentage: 100.0,
        waste_reduction_percentage: 75.0,
        water_efficiency: 90.0,
        indoor_air_quality: 95.0,
        sustainable_materials: 85.0,
      },
      certification_details: {
        certification_type: "LEED Platinum",
        certifying_body: "USGBC",
        score_achieved: 85,
        points_earned: 85,
        total_possible: 100,
      },
      sustainable_features: [
        "Net-zero energy building",
        "Rainwater harvesting system",
        "Green roof installation",
        "Solar panel array",
        "Geothermal heating",
        "Natural ventilation",
      ],
      performance_metrics: {
        energy_use_intensity: 25,
        water_use_reduction: 40,
        renewable_energy_percentage: 100,
        waste_diverted: 90,
      },
      innovation_credits: [
        "Carbon neutral operations",
        "Living building challenge",
        "Biophilic design elements",
      ],
    },
  },
];

interface SampleDocumentsProps {
  className?: string;
}

const SampleDocuments: React.FC<SampleDocumentsProps> = ({
  className = "",
}) => {
  const downloadSample = (sampleDoc: SampleDocument) => {
    const dataStr = JSON.stringify(sampleDoc.data, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = sampleDoc.filename;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          📄 Sample Documents
        </h3>
        <p className="text-sm text-gray-600">
          Download sample JSON documents to test the sustainability analysis
          system
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sampleDocuments.map((doc, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start space-x-3 mb-3">
              <div className="flex-shrink-0 text-green-600">{doc.icon}</div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {doc.name}
                </h4>
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                  {doc.description}
                </p>
              </div>
            </div>

            <button
              onClick={() => downloadSample(doc)}
              className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>
        ))}
      </div>

      <div className="mt-4 space-y-3">
        <div className="p-3 bg-blue-50 rounded-md">
          <p className="text-xs text-blue-700">
            💡 <strong>Tip:</strong> Download any sample document and upload it
            back to see how the system analyzes different types of
            sustainability data and calculates ECO token rewards!
          </p>
        </div>

        <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
          <p className="text-xs text-amber-800">
            ⚠️ <strong>Important Notice:</strong> File reading functionality is
            not yet implemented. Please use the sample JSON documents provided
            above to test the system. This feature will be added in the next
            development phase.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SampleDocuments;
