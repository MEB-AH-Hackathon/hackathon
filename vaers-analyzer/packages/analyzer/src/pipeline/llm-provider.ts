import Anthropic from '@anthropic-ai/sdk';
import 'dotenv/config';

export class LLMProvider {
  private client: Anthropic;

  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY || '',
    });
  }

  async extractKeyInformation(reportText: string): Promise<any> {
    const message = await this.client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      temperature: 0,
      system: `You are a medical data extraction assistant. Extract structured information from VAERS reports.`,
      messages: [
        {
          role: 'user',
          content: `Extract the following information from this VAERS report and return as JSON:
          - vaccines (array of {type, manufacturer, dose})
          - symptoms (array of symptom names)
          - outcomes (object with died, lifeThreatening, hospitalized, disabled, emergencyRoom as booleans)
          - onsetDays (number of days between vaccination and symptom onset)
          - patientInfo (age, sex)
          
          Report text:
          ${reportText}
          
          Return only valid JSON.`
        }
      ]
    });

    const content = message.content[0];
    if (content && content.type === 'text') {
      try {
        return JSON.parse(content.text);
      } catch (e) {
        throw new Error('Failed to parse LLM response as JSON');
      }
    }
    throw new Error('Unexpected response type from LLM');
  }

  async generateAnalysis(data: {
    report: any;
    fdaResults: any[];
    similarReports: any[];
  }): Promise<any> {
    const message = await this.client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      temperature: 0,
      system: `You are a medical analysis assistant specializing in vaccine adverse event reports. 
      Provide objective, evidence-based analysis while being clear about limitations and uncertainties.`,
      messages: [
        {
          role: 'user',
          content: `Analyze this VAERS report data and provide:
          1. A summary of findings
          2. Overall confidence level (high/medium/low) based on FDA validation matches
          3. Key recommendations for healthcare providers
          
          Data:
          ${JSON.stringify(data, null, 2)}
          
          Return as JSON with fields: summary, overallConfidence, recommendations (array)`
        }
      ]
    });

    const content = message.content[0];
    if (content && content.type === 'text') {
      try {
        return JSON.parse(content.text);
      } catch (e) {
        throw new Error('Failed to parse analysis response as JSON');
      }
    }
    throw new Error('Unexpected response type from LLM');
  }

  async findRelevantSearchTerms(extractedInfo: any): Promise<string[]> {
    const message = await this.client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      temperature: 0,
      system: `You are a medical search assistant. Generate relevant search terms for finding similar cases.`,
      messages: [
        {
          role: 'user',
          content: `Given this extracted information from a VAERS report, generate 5-10 relevant search terms 
          that would help find similar cases or validate symptoms. Include medical synonyms and related conditions.
          
          ${JSON.stringify(extractedInfo, null, 2)}
          
          Return as JSON array of strings.`
        }
      ]
    });

    const content = message.content[0];
    if (content && content.type === 'text') {
      try {
        return JSON.parse(content.text);
      } catch (e) {
        return [];
      }
    }
    return [];
  }
}