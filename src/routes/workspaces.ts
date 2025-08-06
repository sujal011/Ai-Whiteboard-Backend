import { Hono } from 'hono';
import { z } from 'zod';
import { authMiddleware } from '../middleware/auth';
import { db, dbHelpers } from '../db/connection';
import { fileProcessor } from '../services/fileProcessor';

export const workspaceRoutes = new Hono();

// Apply auth middleware to all workspace routes
workspaceRoutes.use('*', authMiddleware);

// Validation schemas
const createWorkspaceSchema = z.object({
  name: z.string().min(1, 'Workspace name is required').max(255),
  description: z.string().optional(),
});

const updateContentSchema = z.object({
  excalidrawData: z.any().optional(),
  editorjsData: z.any().optional(),
});

// Get all workspaces for the current user
workspaceRoutes.get('/', async (c) => {
  try {
    const user = c.get('user');
    const workspaces = await dbHelpers.getUserWorkspaces(user.id);
    
    return c.json({
      workspaces: workspaces.map(w => ({
        id: w.id,
        name: w.name,
        description: w.description,
        created_at: w.created_at,
        updated_at: w.updated_at,
      }))
    });
  } catch (error) {
    console.error('Get workspaces error:', error);
    return c.json({ error: 'Failed to fetch workspaces' }, 500);
  }
});

// Create a new workspace
workspaceRoutes.post('/', async (c) => {
  try {
    const user = c.get('user');
    const body = await c.req.json();
    const { name, description } = createWorkspaceSchema.parse(body);

    // Check workspace limit (max 5)
    const existingWorkspaces = await dbHelpers.getUserWorkspaces(user.id);
    if (existingWorkspaces.length >= 5) {
      return c.json({ error: 'Maximum workspace limit (5) reached' }, 400);
    }

    // Check for duplicate names
    const duplicateName = existingWorkspaces.find(w => w.name.toLowerCase() === name.toLowerCase());
    if (duplicateName) {
      return c.json({ error: 'Workspace with this name already exists' }, 400);
    }

    const workspace = await dbHelpers.createWorkspace(user.id, name, description);
    if(!workspace){
        throw new Error('Error creating new workspace');
    }

    return c.json({
      message: 'Workspace created successfully',
      workspace: {
        id: workspace.id,
        name: workspace.name,
        description: workspace.description,
        created_at: workspace.created_at,
        updated_at: workspace.updated_at,
      }
    }, 201);
  } catch (error: any) {
    if (error instanceof z.ZodError) {
      return c.json({ error: 'Validation failed', details: error.message }, 400);
    }
    
    console.error('Create workspace error:', error);
    return c.json({ error: 'Failed to create workspace' }, 500);
  }
});

// Get workspace by ID
workspaceRoutes.get('/:id', async (c) => {
  try {
    const user = c.get('user');
    const workspaceId = c.req.param('id');

    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    const processedFiles = await dbHelpers.getProcessedFiles(workspaceId);

    return c.json({
      workspace: {
        id: workspace.id,
        name: workspace.name,
        description: workspace.description,
        created_at: workspace.created_at,
        updated_at: workspace.updated_at,
        excalidraw_data:workspace.excalidraw_data,
        editorjs_data: workspace.editorjs_data
      },
      files: processedFiles.length === 0? []: processedFiles.map(f => ({
        id: f.id,
        filename: f.filename,
        file_size: f.file_size,
        mime_type: f.mime_type,
        // vector_count: f.vector_count,
        processed_at: f.processed_at,
      }))
    });
  } catch (error) {
    console.error('Get workspace error:', error);
    return c.json({ error: 'Failed to fetch workspace' }, 500);
  }
});

// Update workspace content (Excalidraw/EditorJS data)
workspaceRoutes.put('/:id/content', async (c) => {
  try {
    const user = c.get('user');
    const workspaceId = c.req.param('id');
    const body = await c.req.json();
    const { excalidrawData, editorjsData } = updateContentSchema.parse(body);

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    const updatedContent = await dbHelpers.updateWorkspaceContent(
      workspaceId, 
      excalidrawData, 
      editorjsData
    );

    if(!updatedContent){
        throw new Error("Failed to update the workspace.")
    }

    return c.json({
      message: 'Content updated successfully',
      content: {
        excalidrawData: updatedContent.excalidraw_data,
        editorjsData: updatedContent.editorjs_data,
        updated_at: updatedContent.updated_at,
      }
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return c.json({ error: 'Validation failed', details: error.message }, 400);
    }
    
    console.error('Update content error:', error);
    return c.json({ error: 'Failed to update content' }, 500);
  }
});

// Upload and process files
workspaceRoutes.post('/:id/files', async (c) => {
  try {
    const user = c.get('user');
    const workspaceId = c.req.param('id');

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    // Check file limit (max 3)
    const existingFiles = await dbHelpers.getProcessedFiles(workspaceId);
    if (existingFiles.length >= 3) {
      return c.json({ error: 'Maximum file limit (3) reached for this workspace' }, 400);
    }

    const formData = await c.req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return c.json({ error: 'No file provided' }, 400);
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
    //   'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    //   'application/msword',
    //   'text/plain',
    //   'text/markdown',
    //   'application/vnd.ms-excel',
    //   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    if (!allowedTypes.includes(file.type)) {
      return c.json({ 
        error: 'Unsupported file type. Supported: PDF, DOC, DOCX, TXT, MD, XLS, XLSX' 
      }, 400);
    }

    // Process file and create vectors
    const result = await fileProcessor.processFile(file, workspaceId);

    // Save to database
    const processedFile = await dbHelpers.addProcessedFile(
      workspaceId,
      file.name,
      file.size,
      file.type,
    );

    if(!processedFile){
        throw new Error("Failed to create a processed files")
    }

    return c.json({
      message: 'File processed and vectorized successfully',
      file: {
        id: processedFile.id,
        filename: processedFile.filename,
        file_size: processedFile.file_size,
        mime_type: processedFile.mime_type,
        // vector_count: processedFile.vector_count,
        processed_at: processedFile.processed_at,
      }
    }, 201);
  } catch (error) {
    console.error('File upload error:', error);
    return c.json({ error: 'Failed to process file' }, 500);
  }
});

// Delete a processed file
workspaceRoutes.delete('/:id/files/:fileId', async (c) => {
  try {
    const user = c.get('user');
    const workspaceId = c.req.param('id');
    const fileId = c.req.param('fileId');

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    // Delete from database
    const deletedFile = await dbHelpers.deleteProcessedFile(fileId, workspaceId);
    if (!deletedFile) {
      return c.json({ error: 'File not found' }, 404);
    }

    // Delete from Qdrant (vectors associated with this file)
    await fileProcessor.deleteFileVectors(workspaceId, fileId);

    return c.json({
      message: 'File deleted successfully',
      deleted_file: {
        id: deletedFile.id,
        filename: deletedFile.filename,
      }
    });
  } catch (error) {
    console.error('Delete file error:', error);
    return c.json({ error: 'Failed to delete file' }, 500);
  }
});

// Delete workspace
workspaceRoutes.delete('/:id', async (c) => {
  try {
    const user = c.get('user');
    const workspaceId = c.req.param('id');

    // Verify workspace ownership
    const workspace = await dbHelpers.getWorkspaceById(workspaceId, user.id);
    if (!workspace) {
      return c.json({ error: 'Workspace not found' }, 404);
    }

    // Delete Qdrant collection
    await fileProcessor.deleteWorkspaceCollection(workspaceId);

    // Delete from database (CASCADE will handle related records)
    const deletedWorkspace = await dbHelpers.deleteWorkspace(workspaceId,user.id)

    return c.json({
      message: 'Workspace deleted successfully'
    });
  } catch (error) {
    console.error('Delete workspace error:', error);
    return c.json({ error: 'Failed to delete workspace' }, 500);
  }
});