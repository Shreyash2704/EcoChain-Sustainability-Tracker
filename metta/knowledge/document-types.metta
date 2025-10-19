; Document Type Classification Rules
; MeTTa knowledge base for document type recognition

; Document type definitions
(= (document-type "sustainability_document") 
   (and 
       (contains-carbon-data $content)
       (contains-environmental-metrics $content)))

(= (document-type "carbon_report")
   (and
       (contains-carbon-footprint $content)
       (contains-emission-data $content)))

(= (document-type "energy_audit")
   (and
       (contains-energy-usage $content)
       (contains-efficiency-metrics $content)))

(= (document-type "waste_management")
   (and
       (contains-waste-data $content)
       (contains-recycling-metrics $content)))

(= (document-type "green_certification")
   (and
       (contains-certification $content)
       (contains-compliance-data $content)))

; Content analysis predicates
(= (contains-carbon-data $content)
   (or
       (contains-keyword $content "carbon")
       (contains-keyword $content "co2")
       (contains-keyword $content "emission")))

(= (contains-environmental-metrics $content)
   (or
       (contains-keyword $content "sustainability")
       (contains-keyword $content "environmental")
       (contains-keyword $content "green")))

(= (contains-carbon-footprint $content)
   (or
       (contains-keyword $content "carbon footprint")
       (contains-keyword $content "co2 equivalent")
       (contains-keyword $content "emission factor")))

(= (contains-emission-data $content)
   (or
       (contains-keyword $content "emission")
       (contains-keyword $content "greenhouse gas")
       (contains-keyword $content "ghg")))

(= (contains-energy-usage $content)
   (or
       (contains-keyword $content "energy")
       (contains-keyword $content "kwh")
       (contains-keyword $content "electricity")))

(= (contains-efficiency-metrics $content)
   (or
       (contains-keyword $content "efficiency")
       (contains-keyword $content "consumption")
       (contains-keyword $content "usage")))

(= (contains-waste-data $content)
   (or
       (contains-keyword $content "waste")
       (contains-keyword $content "recycling")
       (contains-keyword $content "disposal")))

(= (contains-recycling-metrics $content)
   (or
       (contains-keyword $content "recycling rate")
       (contains-keyword $content "waste reduction")
       (contains-keyword $content "circular economy")))

(= (contains-certification $content)
   (or
       (contains-keyword $content "certification")
       (contains-keyword $content "standard")
       (contains-keyword $content "compliance")))

(= (contains-compliance-data $content)
   (or
       (contains-keyword $content "iso")
       (contains-keyword $content "leed")
       (contains-keyword $content "breeam")))

; Keyword matching helper
(= (contains-keyword $content $keyword)
   (string-contains (to-lower $content) (to-lower $keyword)))
