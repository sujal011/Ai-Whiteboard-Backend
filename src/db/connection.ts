import { drizzle } from 'drizzle-orm/bun-sql';
import { SQL } from 'bun';
import { processedFilesTable, usersTable, workspacesTable } from './schema';
import { and, desc, eq, sql } from 'drizzle-orm';

const client = new SQL(process.env.DATABASE_URL!);
export const db = drizzle({ client });


// Helper functions for common database operations
export const dbHelpers = {
  async getUserById(id: string) {
    const [user] = await db.select().from(usersTable).where(eq(usersTable.id, id));
    return user;
  },

  async getUserByEmail(email: string) {
    const [user] = await db.select().from(usersTable).where(eq(usersTable.email, email));
    return user;
  },

  async createUser(email: string, passwordHash: string, name: string) {
    const [user] = await db.insert(usersTable).values({ email, password_hash: passwordHash, name }).returning();
    return user;
  },

  async getUserWorkspaces(userId: string) {
    return await db.select().from(workspacesTable).where(eq(workspacesTable.user_id, userId)).orderBy(desc(workspacesTable.updated_at));
    // `
    //   SELECT w.*, 
    //          (SELECT COUNT(*) FROM processed_files pf WHERE pf.workspace_id = w.id) as file_count
    //   FROM workspaces w 
    //   WHERE w.user_id = ${userId}
    //   ORDER BY w.updated_at DESC
    // `;
  },

  async getWorkspaceById(id: string, userId: string) {
   const [workspace] = await db.select().from(workspacesTable).where(and(eq(workspacesTable.id,id),eq(workspacesTable.user_id,userId)));
    // `
    //   SELECT * FROM workspaces 
    //   WHERE id = ${id} AND user_id = ${userId}
    // `;
    return workspace;
  },

  async createWorkspace(userId: string, name: string, description: string = "") {
    const [workspace] = await db.insert(workspacesTable).values({user_id:userId,name,description}).returning();
    // `
    //   INSERT INTO workspaces (user_id, name, description)
    //   VALUES (${userId}, ${name}, ${description || ''})
    //   RETURNING *
    // `;
    
    // // Create initial workspace content
    // await sql`
    //   INSERT INTO workspace_content (workspace_id)
    //   VALUES (${workspace?.id})
    // `;
    
    return workspace;
  },

//   async getWorkspaceContent(workspaceId: string) {
//     const [content] = await db.select().from(workspacesTable).where(eq(workspacesTable.id,workspaceId))
    
//     // `
//     //   SELECT * FROM workspace_content 
//     //   WHERE workspace_id = ${workspaceId}
//     // `;
//     return content;
//   },

  async updateWorkspaceContent(workspaceId: string, excalidrawData?: any, editorjsData?: any) {
    const updates: any = { updated_at: new Date() };
    if (excalidrawData !== undefined) updates.excalidraw_data = excalidrawData;
    if (editorjsData !== undefined) updates.editorjs_data = editorjsData;

    const [content] = await db.update(workspacesTable).set({
        updated_at: sql`NOW()`,
        editorjs_data: editorjsData,
        excalidraw_data: excalidrawData
    }).where(eq(workspacesTable.id,workspaceId)).returning();
    
    // `
    //   UPDATE workspace_content 
    //   SET ${sql(updates)}
    //   WHERE workspace_id = ${workspaceId}
    //   RETURNING *
    // `;
    return content;
  },

  async deleteWorkspace(workspaceId:string,userId:string){
    const [deleted] = await db.delete(workspacesTable).where(and(eq(workspacesTable.id,workspaceId),eq(workspacesTable.user_id,userId))).returning();
    return deleted;

  },

  async getProcessedFiles(workspaceId: string) {
    return await db.select().from(processedFilesTable).where(eq(workspacesTable.id,workspaceId))
    .orderBy(desc(workspacesTable.updated_at))
    
    // `
    //   SELECT * FROM processed_files 
    //   WHERE workspace_id = ${workspaceId}
    //   ORDER BY processed_at DESC
    // `;
  },

  async addProcessedFile(workspaceId: string, filename: string, fileSize: number, mimeType: string) {
    const collectionName = `workspace_${workspaceId.replace(/-/g, '_')}`;
    
    const [file] = await db.insert(processedFilesTable).values({workspace_id:workspaceId,file_size:fileSize,filename,mime_type:mimeType,qdrant_collection_name:collectionName}).returning();
    
    // sql`
    //   INSERT INTO processed_files (workspace_id, filename, file_size, mime_type, qdrant_collection_name, vector_count)
    //   VALUES (${workspaceId}, ${filename}, ${fileSize}, ${mimeType}, ${collectionName}, ${vectorCount})
    //   RETURNING *
    // `;
    return file;
  },

  async deleteProcessedFile(id: string, workspaceId: string) {
    const [deleted] = await db.delete(processedFilesTable).where(and(eq(processedFilesTable.id,id),eq(processedFilesTable.workspace_id,workspaceId))).returning();
    
    // sql`
    //   DELETE FROM processed_files 
    //   WHERE id = ${id} AND workspace_id = ${workspaceId}
    //   RETURNING *
    // `;
    return deleted;
  }
};