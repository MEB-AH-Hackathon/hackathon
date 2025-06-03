import type { AnalysisResult, StructuredReport } from '../types';

export class ReportGenerator {
  generateReport(analysis: AnalysisResult): StructuredReport {
    return {
      summary: this.generateSummary(analysis),
      disclaimer: "VAERS reports are unverified and may contain errors. This analysis is for informational purposes only and should not replace professional medical advice. Always consult with healthcare providers for medical decisions.",
      
      sections: [
        {
          title: "FDA Validated Information",
          content: this.formatFDAFindings(analysis.fdaResults),
          confidence: this.calculateFDAConfidence(analysis.fdaResults)
        },
        {
          title: "Similar VAERS Reports",
          content: this.formatSimilarReports(analysis.similarReports),
          links: analysis.similarReports.map(r => ({
            vaersId: r.vaersId,
            similarity: r.similarityScore
          }))
        },
        {
          title: "Analysis Summary",
          content: this.generateAnalysisSummary(analysis)
        }
      ],
      
      metadata: {
        searchedDatabases: ['FDA Labels', 'FDA Trials', 'VAERS Historical'],
        analysisDate: new Date(),
        confidenceLevel: analysis.overallConfidence
      }
    };
  }

  private generateSummary(analysis: AnalysisResult): string {
    const { extractedInfo, fdaResults, similarReports } = analysis;
    const totalFDAReports = fdaResults.reduce((acc, r) => acc + r.foundReports, 0);
    
    let summary = `Analysis of VAERS report for ${extractedInfo.patientInfo.age || 'unknown age'} year old ${extractedInfo.patientInfo.sex || 'patient'} `;
    summary += `who received ${extractedInfo.vaccines.map(v => v.type).join(', ')} vaccine(s). `;
    
    if (extractedInfo.onsetDays) {
      summary += `Symptoms appeared ${extractedInfo.onsetDays} days after vaccination. `;
    }
    
    summary += `Found ${totalFDAReports} FDA-validated reports and ${similarReports.length} similar VAERS cases. `;
    
    const severeOutcomes = [];
    if (extractedInfo.outcomes.died) severeOutcomes.push('death');
    if (extractedInfo.outcomes.lifeThreatening) severeOutcomes.push('life-threatening event');
    if (extractedInfo.outcomes.hospitalized) severeOutcomes.push('hospitalization');
    if (extractedInfo.outcomes.disabled) severeOutcomes.push('disability');
    
    if (severeOutcomes.length > 0) {
      summary += `Report includes severe outcomes: ${severeOutcomes.join(', ')}.`;
    }
    
    return summary;
  }

  private formatFDAFindings(fdaResults: any[]): string {
    if (fdaResults.length === 0) {
      return "No FDA-validated data found for the reported vaccine-symptom combinations. This does not necessarily indicate the symptoms are not related to the vaccine, only that they were not found in the FDA database searched.";
    }

    let content = "";
    for (const result of fdaResults) {
      content += `\n**${result.vaccine}**\n`;
      content += `- Found ${result.foundReports} FDA reports\n`;
      content += `- Searched symptoms: ${result.symptoms.join(', ')}\n`;
      
      if (result.reports.length > 0) {
        content += `- Top matching studies:\n`;
        result.reports.slice(0, 3).forEach((report: any) => {
          content += `  - ${report.studyType} (${report.sourceSection}): ${report.symptoms.slice(0, 5).join(', ')}\n`;
        });
      }
    }
    
    return content;
  }

  private formatSimilarReports(similarReports: any[]): string {
    if (similarReports.length === 0) {
      return "No similar reports found in the VAERS database.";
    }

    let content = `Found ${similarReports.length} similar VAERS reports:\n\n`;
    
    similarReports.slice(0, 5).forEach((report, index) => {
      content += `${index + 1}. VAERS ID: ${report.vaersId} (${Math.round(report.similarityScore * 100)}% match)\n`;
      content += `   - Vaccines: ${report.vaccines.join(', ')}\n`;
      content += `   - Matched symptoms: ${report.matchedSymptoms.slice(0, 5).join(', ')}\n`;
      if (report.outcomes.length > 0) {
        content += `   - Outcomes: ${report.outcomes.join(', ')}\n`;
      }
      content += '\n';
    });
    
    return content;
  }

  private generateAnalysisSummary(analysis: AnalysisResult): string {
    const { fdaResults, similarReports, extractedInfo } = analysis;
    const hasFDAMatches = fdaResults.some(r => r.foundReports > 0);
    const hasSimilarReports = similarReports.length > 0;
    
    let summary = "";
    
    if (hasFDAMatches) {
      summary += "The reported symptoms have been documented in FDA-validated data for these vaccines. ";
    } else {
      summary += "The reported symptoms were not found in FDA-validated data, which may indicate they are uncommon or not previously documented. ";
    }
    
    if (hasSimilarReports) {
      const avgSimilarity = similarReports.reduce((acc, r) => acc + r.similarityScore, 0) / similarReports.length;
      if (avgSimilarity > 0.7) {
        summary += "Multiple highly similar reports exist in VAERS, suggesting this may be a recurring pattern. ";
      } else if (avgSimilarity > 0.4) {
        summary += "Some similar reports exist in VAERS with moderate similarity. ";
      } else {
        summary += "Few similar reports found, suggesting this may be a less common presentation. ";
      }
    }
    
    // Add severity assessment
    const severeOutcomes = [
      extractedInfo.outcomes.died,
      extractedInfo.outcomes.lifeThreatening,
      extractedInfo.outcomes.hospitalized,
      extractedInfo.outcomes.disabled
    ].filter(Boolean).length;
    
    if (severeOutcomes > 0) {
      summary += `This report includes ${severeOutcomes} severe outcome(s), requiring careful medical evaluation. `;
    }
    
    return summary;
  }

  private calculateFDAConfidence(fdaResults: any[]): 'high' | 'medium' | 'low' {
    const totalReports = fdaResults.reduce((acc, r) => acc + r.foundReports, 0);
    
    if (totalReports > 10) return 'high';
    if (totalReports > 3) return 'medium';
    return 'low';
  }
}