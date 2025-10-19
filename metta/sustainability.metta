; Main MeTTa file for EcoChain Sustainability Analysis
; This file loads all sustainability knowledge base modules

; Load sustainability rules
(load "knowledge/sustainability-rules.metta")

; Load document type classification
(load "knowledge/document-types.metta")

; Load impact scoring rules
(load "knowledge/impact-scoring.metta")

; Main analysis function
(= (analyze-sustainability $carbon $waste $renewable $doc-type)
   (let*
       ($impact-score (final-impact-score $carbon $waste $renewable $doc-type))
       ($token-amount (token-amount $impact-score))
       ($should-mint (should-mint $impact-score))
       ($level (sustainability-level $impact-score))
       ($impact (environmental-impact $carbon $waste $renewable)))
       (list $impact-score $token-amount $should-mint $level $impact)))

; Document analysis function
(= (analyze-document $content $doc-type)
   (let*
       ($classified-type (document-type $content))
       ($analysis (analyze-sustainability $content $doc-type)))
       (list $classified-type $analysis)))

; Export main functions
(= (main-analysis $data)
   (analyze-sustainability 
       (get $data "carbon_footprint")
       (get $data "waste_reduction")
       (get $data "renewable_energy")
       (get $data "document_type")))
