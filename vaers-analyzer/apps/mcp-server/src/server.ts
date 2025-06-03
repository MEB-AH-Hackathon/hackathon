import express from 'express';
import cors from 'cors';
import { fdaTools, ToolName } from '@vaers/mcp-tools';

const app = express();
app.use(cors());
app.use(express.json());

app.post('/fda', (req, res) => {
  const { tool, params } = req.body as { tool: ToolName; params: any };
  if (!tool || !(tool in fdaTools)) {
    return res.status(400).json({ error: 'Invalid tool' });
  }

  // Placeholder implementation that simply echoes params
  res.json({ tool, params, result: null });
});

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`MCP server listening on port ${port}`);
});
