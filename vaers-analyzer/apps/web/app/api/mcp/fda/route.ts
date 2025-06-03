/**
 * POST handler for MCP FDA tool proxy
 */
export async function POST(request: Request) {
  try {
    const { tool, params } = await request.json();
    
    if (!tool || !params) {
      return Response.json({ error: 'Missing tool or params' }, { status: 400 });
    }

    // Forward request to MCP server
    const mcpResponse = await fetch('http://localhost:3001/fda', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tool, params }),
    });

    if (!mcpResponse.ok) {
      return Response.json(
        { error: 'MCP server error' }, 
        { status: mcpResponse.status }
      );
    }

    const result = await mcpResponse.json();
    return Response.json(result);
  } catch (error) {
    console.error('MCP proxy error:', error);
    return Response.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}