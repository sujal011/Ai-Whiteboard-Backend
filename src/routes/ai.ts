import { Hono } from 'hono';
import { streamText as streamTextAI, generateText } from 'ai';
import {streamText} from 'hono/streaming'
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { google } from '@ai-sdk/google';
import { z } from 'zod';
import { authMiddleware } from '../middleware/auth';
import { dbHelpers } from '../db/connection';
import { fileProcessor } from '../services/fileProcessor';

export const aiRoutes = new Hono();

// Apply auth middleware
aiRoutes.use('*', authMiddleware);

// Validation schemas
const askAISchema = z.object({
  message: z.string().min(1, 'Message is required'),
  workspaceId: z.string().uuid('Valid workspace ID is required'),
  model: z.enum(['gpt-4', 'gpt-3.5-turbo', 'claude-3-sonnet', 'claude-3-haiku', 'gemini-pro', 'gemini-1.5-pro']).default('gpt-4'),
  includeContext: z.boolean().default(true),
  maxTokens: z.number().min(1).max(4000).default(1000),
});

// Model configuration
const getModelConfig = (modelName: string) => {
  switch (modelName) {
    case 'gpt-4o':
      return openai('gpt-4o');
    case 'gpt-3.5-turbo':
      return openai('gpt-3.5-turbo');
    case 'claude-3-7':
      return anthropic('claude-3-7-sonnet-20250219');
    case 'gemini-2.5-flash':
      return google('gemini-2.5-flash');
    case 'gemini-2.5-pro':
      return google('gemini-2.5-pro');
    default:
      return google('gemini-2.5-flash');
  }
};

// RAG-enabled AI chat endpoint (streaming)
aiRoutes.post('/ask-files', async (c) => {
  try {
    const user = c.get('user');
    const body = await c.req.json();
    const { message, workspaceId, model, includeContext, maxTokens } = askAISchema.parse(body);

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    let contextContent = '';
    let sources: any[] = [];

    // Get relevant context if requested
    if (includeContext) {
      try {
        // Search for similar content in vector database
        const similarChunks = await fileProcessor.searchSimilarChunks(workspaceId, message, 5);
        
        if (similarChunks.length > 0) {
          contextContent = similarChunks
            .map((chunk, index) => 
              `[Context ${index + 1}] From "${chunk.filename}":\n${chunk.content}`
            )
            .join('\n\n');
          
          sources = similarChunks.map(chunk => ({
            filename: chunk.filename,
            content_preview: chunk.content.substring(0, 100) + '...',
            file_type: chunk.metadata.blobType,
          }));
        }

        // Get workspace content (Excalidraw/EditorJS data)
        const workspaceContent = await dbHelpers.getWorkspaceById(workspaceId,user.id);
        if (workspaceContent) {
          if (workspaceContent.editorjs_data) {
            contextContent += `\n\n[Workspace Notes]:\n${JSON.stringify(workspaceContent.editorjs_data, null, 2)}`;
          }
          if (workspaceContent.excalidraw_data) {
            contextContent += `\n\n[Workspace Drawings]: User has created visual diagrams/drawings in this workspace.`;
          }
        }
      } catch (searchError) {
        console.warn('Context search failed:', searchError);
        // Continue without context rather than failing
      }
    }

    // Build system prompt
    const systemPrompt = `You are an AI assistant helping a user with their workspace content. 
You have access to their uploaded documents, notes, and drawings.

${contextContent ? `Here is relevant context from their workspace:

${contextContent}

Use this context to provide accurate and helpful responses. Always cite which documents or sources you're referencing.` : 'The user has not provided any context or uploaded files for this query.'}

Be helpful, accurate, and concise. If you reference information from the context, always mention which file or source it came from.`;

    // Stream the AI response
    const modelInstance = getModelConfig(model);
    
    const result = streamTextAI({
      model: modelInstance,
      system: systemPrompt,
      messages: [
        {
          role: 'user',
          content: message,
        },
      ],
      temperature: 0.7,
    });

        return streamText(c, async (stream) => {
            // Write a text with a new line ('\n').
            for await (const textPart of result.textStream) {
                // console.log(textPart);
            await stream.writeln(textPart)

              }
      })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return c.json({ error: 'Validation failed', details: error.message }, 400);
    }
    
    console.error('AI ask error:', error);
    return c.json({ error: 'Failed to process AI request' }, 500);
  }
  
});

// Non-streaming AI chat endpoint
/*
aiRoutes.post('/ask-sync', async (c) => {
  try {
    const user = c.get('user');
    const body = await c.req.json();
    const { message, workspaceId, model, includeContext, maxTokens } = askAISchema.parse(body);

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    let contextContent = '';
    let sources: any[] = [];

    // Get relevant context if requested
    if (includeContext) {
      try {
        const similarChunks = await fileProcessor.searchSimilarChunks(workspaceId, message, 5);
        
        if (similarChunks.length > 0) {
          contextContent = similarChunks
            .map((chunk, index) => 
              `[Context ${index + 1}] From "${chunk.filename}":\n${chunk.content}`
            )
            .join('\n\n');
          
          sources = similarChunks.map(chunk => ({
            filename: chunk.filename,
            content_preview: chunk.content.substring(0, 100) + '...',
            relevance_score: chunk.score,
            file_type: chunk.metadata.file_type,
          }));
        }

        const workspaceContent = await dbHelpers.getWorkspaceContent(workspaceId);
        if (workspaceContent) {
          if (workspaceContent.editorjs_data) {
            contextContent += `\n\n[Workspace Notes]:\n${JSON.stringify(workspaceContent.editorjs_data, null, 2)}`;
          }
          if (workspaceContent.excalidraw_data) {
            contextContent += `\n\n[Workspace Drawings]: User has created visual diagrams/drawings in this workspace.`;
          }
        }
      } catch (searchError) {
        console.warn('Context search failed:', searchError);
      }
    }

    const systemPrompt = `You are an AI assistant helping a user with their workspace content. 
You have access to their uploaded documents, notes, and drawings.

${contextContent ? `Here is relevant context from their workspace:

${contextContent}

Use this context to provide accurate and helpful responses. Always cite which documents or sources you're referencing.` : 'The user has not provided any context or uploaded files for this query.'}

Be helpful, accurate, and concise. If you reference information from the context, always mention which file or source it came from.`;

    const modelInstance = getModelConfig(model);
    
    const { text } = await generateText({
      model: modelInstance,
      system: systemPrompt,
      messages: [
        {
          role: 'user',
          content: message,
        },
      ],
      maxTokens,
      temperature: 0.7,
    });

    // Save conversation to database (optional)
    try {
      await dbHelpers.db`
        INSERT INTO ai_conversations (workspace_id, user_message, ai_response, model_used)
        VALUES (${workspaceId}, ${message}, ${text}, ${model})
      `;
    } catch (saveError) {
      console.warn('Failed to save conversation:', saveError);
    }

    return c.json({
      response: text,
      sources,
      model_used: model,
      context_included: includeContext,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    if (error instanceof z.ZodError) {
      return c.json({ error: 'Validation failed', details: error.errors }, 400);
    }
    
    console.error('AI ask sync error:', error);
    return c.json({ error: 'Failed to process AI request' }, 500);
  }
});

// Get conversation history for a workspace
aiRoutes.get('/conversations/:workspaceId', async (c) => {
  try {
    const user = c.get('user');
    const workspaceId = c.req.param('workspaceId');
    const limit = parseInt(c.req.query('limit') || '50');
    const offset = parseInt(c.req.query('offset') || '0');

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    const conversations = await dbHelpers.db`
      SELECT id, user_message, ai_response, model_used, created_at
      FROM ai_conversations 
      WHERE workspace_id = ${workspaceId}
      ORDER BY created_at DESC
      LIMIT ${limit} OFFSET ${offset}
    `;

    return c.json({
      conversations,
      workspace: {
        id: workspace.id,
        name: workspace.name,
      },
      pagination: {
        limit,
        offset,
        total: conversations.length,
      }
    });
  } catch (error) {
    console.error('Get conversations error:', error);
    return c.json({ error: 'Failed to fetch conversations' }, 500);
  }
});

// Available models endpoint
aiRoutes.get('/models', async (c) => {
  return c.json({
    models: [
      {
        id: 'gpt-4',
        name: 'GPT-4 Turbo',
        provider: 'OpenAI',
        description: 'Most capable GPT model, great for complex reasoning',
      },
      {
        id: 'gpt-3.5-turbo',
        name: 'GPT-3.5 Turbo',
        provider: 'OpenAI',
        description: 'Fast and efficient, good for most tasks',
      },
      {
        id: 'claude-3-sonnet',
        name: 'Claude 3 Sonnet',
        provider: 'Anthropic',
        description: 'Balanced performance and speed',
      },
      {
        id: 'claude-3-haiku',
        name: 'Claude 3 Haiku',
        provider: 'Anthropic',
        description: 'Fast and concise responses',
      },
      {
        id: 'gemini-pro',
        name: 'Gemini Pro',
        provider: 'Google',
        description: 'Google\'s advanced language model',
      },
      {
        id: 'gemini-1.5-pro',
        name: 'Gemini 1.5 Pro',
        provider: 'Google',
        description: 'Latest Gemini model with enhanced capabilities',
      },
    ],
  });
});
*/