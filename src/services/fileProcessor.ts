import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { QdrantClient } from '@qdrant/js-client-rest';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { HuggingFaceInferenceEmbeddings } from "@langchain/community/embeddings/hf";
import { QdrantVectorStore } from "@langchain/qdrant";
import mammoth from 'mammoth';
import * as XLSX from 'xlsx';

const qdrantClient = new QdrantClient({
  url: process.env.QDRANT_URL || 'http://localhost:6333',
});

const embeddingsModel = new HuggingFaceInferenceEmbeddings({
  model: "sentence-transformers/all-MiniLM-l6-v2", // Defaults to `BAAI/bge-base-en-v1.5` if not provided
//   provider: "", // Falls back to auto selection mechanism within Hugging Face's inference API if not provided
});

const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});

interface ProcessFileResult {
  vectorCount: number;
  collectionName: string;
}

class FileProcessor {
  private async ensureCollection(workspaceId: string): Promise<string> {
    const collectionName = `workspace_${workspaceId.replace(/-/g, '_')}`;
    
    try {
      // Check if collection exists
      const collections = await qdrantClient.getCollections();
      const exists = collections.collections?.some(c => c.name === collectionName);
      
      if (!exists) {
        // Create collection with proper vector configuration
        await qdrantClient.createCollection(collectionName, {
          vectors: {
            size: 384, // OpenAI embedding size for text-embedding-3-small
            distance: 'Cosine',
          },
        });
      }
      
      return collectionName;
    } catch (error) {
      console.error('Error ensuring collection:', error);
      throw new Error('Failed to setup vector collection');
    }
  }

  private async extractTextFromFile(file: File) {

    switch (file.type) {
      case 'application/pdf':
        const loader = new PDFLoader(file);
        const docs = await loader.load();
        return docs;

    //   case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
    //     const docxResult = await mammoth.extractRawText({ buffer: uint8Array });
    //     return docxResult.value;

    //   case 'application/msword':
    //     // For older .doc files, mammoth might work but results vary
    //     try {
    //       const docResult = await mammoth.extractRawText({ buffer: uint8Array });
    //       return docResult.value;
    //     } catch {
    //       throw new Error('Unable to process .doc file. Please convert to .docx format.');
    //     }

    //   case 'text/plain':
    //   case 'text/markdown':
    //     return new TextDecoder().decode(uint8Array);

    //   case 'application/vnd.ms-excel':
    //   case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
    //     const workbook = XLSX.read(uint8Array, { type: 'array' });
    //     let excelText = '';
        
    //     workbook.SheetNames.forEach(sheetName => {
    //       const sheet = workbook.Sheets[sheetName];
    //       const sheetData = XLSX.utils.sheet_to_csv(sheet);
    //       excelText += `Sheet: ${sheetName}\n${sheetData}\n\n`;
    //     });
        
    //     return excelText;

      default:
        throw new Error(`Unsupported file type: ${file.type}`);
    }
  }

  async processFile(file: File, workspaceId: string) {
    try {
      // Ensure collection exists
      const collectionName = await this.ensureCollection(workspaceId);
      
      // Extract text from file
      const docs = await this.extractTextFromFile(file);
      
      if (!docs) {
        throw new Error('No document loaded from file');
      }
      // Split text into chunks
      const splits = await textSplitter.splitDocuments(docs)
    if(!splits) {
        throw new Error('No text chunks were created from the documents.');
        
    }      

      // Create embeddings for chunks
      const qdrant = await QdrantVectorStore.fromExistingCollection(
        embeddingsModel,
        {
            collectionName:collectionName,
            url:process.env.QDRANT_URL!
        }
    )
    ;
    
    try{
        await qdrant.addDocuments(splits);
    }catch(err: any){
        throw new Error(`Failed to insert documents to the vector db. Error: ${err.message}`)
    }
    //   const embeddings_results = await embeddings.embedDocuments(splits);
      
      // Prepare points for Qdrant
    //   const points = chunks.map((chunk, index) => ({
    //     id: `${workspaceId}_${file.name}_${Date.now()}_${index}`,
    //     vector: embeddings_results[index],
    //     payload: {
    //       content: chunk,
    //       filename: file.name,
    //       file_type: file.type,
    //       file_size: file.size,
    //       workspace_id: workspaceId,
    //       chunk_index: index,
    //       created_at: new Date().toISOString(),
    //     },
    //   }));

    //   // Insert vectors into Qdrant
    //   await qdrantClient.upsert(collectionName, {
    //     wait: true,
    //     points,
    //   });

      return {
        collectionName,
      };
    } catch (error: any) {
      console.error('File processing error:', error);
      throw new Error(`Failed to process file: ${error.message}`);
    }
  }

  async deleteFileVectors(workspaceId: string, fileId: string): Promise<void> {
    try {
      const collectionName = `workspace_${workspaceId.replace(/-/g, '_')}`;
      
      // Delete points that match the file ID pattern
      await qdrantClient.delete(collectionName, {
        filter: {
          must: [
            {
              key: 'workspace_id',
              match: { value: workspaceId },
            },
          ],
        },
      });
    } catch (error) {
      console.error('Error deleting file vectors:', error);
      // Don't throw error as file might already be deleted from DB
    }
  }

  async deleteWorkspaceCollection(workspaceId: string): Promise<void> {
    try {
      const collectionName = `workspace_${workspaceId.replace(/-/g, '_')}`;
      await qdrantClient.deleteCollection(collectionName);
    } catch (error) {
      console.error('Error deleting workspace collection:', error);
      // Don't throw error as collection might not exist
    }
  }

//   async searchSimilarChunks(workspaceId: string, query: string, limit: number = 5) {
//     try {
//       const collectionName = `workspace_${workspaceId.replace(/-/g, '_')}`;

//       const qdrant = await QdrantVectorStore.fromExistingCollection(
//         embeddingsModel,
//         {
//             collectionName:collectionName,
//             url:process.env.QDRANT_URL!
//         }
//     )
//     const similaritySearchResults = await qdrant.similaritySearch(
//         query,limit,
//       );
//     //   // Create embedding for the query
//     //   const queryEmbedding = await embeddings.embedQuery(query);


      
//     //   // Search in Qdrant
//     //   const searchResult = await qdrantClient.search(collectionName, {
//     //     vector: queryEmbedding,
//     //     limit,
//     //     with_payload: true,
//     //     score_threshold: 0.7, // Minimum similarity threshold
//     //   });

//       return similaritySearchResults.map(result => ({
//         content: result.payload?.content,
//         filename: result.payload?.filename,
//         score: result.score,
//         metadata: {
//           file_type: result.payload?.file_type,
//           chunk_index: result.payload?.chunk_index,
//           created_at: result.payload?.created_at,
//         },
//       }));
//     } catch (error) {
//       console.error('Search error:', error);
//       throw new Error('Failed to search similar content');
//     }
//   }
}

export const fileProcessor = new FileProcessor();