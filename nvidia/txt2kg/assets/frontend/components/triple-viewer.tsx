"use client"

import { useState, useEffect, useRef } from "react"
import { useDocuments } from "@/contexts/document-context"
import type { Triple } from "@/utils/text-processing"
import { Pencil, Trash2, Plus, Download, ChevronDown, FileJson, FileText, List, Network, Check, X, Database } from "lucide-react"
import { TripleEditor } from "./triple-editor"

// Add this new EntityEditor component before the TripleViewer component
interface EntityEditorProps {
  entity: string
  onSave: (oldEntity: string, newEntity: string) => void
  onCancel: () => void
}

function EntityEditor({ entity, onSave, onCancel }: EntityEditorProps) {
  const [newEntityName, setNewEntityName] = useState(entity)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (newEntityName.trim()) {
      onSave(entity, newEntityName.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-muted/20 border-b border-border">
      <div className="mb-3">
        <label htmlFor="entity" className="block text-xs text-muted-foreground mb-1">
          Entity Name
        </label>
        <input
          id="entity"
          type="text"
          value={newEntityName}
          onChange={(e) => setNewEntityName(e.target.value)}
          className="w-full bg-background border border-border rounded-md p-2 text-sm text-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary"
          placeholder="Entity"
          required
        />
      </div>
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="p-2 text-muted-foreground hover:text-foreground rounded-full hover:bg-muted/30"
        >
          <X className="h-4 w-4" />
        </button>
        <button type="submit" className="p-2 text-primary hover:text-primary/80 rounded-full hover:bg-primary/10">
          <Check className="h-4 w-4" />
        </button>
      </div>
    </form>
  )
}

export function TripleViewer() {
  const { documents, addTriple, editTriple, deleteTriple, updateTriples } = useDocuments()
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)

  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [isAddingTriple, setIsAddingTriple] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [viewMode, setViewMode] = useState<'triples' | 'entities'>('triples')
  const [editingEntityIndex, setEditingEntityIndex] = useState<number | null>(null)
  const [isAddingEntity, setIsAddingEntity] = useState(false)
  const [newEntityName, setNewEntityName] = useState('')
  const [isStoringSingle, setIsStoringSingle] = useState(false)
  const [storeSingleStatus, setStoreSingleStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [isStoringAll, setIsStoringAll] = useState(false)
  const [storeAllStatus, setStoreAllStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Handle click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  const processedDocs = documents.filter((doc) => doc.status === "Processed")
  const selectedDoc = selectedDocId
    ? documents.find((doc) => doc.id === selectedDocId)
    : processedDocs.length > 0
      ? processedDocs[0]
      : null

  // Filter documents based on search query
  const filteredDocs = processedDocs.filter(doc => 
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Extract unique entities from triples
  const getUniqueEntities = () => {
    if (!selectedDoc?.triples) return [];
    
    const entitiesSet = new Set<string>();
    selectedDoc.triples.forEach(triple => {
      if (triple.subject && typeof triple.subject === 'string') {
        entitiesSet.add(triple.subject);
      }
      if (triple.object && typeof triple.object === 'string') {
        entitiesSet.add(triple.object);
      }
    });
    
    return Array.from(entitiesSet).sort();
  };

  const uniqueEntities = getUniqueEntities();

  // Helper function to normalize triple text by removing parentheses and quotes
  const normalizeText = (text: string | null | undefined): string => {
    if (!text || typeof text !== 'string') return '';
    return text.replace(/['"()]/g, '').trim();
  };

  if (processedDocs.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="flex flex-col items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-secondary/50 flex items-center justify-center mb-4">
            <FileText className="h-8 w-8 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground mb-2">No processed documents available</p>
          <p className="text-xs text-muted-foreground max-w-md mx-auto">
            Upload markdown, CSV, or text files and click "Generate Graph" to extract knowledge triples
          </p>
        </div>
      </div>
    )
  }

  const handleSaveTriple = (triple: Triple, index?: number) => {
    if (selectedDoc) {
      if (index !== undefined) {
        editTriple(selectedDoc.id, index, triple)
      } else {
        addTriple(selectedDoc.id, triple)
      }
    }
    setEditingIndex(null)
    setIsAddingTriple(false)
  }

  const handleDeleteTriple = (index: number) => {
    if (selectedDoc) {
      if (confirm("Are you sure you want to delete this triple?")) {
        deleteTriple(selectedDoc.id, index)
      }
    }
  }

  const exportTriplesCSV = () => {
    if (!selectedDoc || !selectedDoc.triples) return

    const tripleCsv = [
      "Subject,Predicate,Object",
      ...selectedDoc.triples.map((t) => `"${normalizeText(t.subject)}","${normalizeText(t.predicate)}","${normalizeText(t.object)}"`),
    ].join("\n")

    const blob = new Blob([tripleCsv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${selectedDoc.name.replace(/\.[^/.]+$/, "")}_triples.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setShowExportMenu(false)
  }

  const exportTriplesJSON = () => {
    if (!selectedDoc || !selectedDoc.triples) return

    // Export the triples in the exact format expected by the graph viewer
    const triplesJSON = JSON.stringify(selectedDoc.triples, null, 2)

    const blob = new Blob([triplesJSON], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${selectedDoc.name.replace(/\.[^/.]+$/, "")}_triples.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setShowExportMenu(false)
  }

  // Export entities list to CSV
  const exportEntitiesCSV = () => {
    if (!uniqueEntities.length) return;

    const entitiesCsv = [
      "Entity",
      ...uniqueEntities.map(entity => `"${normalizeText(entity)}"`),
    ].join("\n");

    const blob = new Blob([entitiesCsv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedDoc?.name.replace(/\.[^/.]+$/, "") || "graph"}_entities.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportMenu(false);
  }

  const handleSaveEntity = (oldEntity: string, newEntity: string) => {
    if (selectedDoc && selectedDoc.triples) {
      // Create new triples array with updated entity names
      const updatedTriples = selectedDoc.triples.map(triple => {
        const updatedTriple = { ...triple };
        
        // Update subject if it matches the old entity name
        if (updatedTriple.subject === oldEntity) {
          updatedTriple.subject = newEntity;
        }
        
        // Update object if it matches the old entity name
        if (updatedTriple.object === oldEntity) {
          updatedTriple.object = newEntity;
        }
        
        return updatedTriple;
      });
      
      // Update the document with the new triples
      updateTriples(selectedDoc.id, updatedTriples);
    }
    
    // Reset editing state
    setEditingEntityIndex(null);
  };

  const handleAddEntity = () => {
    if (!newEntityName.trim() || !selectedDoc) return
    
    // Add a self-referential triple: "entity" is "entity"
    // This is a simple way to add an entity to the graph
    const selfReferentialTriple: Triple = {
      subject: newEntityName.trim(),
      predicate: 'is',
      object: newEntityName.trim()
    }
    
    // Add the new triple to the document
    addTriple(selectedDoc.id, selfReferentialTriple)
    
    // Reset state
    setNewEntityName('')
    setIsAddingEntity(false)
  }

  const handleDeleteEntity = (entity: string) => {
    if (!selectedDoc || !selectedDoc.triples) return;
    
    if (confirm(`Are you sure you want to delete the entity "${entity}"? This will remove all triples containing this entity.`)) {
      // Filter out all triples that contain the entity
      const filteredTriples = selectedDoc.triples.filter(triple => 
        triple.subject !== entity && triple.object !== entity
      );
      
      // Update the document with the filtered triples
      updateTriples(selectedDoc.id, filteredTriples);
    }
  };

  // Function to store triples in the Neo4j database
  const storeInGraphDb = async () => {
    if (!selectedDoc || !selectedDoc.triples || selectedDoc.triples.length === 0) {
      alert("No triples to store in the database");
      return;
    }

    try {
      setIsStoringSingle(true);
      setStoreSingleStatus('loading');

      const response = await fetch('/api/graph-db/triples', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          triples: selectedDoc.triples,
          documentName: selectedDoc.name
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to store triples in the database');
      }

      setStoreSingleStatus('success');
      setTimeout(() => setStoreSingleStatus('idle'), 3000);
    } catch (error) {
      console.error("Error storing triples in graph database:", error);
      setStoreSingleStatus('error');
      alert(error instanceof Error ? error.message : 'An error occurred while storing triples');
    } finally {
      setIsStoringSingle(false);
    }
  };

  // Function to store all triples from all documents in the graph database
  const storeAllTriplesInGraphDb = async () => {
    // Get all documents with triples
    const docsWithTriples = documents.filter(doc => doc.triples && doc.triples.length > 0);

    if (docsWithTriples.length === 0) {
      alert("No documents with triples to store in the database");
      return;
    }

    try {
      setIsStoringAll(true);
      setStoreAllStatus('loading');

      // Collect all triples from all documents
      const allTriples = docsWithTriples.flatMap(doc => doc.triples || []);

      const response = await fetch('/api/graph-db/triples', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          triples: allTriples,
          documentName: 'All Documents'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to store all triples in the database');
      }

      setStoreAllStatus('success');
      setTimeout(() => setStoreAllStatus('idle'), 3000);
    } catch (error) {
      console.error("Error storing all triples in graph database:", error);
      setStoreAllStatus('error');
      alert(error instanceof Error ? error.message : 'An error occurred while storing all triples');
    } finally {
      setIsStoringAll(false);
    }
  };

  return (
    <div className="p-6">
      {/* Header Section - Document Selector and Global Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div className="flex items-center gap-4 relative flex-1" ref={dropdownRef}>
          <label className="text-sm font-semibold text-foreground whitespace-nowrap">Select Document</label>
          <div className="relative flex-1 max-w-md">
            <button
              className="w-full flex items-center justify-between bg-card border border-border rounded-lg p-3 text-foreground text-sm hover:bg-muted/30 transition-colors"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              <span className="truncate">
                {selectedDoc?.name || "Select document"}
              </span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className={`transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>

            {isDropdownOpen && (
              <div className="absolute z-10 mt-1 w-full bg-card border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
                <div className="p-2 sticky top-0 bg-card border-b border-border">
                  <input
                    type="text"
                    className="w-full bg-background border border-border rounded-md p-1.5 text-sm"
                    placeholder="Search documents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
                {filteredDocs.length === 0 ? (
                  <div className="p-2 text-center text-muted-foreground text-sm">
                    No documents found
                  </div>
                ) : (
                  filteredDocs.map((doc) => (
                    <button
                      key={doc.id}
                      className={`w-full text-left p-2 hover:bg-muted/30 text-sm ${
                        doc.id === selectedDoc?.id ? 'bg-primary/10 text-primary' : ''
                      }`}
                      onClick={() => {
                        setSelectedDocId(doc.id)
                        setEditingIndex(null)
                        setIsAddingTriple(false)
                        setIsDropdownOpen(false)
                        setSearchQuery('')
                      }}
                    >
                      {doc.name}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Global Action - Store All Documents */}
        <button
          onClick={storeAllTriplesInGraphDb}
          disabled={isStoringAll || documents.filter(doc => doc.triples && doc.triples.length > 0).length === 0}
          className={`inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium rounded-lg transition-all shadow-sm ${
            storeAllStatus === 'success'
              ? 'bg-green-50 border border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400'
              : storeAllStatus === 'error'
                ? 'bg-red-50 border border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400'
                : 'bg-nvidia-green hover:bg-nvidia-green/90 text-white hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed'
          }`}
        >
          <Database className="h-4 w-4" />
          <span>
            {storeAllStatus === 'loading' ? 'Storing All...' :
             storeAllStatus === 'success' ? 'All Stored!' :
             storeAllStatus === 'error' ? 'Failed' :
             'Store All Documents'}
          </span>
        </button>
      </div>

      {selectedDoc && (
        <>
          {/* Tab Navigation with Stats */}
          <div className="mb-6 border border-border/40 rounded-xl p-4 bg-muted/10">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
              <div className="inline-flex items-center justify-center rounded-xl bg-muted/20 border border-border/15 p-2 shadow-sm backdrop-blur-sm w-fit">
                <button
                  onClick={() => setViewMode('triples')}
                  className={`inline-flex items-center justify-center gap-3 whitespace-nowrap rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200 hover:bg-background/60 ${
                    viewMode === 'triples'
                      ? 'bg-background text-foreground shadow-sm border border-border/20'
                      : 'text-muted-foreground'
                  }`}
                >
                  <div className={`nvidia-build-tab-icon ${viewMode === 'triples' ? 'scale-105' : ''}`}>
                    <List className="h-3 w-3 text-nvidia-green" />
                  </div>
                  <span>Triples</span>
                </button>
                <button
                  onClick={() => setViewMode('entities')}
                  className={`inline-flex items-center justify-center gap-3 whitespace-nowrap rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200 hover:bg-background/60 ${
                    viewMode === 'entities'
                      ? 'bg-background text-foreground shadow-sm border border-border/20'
                      : 'text-muted-foreground'
                  }`}
                >
                  <div className={`nvidia-build-tab-icon ${viewMode === 'entities' ? 'scale-105' : ''}`}>
                    <Network className="h-3 w-3 text-nvidia-green" />
                  </div>
                  <span>Entities</span>
                </button>
              </div>

              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-nvidia-green text-lg">{selectedDoc.triples?.length || 0}</span>
                  <span className="text-xs text-muted-foreground font-medium">Triples</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-nvidia-green text-lg">{uniqueEntities.length}</span>
                  <span className="text-xs text-muted-foreground font-medium">Entities</span>
                </div>
                {selectedDoc.chunkCount && selectedDoc.chunkCount > 1 && (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-medium">
                    {selectedDoc.chunkCount} chunks
                  </span>
                )}
              </div>
            </div>
          </div>



          {/* Action Bar - Document Actions */}
          <div className="flex flex-wrap items-center justify-end gap-2 mb-4">
            <button
              onClick={() => {
                if (viewMode === 'triples') {
                  setIsAddingTriple(true)
                  setEditingIndex(null)
                } else {
                  setIsAddingEntity(true)
                }
              }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-nvidia-green hover:bg-nvidia-green/90 text-white rounded-md transition-all"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Add {viewMode === 'triples' ? 'Triple' : 'Entity'}</span>
            </button>

            {viewMode === 'triples' && (
              <>
                <button
                  onClick={storeInGraphDb}
                  disabled={isStoringSingle || !selectedDoc.triples || selectedDoc.triples.length === 0}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                    storeSingleStatus === 'success'
                      ? 'bg-green-50 border border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400'
                      : storeSingleStatus === 'error'
                        ? 'bg-red-50 border border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400'
                        : 'bg-background border border-border hover:bg-muted/50 text-foreground disabled:opacity-50 disabled:cursor-not-allowed'
                  }`}
                >
                  <Database className="h-3.5 w-3.5" />
                  <span>
                    {storeSingleStatus === 'loading' ? 'Storing...' :
                     storeSingleStatus === 'success' ? 'Stored!' :
                     storeSingleStatus === 'error' ? 'Failed' :
                     'Store Document'}
                  </span>
                </button>

                <div className="relative">
                  <button
                    onClick={() => setShowExportMenu(!showExportMenu)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-background border border-border hover:bg-muted/50 text-foreground rounded-md transition-all"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>Export</span>
                    <ChevronDown className="h-3 w-3" />
                  </button>

                  {showExportMenu && (
                    <div className="absolute right-0 mt-2 w-64 bg-card border border-border rounded-lg shadow-lg z-50 overflow-hidden">
                      <button
                        onClick={exportTriplesJSON}
                        className="w-full text-left px-4 py-3 hover:bg-muted/30 flex items-center gap-3 transition-colors"
                      >
                        <FileJson className="h-4 w-4 text-primary" />
                        <div>
                          <div className="text-sm font-medium">Export as JSON</div>
                          <div className="text-xs text-muted-foreground">For Graph Viewer</div>
                        </div>
                      </button>
                      <button
                        onClick={exportTriplesCSV}
                        className="w-full text-left px-4 py-3 hover:bg-muted/30 flex items-center gap-3 transition-colors"
                      >
                        <FileText className="h-4 w-4 text-primary" />
                        <div>
                          <div className="text-sm font-medium">Export as CSV</div>
                          <div className="text-xs text-muted-foreground">For spreadsheets</div>
                        </div>
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {viewMode === 'triples' ? (
            selectedDoc.triples && selectedDoc.triples.length > 0 ? (
              <div>

                <div className="border border-border rounded-xl overflow-hidden">
                  <div className="flex justify-between items-center p-4 bg-muted/30 border-b border-border">
                    <div className="grid grid-cols-3 gap-4 w-full">
                      <div className="text-sm font-semibold text-muted-foreground">Subject</div>
                      <div className="text-sm font-semibold text-muted-foreground">Predicate</div>
                      <div className="text-sm font-semibold text-muted-foreground">Object</div>
                    </div>
                  </div>

                  {isAddingTriple && (
                    <div className="border-b border-border">
                      <TripleEditor onSave={handleSaveTriple} onCancel={() => setIsAddingTriple(false)} />
                    </div>
                  )}

                  <div className="max-h-96 overflow-y-auto">
                    {selectedDoc.triples.map((triple, index) => (
                      <div key={index} className="border-b border-border last:border-b-0">
                        {editingIndex === index ? (
                          <TripleEditor
                            triple={triple}
                            index={index}
                            onSave={handleSaveTriple}
                            onCancel={() => setEditingIndex(null)}
                          />
                        ) : (
                          <div className="flex justify-between items-center p-4 hover:bg-muted/30 transition-colors">
                            <div className="grid grid-cols-3 gap-4 w-full">
                              <div className="text-sm text-foreground truncate" title={triple.subject}>
                                {normalizeText(triple.subject)}
                              </div>
                              <div className="text-sm text-foreground truncate" title={triple.predicate}>
                                {normalizeText(triple.predicate)}
                              </div>
                              <div className="text-sm text-foreground truncate" title={triple.object}>
                                {normalizeText(triple.object)}
                              </div>
                            </div>
                            <div className="flex items-center gap-1 ml-2">
                              <button
                                onClick={() => setEditingIndex(index)}
                                className="p-1.5 text-muted-foreground hover:text-foreground rounded-full hover:bg-muted/50 transition-colors"
                                title="Edit Triple"
                              >
                                <Pencil className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeleteTriple(index)}
                                className="p-1.5 text-muted-foreground hover:text-destructive rounded-full hover:bg-destructive/10 transition-colors"
                                title="Delete Triple"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center border border-border rounded-xl">
                <div className="flex flex-col items-center justify-center">
                  <p className="text-muted-foreground mb-2">No triples found in this document</p>
                  <p className="text-xs text-muted-foreground mb-6">
                    Try regenerating the graph or add triples manually
                  </p>
                  <button
                    onClick={() => setIsAddingTriple(true)}
                    className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium bg-nvidia-green hover:bg-nvidia-green/90 text-white rounded-lg transition-all shadow-sm hover:shadow-md"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add First Triple</span>
                  </button>
                </div>
              </div>
            )
          ) : (
            // Entities View
            <div>
              {isAddingEntity && (
                <div className="mb-6 p-4 bg-muted/20 border border-border rounded-lg">
                  <div className="mb-3">
                    <label htmlFor="newEntity" className="block text-sm font-medium text-foreground mb-2">
                      New Entity Name
                    </label>
                    <div className="flex gap-3">
                      <input
                        id="newEntity"
                        type="text"
                        value={newEntityName}
                        onChange={(e) => setNewEntityName(e.target.value)}
                        className="flex-1 bg-background border border-border rounded-lg p-3 text-sm text-foreground focus:ring-2 focus:ring-nvidia-green/50 focus:border-nvidia-green transition-colors"
                        placeholder="Enter entity name"
                      />
                      <button 
                        onClick={handleAddEntity}
                        disabled={!newEntityName.trim()}
                        className="inline-flex items-center gap-2 px-4 py-3 text-sm font-medium bg-nvidia-green hover:bg-nvidia-green/90 text-white rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Plus className="h-4 w-4" />
                        <span>Add</span>
                      </button>
                      <button 
                        onClick={() => {
                          setIsAddingEntity(false)
                          setNewEntityName('')
                        }}
                        className="p-3 text-muted-foreground hover:text-foreground rounded-lg hover:bg-muted/30 transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {uniqueEntities.length > 0 ? (
                <div className="border border-border rounded-xl overflow-hidden">
                  <div className="flex justify-between items-center p-4 bg-card border-b border-border">
                    <div className="text-sm font-medium text-muted-foreground">Entity</div>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {uniqueEntities.map((entity, index) => (
                      <div key={index} className="border-b border-border last:border-b-0">
                        {editingEntityIndex === index ? (
                          <EntityEditor
                            entity={entity}
                            onSave={handleSaveEntity}
                            onCancel={() => setEditingEntityIndex(null)}
                          />
                        ) : (
                          <div className="flex justify-between items-center p-4 hover:bg-muted/20">
                            <div className="text-sm text-foreground truncate" title={entity}>
                              {normalizeText(entity)}
                            </div>
                            <div className="flex items-center gap-1 ml-2">
                              <button
                                onClick={() => setEditingEntityIndex(index)}
                                className="p-1.5 text-muted-foreground hover:text-foreground rounded-full hover:bg-muted/30"
                                title="Edit Entity"
                              >
                                <Pencil className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeleteEntity(entity)}
                                className="p-1.5 text-muted-foreground hover:text-destructive rounded-full hover:bg-destructive/10"
                                title="Delete Entity"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center border border-border rounded-xl">
                  <div className="flex flex-col items-center justify-center">
                    <p className="text-muted-foreground mb-2">No entities found</p>
                    <p className="text-xs text-muted-foreground">
                      Add triples to create entities in the knowledge graph
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

