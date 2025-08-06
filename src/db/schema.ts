import { integer, jsonb, pgTable, text, timestamp, uuid, varchar } from "drizzle-orm/pg-core";

export const usersTable = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  password_hash: varchar("password_hash", { length: 255 }).notNull(),
  name: varchar("name", { length: 255 }).notNull(),
  created_at: timestamp("created_at").defaultNow(),
  updated_at: timestamp("updated_at").defaultNow(),
})

//       CREATE TABLE IF NOT EXISTS workspaces (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
//         name VARCHAR(255) NOT NULL,
//         description TEXT,
//         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         CONSTRAINT unique_user_workspace_name UNIQUE(user_id, name)
//       )
//     `;
export const workspacesTable = pgTable("workspaces", {
  id: uuid("id").primaryKey().defaultRandom(),
  user_id: uuid("user_id").references(() => usersTable.id,{onDelete: "cascade"}).notNull(),
  name: varchar("name", { length: 255 }).notNull(),
  description: text("description"),
  created_at: timestamp("created_at").defaultNow(),
  updated_at: timestamp("updated_at").defaultNow(),
  excalidraw_data: jsonb("excalidraw_data").default(null),
  editorjs_data: jsonb("editorjs_data").default(null),
})

//     // Create processed_files table
//     await db`
//       CREATE TABLE IF NOT EXISTS processed_files (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
//         filename VARCHAR(255) NOT NULL,
//         file_size INTEGER NOT NULL,
//         mime_type VARCHAR(100) NOT NULL,
//         qdrant_collection_name VARCHAR(255) NOT NULL,
//         vector_count INTEGER DEFAULT 0,
//         processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
//       )
//     `;
export const processedFilesTable = pgTable("processed_files", {
  id: uuid("id").primaryKey().defaultRandom(),
  workspace_id: uuid("workspace_id").references(() => workspacesTable.id,{onDelete: "cascade"}).notNull(),
  filename: varchar("filename", { length: 255 }).notNull(),
  file_size: integer("file_size").notNull(),
  mime_type: varchar("mime_type", { length: 100 }).notNull(),
  qdrant_collection_name: varchar("qdrant_collection_name", { length: 255 }).notNull(),
  // vector_count: integer("vector_count").default(0),
  processed_at: timestamp("processed_at").defaultNow(),
})

// async function migrate() {
//   try {
//     console.log('Starting database migration...');

//     // Create users table
//     await db`
//       CREATE TABLE IF NOT EXISTS users (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         email VARCHAR(255) UNIQUE NOT NULL,
//         password_hash VARCHAR(255) NOT NULL,
//         name VARCHAR(255) NOT NULL,
//         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
//       )
//     `;

//     // Create workspaces table
//     await db`
//       CREATE TABLE IF NOT EXISTS workspaces (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
//         name VARCHAR(255) NOT NULL,
//         description TEXT,
//         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         CONSTRAINT unique_user_workspace_name UNIQUE(user_id, name)
//       )
//     `;

//     // Create workspace_content table
//     await db`
//       CREATE TABLE IF NOT EXISTS workspace_content (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
//         excalidraw_data JSONB,
//         editorjs_data JSONB,
//         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         CONSTRAINT unique_workspace_content UNIQUE(workspace_id)
//       )
//     `;

//     // Create processed_files table
//     await db`
//       CREATE TABLE IF NOT EXISTS processed_files (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
//         filename VARCHAR(255) NOT NULL,
//         file_size INTEGER NOT NULL,
//         mime_type VARCHAR(100) NOT NULL,
//         qdrant_collection_name VARCHAR(255) NOT NULL,
//         vector_count INTEGER DEFAULT 0,
//         processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
//       )
//     `;

//     // Create ai_conversations table
//     await db`
//       CREATE TABLE IF NOT EXISTS ai_conversations (
//         id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//         workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
//         user_message TEXT NOT NULL,
//         ai_response TEXT NOT NULL,
//         model_used VARCHAR(100) NOT NULL,
//         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
//       )
//     `;

//     // Create indexes for better performance
//     await db`CREATE INDEX IF NOT EXISTS idx_workspaces_user_id ON workspaces(user_id)`;
//     await db`CREATE INDEX IF NOT EXISTS idx_workspace_content_workspace_id ON workspace_content(workspace_id)`;
//     await db`CREATE INDEX IF NOT EXISTS idx_processed_files_workspace_id ON processed_files(workspace_id)`;
//     await db`CREATE INDEX IF NOT EXISTS idx_ai_conversations_workspace_id ON ai_conversations(workspace_id)`;
//     await db`CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_at ON ai_conversations(created_at)`;

//     // Create updated_at trigger function
//     await db`
//       CREATE OR REPLACE FUNCTION update_updated_at_column()
//       RETURNS TRIGGER AS $$
//       BEGIN
//         NEW.updated_at = CURRENT_TIMESTAMP;
//         RETURN NEW;
//       END;
//       $$ language 'plpgsql'
//     `;

//     // Add triggers for updated_at
//     await db`
//       DROP TRIGGER IF EXISTS update_users_updated_at ON users;
//       CREATE TRIGGER update_users_updated_at 
//         BEFORE UPDATE ON users 
//         FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
//     `;

//     await db`
//       DROP TRIGGER IF EXISTS update_workspaces_updated_at ON workspaces;
//       CREATE TRIGGER update_workspaces_updated_at 
//         BEFORE UPDATE ON workspaces 
//         FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
//     `;

//     await db`
//       DROP TRIGGER IF EXISTS update_workspace_content_updated_at ON workspace_content;
//       CREATE TRIGGER update_workspace_content_updated_at 
//         BEFORE UPDATE ON workspace_content 
//         FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
//     `;

//     console.log('Database migration completed successfully!');
    
//     // Test database connection
//     const result = await db`SELECT COUNT(*) as table_count 
//       FROM information_schema.tables 
//       WHERE table_schema = 'public' 
//       AND table_name IN ('users', 'workspaces', 'workspace_content', 'processed_files', 'ai_conversations')`;
    
//     console.log(`Created ${result[0]?.table_count} tables successfully`);
    
//   } catch (error) {
//     console.error('Migration failed:', error);
//     throw error;
//   } finally {
//     await db.end();
//   }
// }

// // Run migration if this file is executed directly
// if (import.meta.main) {
//   migrate()
//     .then(() => {
//       console.log('Migration script completed');
//       process.exit(0);
//     })
//     .catch((error) => {
//       console.error('Migration script failed:', error);
//       process.exit(1);
//     });
// }

// export { migrate };