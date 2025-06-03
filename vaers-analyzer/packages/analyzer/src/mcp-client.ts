import type { ToolName, ToolParams } from '@vaers/mcp-tools';

export class MCPClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async call<T extends ToolName>(tool: T, params: ToolParams<T>): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}/fda`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool, params })
    });

    if (!response.ok) {
      throw new Error(`MCP request failed: ${response.statusText}`);
    }

    return response.json();
  }
}
