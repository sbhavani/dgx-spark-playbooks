"use client"

import { Network, Zap } from "lucide-react"
import { useDocuments } from "@/contexts/document-context"
import { Loader2 } from "lucide-react"

export function GraphActions() {
  const { documents, processDocuments, isProcessing, openGraphVisualization } = useDocuments()

  const hasNewDocuments = documents.some((doc) => doc.status === "New")
  const hasProcessedDocuments = documents.some(
    (doc) => doc.status === "Processed" && doc.triples && doc.triples.length > 0,
  )

  const handleProcessDocuments = async () => {
    try {
      // Get IDs of documents with "New" status
      const newDocumentIds = documents
        .filter(doc => doc.status === "New")
        .map(doc => doc.id);
        
      if (newDocumentIds.length === 0) {
        console.log("No new documents to process");
        return;
      }
      
      await processDocuments(newDocumentIds, {
        useLangChain: false,
        useGraphTransformer: false,
        promptConfigs: undefined
      });
    } catch (error) {
      console.error('Error processing documents:', error);
    }
  }

  return (
    <div className="flex gap-3 items-center">
      <button
        className={`btn-primary ${!hasNewDocuments || isProcessing ? "opacity-60 cursor-not-allowed" : ""}`}
        disabled={!hasNewDocuments || isProcessing}
        onClick={handleProcessDocuments}
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Zap className="h-4 w-4" />
            Process Documents
          </>
        )}
      </button>
      <button
        className={`btn-primary ${!hasProcessedDocuments || isProcessing ? "opacity-60 cursor-not-allowed" : ""}`}
        disabled={!hasProcessedDocuments || isProcessing}
        onClick={() => openGraphVisualization()}
      >
        <Network className="h-4 w-4" />
        View Knowledge Graph
      </button>
    </div>
  )
}

