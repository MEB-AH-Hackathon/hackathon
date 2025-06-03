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
      system: `You are a medical data extraction assistant. Extract structured information from VAERS reports. Always respond with valid JSON only, no additional text or markdown formatting.`,
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
          
          Return ONLY valid JSON without any markdown formatting or explanation.`
        }
      ]
    });

    const content = message.content[0];
    if (content && content.type === 'text') {
      try {
        // Try to extract JSON from the response
        let jsonText = content.text.trim();
        
        // Remove markdown code blocks if present
        if (jsonText.startsWith('```json')) {
          jsonText = jsonText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
        } else if (jsonText.startsWith('```')) {
          jsonText = jsonText.replace(/^```\s*/, '').replace(/\s*```$/, '');
        }
        
        return JSON.parse(jsonText);
      } catch (e) {
        console.error('Failed to parse LLM response:', content.text);
        throw new Error('Failed to parse LLM response as JSON: ' + (e instanceof Error ? e.message : String(e)));
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
      Provide objective, evidence-based analysis while being clear about limitations and uncertainties.
      Always respond with valid JSON only, no additional text or markdown formatting.`,
      messages: [
        {
          role: 'user',
          content: `Analyze this VAERS report data and provide:
          1. A summary of findings
          2. Overall confidence level (high/medium/low) based on FDA validation matches
          3. Key recommendations for healthcare providers
          
          Data:
          ${JSON.stringify(data, null, 2)}
          
          Return ONLY valid JSON with fields: summary (string), overallConfidence (string: "high" | "medium" | "low"), recommendations (array of strings).
          Do not include any markdown formatting or explanation.`
        }
      ]
    });

    const content = message.content[0];
    if (content && content.type === 'text') {
      try {
        // Try to extract JSON from the response
        let jsonText = content.text.trim();
        
        // Remove markdown code blocks if present
        if (jsonText.startsWith('```json')) {
          jsonText = jsonText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
        } else if (jsonText.startsWith('```')) {
          jsonText = jsonText.replace(/^```\s*/, '').replace(/\s*```$/, '');
        }
        
        return JSON.parse(jsonText);
      } catch (e) {
        console.error('Failed to parse analysis response:', content.text);
        throw new Error('Failed to parse analysis response as JSON: ' + (e instanceof Error ? e.message : String(e)));
      }
    }
    throw new Error('Unexpected response type from LLM');
  }

  async findRelevantSearchTerms(extractedInfo: any): Promise<string[]> {
    const message = await this.client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      temperature: 0,
      system: `You are a medical search assistant. Generate relevant search terms for finding similar cases. Always respond with valid JSON only, no additional text or markdown formatting.`,
      messages: [
        {
          role: 'user',
          content: `Given this extracted information from a VAERS report, generate 5-10 relevant search terms 
          that would help find similar cases or validate symptoms. Include medical synonyms and related conditions.
          
          ${JSON.stringify(extractedInfo, null, 2)}
          
          Return ONLY a JSON array of strings. No markdown or explanation.`
        }
      ]
    });

    const content = message.content[0];
    if (content && content.type === 'text') {
      try {
        // Try to extract JSON from the response
        let jsonText = content.text.trim();
        
        // Remove markdown code blocks if present
        if (jsonText.startsWith('```json')) {
          jsonText = jsonText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
        } else if (jsonText.startsWith('```')) {
          jsonText = jsonText.replace(/^```\s*/, '').replace(/\s*```$/, '');
        }
        
        return JSON.parse(jsonText);
      } catch (e) {
        console.error('Failed to parse search terms:', content.text);
        return [];
      }
    }
    return [];
  }
}