; Impact Score Calculation Rules
; MeTTa knowledge base for sustainability impact scoring

; Base scoring functions
(= (base-carbon-score $carbon)
   (if (> $carbon 1000)
       100
       (if (> $carbon 500)
           80
           (if (> $carbon 200)
               60
               (if (> $carbon 100)
                   40
                   20)))))

(= (base-waste-score $waste)
   (if (> $waste 50)
       100
       (if (> $waste 30)
           80
           (if (> $waste 20)
               60
               (if (> $waste 10)
                   40
                   20)))))

(= (base-renewable-score $renewable)
   (if (> $renewable 80)
       100
       (if (> $renewable 60)
           80
           (if (> $renewable 40)
               60
               (if (> $renewable 20)
                   40
                   20)))))

; Weighted scoring
(= (weighted-score $carbon $waste $renewable)
   (let*
       ($carbon-weighted (* (base-carbon-score $carbon) 0.4))
       ($waste-weighted (* (base-waste-score $waste) 0.3))
       ($renewable-weighted (* (base-renewable-score $renewable) 0.3)))
       (+ $carbon-weighted $waste-weighted $renewable-weighted)))

; Document type bonuses
(= (document-bonus "sustainability_document") 0)
(= (document-bonus "carbon_report") 10)
(= (document-bonus "energy_audit") 5)
(= (document-bonus "waste_management") 0)
(= (document-bonus "green_certification") 15)

; Final impact score calculation
(= (final-impact-score $carbon $waste $renewable $doc-type)
   (let*
       ($base-score (weighted-score $carbon $waste $renewable))
       ($bonus (document-bonus $doc-type)))
       (min 100 (+ $base-score $bonus))))

; Token amount calculation based on impact score
(= (token-amount $impact-score)
   (if (> $impact-score 90)
       100
       (if (> $impact-score 80)
           80
           (if (> $impact-score 70)
               60
               (if (> $impact-score 60)
                   40
                   (if (> $impact-score 50)
                       20
                       0))))))

; Sustainability level classification
(= (sustainability-level $score)
   (if (> $score 90)
       "excellent"
       (if (> $score 80)
           "very-good"
           (if (> $score 70)
               "good"
               (if (> $score 60)
                   "fair"
                   (if (> $score 50)
                       "poor"
                       "insufficient"))))))

; Environmental impact assessment
(= (environmental-impact $carbon $waste $renewable)
   (let*
       ($total-impact (+ $carbon $waste $renewable))
       (if (> $total-impact 1000)
           "high"
           (if (> $total-impact 500)
               "medium"
               "low"))))

; Recommendation generation
(= (recommendation $level $impact)
   (if (= $level "excellent")
       "Outstanding sustainability performance! Consider sharing best practices."
       (if (= $level "very-good")
           "Great sustainability efforts! Continue current practices."
           (if (= $level "good")
               "Good progress! Focus on areas with highest impact potential."
               (if (= $level "fair")
                   "Room for improvement. Consider implementing additional sustainability measures."
                   (if (= $level "poor")
                       "Significant improvement needed. Develop comprehensive sustainability strategy."
                       "Insufficient data or impact. Please provide more detailed sustainability information."))))))
