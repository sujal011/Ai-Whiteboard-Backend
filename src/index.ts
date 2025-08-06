import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { authRoutes } from "./routes/auth";
import { workspaceRoutes } from "./routes/workspaces";
import { aiRoutes } from "./routes/ai";

const app = new Hono();

app.use('*', cors({
    origin: '*',
    allowHeaders: ['Content-Type', 'Authorization'],
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
}));
app.use('*', logger());


// Health check
app.get('/health', (c) => {
    return c.json({ status: 'ok', timestamp: new Date().toISOString() });
  });


app.route('/auth', authRoutes);
app.route('/workspaces',workspaceRoutes)
app.route('/ai',aiRoutes)

// Error handler
app.onError((err, c) => {
    console.error('Error:', err);
    return c.json({ error: 'Internal Server Error' }, 500);
  });
  
  // 404 handler
  app.notFound((c) => {
    return c.json({ error: 'Not Found' }, 404);
  });
  
  const port = process.env.PORT || 3001;
  
  console.log(`Server is running on port ${port}`);
  
  export default {
    port,
    fetch: app.fetch,
  };