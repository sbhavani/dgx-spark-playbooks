"use client"

import React, { useState, useEffect } from "react"
import { 
  Settings, 
  Database, 
  Save, 
  Eye,
  EyeOff,
  Search as SearchIcon,
  Cpu,
  HardDrive,
  Server,
  RefreshCw,
  Check,
  X
} from "lucide-react"
import { GraphDBType } from "@/lib/graph-db-service"
import { listFilesInS3 } from "@/utils/s3-storage"
import { useToast } from "@/hooks/use-toast"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export function SettingsModal() {
  const { toast } = useToast()
  const [isOpen, setIsOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("models")
  const [dbUrl, setDbUrl] = useState("")
  const [dbUsername, setDbUsername] = useState("")
  const [dbPassword, setDbPassword] = useState("")
  const [vectorDbHost, setVectorDbHost] = useState("")
  const [vectorDbPort, setVectorDbPort] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  
  // Graph DB settings
  const [graphDbType, setGraphDbType] = useState<GraphDBType>("arangodb")
  const [neo4jUrl, setNeo4jUrl] = useState("")
  const [neo4jUser, setNeo4jUser] = useState("")
  const [neo4jPassword, setNeo4jPassword] = useState("")
  const [arangoUrl, setArangoUrl] = useState("http://localhost:8529")
  const [arangoDb, setArangoDb] = useState("txt2kg")
  const [arangoUser, setArangoUser] = useState("")
  const [arangoPassword, setArangoPassword] = useState("")
  
  // Vector DB settings - changed from Milvus to Pinecone
  const [pineconeApiKey, setPineconeApiKey] = useState("")
  const [pineconeEnvironment, setPineconeEnvironment] = useState("")
  const [pineconeIndex, setPineconeIndex] = useState("")
  
  // S3 Storage settings
  const [s3Endpoint, setS3Endpoint] = useState("")
  const [s3Bucket, setS3Bucket] = useState("")
  const [s3AccessKey, setS3AccessKey] = useState("")
  const [s3SecretKey, setS3SecretKey] = useState("")
  const [isConnecting, setIsConnecting] = useState(false)
  const [isS3Connected, setIsS3Connected] = useState(false)
  const [s3FileCount, setS3FileCount] = useState(0)
  const [s3Error, setS3Error] = useState<string | null>(null)
  
  // Embeddings model settings
  const [embeddingsProvider, setEmbeddingsProvider] = useState("local")
  const [nvidiaEmbeddingsModel, setNvidiaEmbeddingsModel] = useState("nvidia/llama-3.2-nv-embedqa-1b-v2")
  
  // Ollama model configuration
  const [availableOllamaModels, setAvailableOllamaModels] = useState<string[]>([])
  const [selectedOllamaModels, setSelectedOllamaModels] = useState<string[]>([])
  const [isLoadingOllamaModels, setIsLoadingOllamaModels] = useState(false)
  const [ollamaConnectionStatus, setOllamaConnectionStatus] = useState<'idle' | 'connected' | 'error'>('idle')
  const [ollamaError, setOllamaError] = useState<string | null>(null)
  
  // Listen for open-settings event
  useEffect(() => {
    const handleOpenSettings = (event: CustomEvent) => {
      const { tab } = event.detail
      setIsOpen(true)
      if (tab) {
        setActiveTab(tab)
      }
    }
    
    window.addEventListener('open-settings', handleOpenSettings as EventListener)
    
    return () => {
      window.removeEventListener('open-settings', handleOpenSettings as EventListener)
    }
  }, [])
  
  // Automatically fetch Ollama models when modal opens and models tab is active
  useEffect(() => {
    if (isOpen && activeTab === "models" && ollamaConnectionStatus === 'idle') {
      fetchOllamaModels()
    }
  }, [isOpen, activeTab])
  
  // Load saved settings when modal opens
  useEffect(() => {
    if (isOpen) {
      const storedDbUrl = localStorage.getItem("NEO4J_URL") || ""
      const storedDbUsername = localStorage.getItem("NEO4J_USERNAME") || ""
      const storedDbPassword = localStorage.getItem("NEO4J_PASSWORD") || ""
      const storedVectorDbHost = localStorage.getItem("VECTOR_DB_HOST") || ""
      const storedVectorDbPort = localStorage.getItem("VECTOR_DB_PORT") || ""
      
      setDbUrl(storedDbUrl)
      setDbUsername(storedDbUsername)
      setDbPassword(storedDbPassword)
      setVectorDbHost(storedVectorDbHost)
      setVectorDbPort(storedVectorDbPort)
      
      // Load embeddings settings
      const storedEmbeddingsProvider = localStorage.getItem("embeddings_provider") || "local"
      const storedNvidiaModel = localStorage.getItem("nvidia_embeddings_model") || "nvidia/llama-3.2-nv-embedqa-1b-v2"
      setEmbeddingsProvider(storedEmbeddingsProvider)
      setNvidiaEmbeddingsModel(storedNvidiaModel)
      
      // Load Ollama model configuration
      const storedSelectedModels = localStorage.getItem("selected_ollama_models")
      if (storedSelectedModels) {
        try {
          setSelectedOllamaModels(JSON.parse(storedSelectedModels))
        } catch (e) {
          console.error("Error parsing stored Ollama models:", e)
        }
      }
      
      // Load S3 settings
      const savedS3Endpoint = localStorage.getItem("S3_ENDPOINT") || ""
      const savedS3Bucket = localStorage.getItem("S3_BUCKET") || ""
      const savedS3AccessKey = localStorage.getItem("S3_ACCESS_KEY") || ""
      const savedS3SecretKey = localStorage.getItem("S3_SECRET_KEY") || ""
      const s3Connected = localStorage.getItem("S3_CONNECTED") === "true"
      
      setS3Endpoint(savedS3Endpoint)
      setS3Bucket(savedS3Bucket)
      setS3AccessKey(savedS3AccessKey)
      setS3SecretKey(savedS3SecretKey)
      setIsS3Connected(s3Connected)
    }
    
    // Load graph DB type
    const storedGraphDbType = localStorage.getItem("graph_db_type") || "arangodb"
    setGraphDbType(storedGraphDbType as GraphDBType)
    
    // Load Neo4j settings
    setNeo4jUrl(localStorage.getItem("neo4j_url") || "")
    setNeo4jUser(localStorage.getItem("neo4j_user") || "")
    setNeo4jPassword(localStorage.getItem("neo4j_password") || "")
    
    // Load ArangoDB settings
    setArangoUrl(localStorage.getItem("arango_url") || "http://localhost:8529")
    setArangoDb(localStorage.getItem("arango_db") || "txt2kg")
    setArangoUser(localStorage.getItem("arango_user") || "")
    setArangoPassword(localStorage.getItem("arango_password") || "")
    
    setPineconeApiKey(localStorage.getItem("pinecone_api_key") || "")
    setPineconeEnvironment(localStorage.getItem("pinecone_environment") || "")
    setPineconeIndex(localStorage.getItem("pinecone_index") || "")
  }, [isOpen])
  
  // Save all settings
  const saveSettings = async (e: React.FormEvent) => {
    e.preventDefault()

    let successMessage = ""

    // Save based on active tab
    if (activeTab === "graph") {
      localStorage.setItem("graph_db_type", graphDbType)
      localStorage.setItem("neo4j_url", neo4jUrl)
      localStorage.setItem("neo4j_user", neo4jUser)
      localStorage.setItem("neo4j_password", neo4jPassword)
      localStorage.setItem("arango_url", arangoUrl)
      localStorage.setItem("arango_db", arangoDb)
      localStorage.setItem("arango_user", arangoUser)
      localStorage.setItem("arango_password", arangoPassword)

      try {
        await fetch('/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            settings: {
              graph_db_type: graphDbType,
              neo4j_url: neo4jUrl,
              neo4j_user: neo4jUser,
              neo4j_password: neo4jPassword,
              arango_url: arangoUrl,
              arango_db: arangoDb,
              arango_user: arangoUser,
              arango_password: arangoPassword
            }
          }),
        });
      } catch (error) {
        console.error('Error syncing settings:', error);
      }
      successMessage = "Graph database settings saved"
    } else if (activeTab === "vectordb") {
      localStorage.setItem("pinecone_api_key", pineconeApiKey)
      localStorage.setItem("pinecone_environment", pineconeEnvironment)
      localStorage.setItem("pinecone_index", pineconeIndex)

      try {
        await fetch('/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            settings: {
              pinecone_api_key: pineconeApiKey,
              pinecone_environment: pineconeEnvironment,
              pinecone_index: pineconeIndex,
            }
          }),
        });
      } catch (error) {
        console.error('Error syncing settings:', error);
      }
      successMessage = "Vector database settings saved"
    } else if (activeTab === "s3") {
      setIsConnecting(true)
      setS3Error(null)

      try {
        localStorage.setItem("S3_ENDPOINT", s3Endpoint)
        localStorage.setItem("S3_BUCKET", s3Bucket)
        localStorage.setItem("S3_ACCESS_KEY", s3AccessKey)
        localStorage.setItem("S3_SECRET_KEY", s3SecretKey)

        window.process = window.process || {}
        window.process.env = window.process.env || {}
        window.process.env.S3_ENDPOINT = s3Endpoint
        window.process.env.S3_BUCKET = s3Bucket
        window.process.env.S3_ACCESS_KEY = s3AccessKey
        window.process.env.S3_SECRET_KEY = s3SecretKey

        const files = await listFilesInS3()
        setS3FileCount(files.length)
        setIsS3Connected(true)
        localStorage.setItem("S3_CONNECTED", "true")

        window.dispatchEvent(new CustomEvent('s3ConnectionChanged', {
          detail: { isConnected: true }
        }))

        successMessage = `Connected to S3. Found ${files.length} files.`
      } catch (error) {
        console.error("Failed to connect to S3:", error)
        setIsS3Connected(false)
        localStorage.setItem("S3_CONNECTED", "false")

        window.dispatchEvent(new CustomEvent('s3ConnectionChanged', {
          detail: { isConnected: false }
        }))

        setS3Error(error instanceof Error ? error.message : "Could not connect to S3 storage")
        toast({
          variant: "destructive",
          title: "S3 Connection Failed",
          description: error instanceof Error ? error.message : "Unknown error"
        })
        setIsConnecting(false)
        return
      } finally {
        setIsConnecting(false)
      }
    } else if (activeTab === "embeddings") {
      localStorage.setItem("embeddings_provider", embeddingsProvider);

      if (embeddingsProvider === "nvidia") {
        localStorage.setItem("nvidia_embeddings_model", nvidiaEmbeddingsModel);
      }

      process.env.EMBEDDINGS_PROVIDER = embeddingsProvider;

      if (embeddingsProvider === "nvidia") {
        process.env.NVIDIA_EMBEDDINGS_MODEL = nvidiaEmbeddingsModel;
      }

      try {
        import("@/lib/embeddings").then(({ EmbeddingsService }) => {
          EmbeddingsService.reset();
          console.log("EmbeddingsService reset successfully");

          if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('embeddings-settings-changed'));
          }
        });
      } catch (error) {
        console.error("Error resetting EmbeddingsService:", error);
      }

      successMessage = "Embeddings settings saved"
    } else if (activeTab === "models") {
      localStorage.setItem("selected_ollama_models", JSON.stringify(selectedOllamaModels))

      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('ollama-models-updated', {
          detail: { selectedModels: selectedOllamaModels }
        }))
      }

      successMessage = "Ollama model settings saved"
    }

    toast({
      title: "Success",
      description: successMessage
    });
  }

  
  // Fetch available Ollama models
  const fetchOllamaModels = async () => {
    setIsLoadingOllamaModels(true)
    setOllamaError(null)
    
    try {
      const response = await fetch('/api/ollama?action=test-connection')
      const data = await response.json()
      
      if (data.connected && data.models) {
        setAvailableOllamaModels(data.models)
        setOllamaConnectionStatus('connected')
        
        // If no models are selected yet, select all by default
        if (selectedOllamaModels.length === 0) {
          setSelectedOllamaModels(data.models)
        }
      } else {
        setOllamaConnectionStatus('error')
        setOllamaError(data.error || 'Failed to connect to Ollama')
        setAvailableOllamaModels([])
      }
    } catch (error) {
      console.error('Error fetching Ollama models:', error)
      setOllamaConnectionStatus('error')
      setOllamaError(error instanceof Error ? error.message : 'Unknown error')
      setAvailableOllamaModels([])
    } finally {
      setIsLoadingOllamaModels(false)
    }
  }

  // Toggle Ollama model selection
  const toggleOllamaModel = (modelName: string) => {
    setSelectedOllamaModels(prev => {
      if (prev.includes(modelName)) {
        return prev.filter(m => m !== modelName)
      } else {
        return [...prev, modelName]
      }
    })
  }
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <button className="flex items-center justify-center gap-2 p-2 hover:bg-primary/10 rounded-full transition-colors" title="Settings">
          <Settings className="h-5 w-5 text-muted-foreground hover:text-primary transition-colors" />
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-5xl max-h-[85vh] p-0 gap-0 bg-background border-border flex flex-col">
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-border/10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-nvidia-green/15 flex items-center justify-center">
              <Settings className="h-5 w-5 text-nvidia-green" />
            </div>
            <div>
              <DialogTitle className="text-2xl font-semibold text-foreground">
                Settings
              </DialogTitle>
              <DialogDescription className="text-sm text-muted-foreground mt-1">
                Configure your API keys and database connections
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={saveSettings} className="flex flex-col flex-1 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-1 overflow-hidden">
          <TabsList className="flex-col h-full w-56 rounded-none bg-muted/30 p-2 space-y-1 justify-start border-r border-border/40">
            <TabsTrigger
              value="graph"
              className="w-full justify-start gap-3 data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              <Database className="h-4 w-4" />
              Graph Database
            </TabsTrigger>
            <TabsTrigger
              value="vectordb"
              className="w-full justify-start gap-3 data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              <SearchIcon className="h-4 w-4" />
              Vector Database
            </TabsTrigger>
            <TabsTrigger
              value="s3"
              className="w-full justify-start gap-3 data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              <HardDrive className="h-4 w-4" />
              S3 Storage
            </TabsTrigger>
            <TabsTrigger
              value="embeddings"
              className="w-full justify-start gap-3 data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              <Cpu className="h-4 w-4" />
              Embeddings
            </TabsTrigger>
            <TabsTrigger
              value="models"
              className="w-full justify-start gap-3 data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              <Server className="h-4 w-4" />
              Model Management
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-y-auto bg-muted/10">
            <TabsContent value="graph" className="mt-0 p-6 space-y-4">
              <div className="bg-card rounded-lg border border-border/40 p-5 space-y-4">
                <div className="space-y-3">
                  <label className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Database className="h-4 w-4 text-nvidia-green" />
                    Database Type
                  </label>
                  <select
                    value={graphDbType}
                    onChange={(e) => setGraphDbType(e.target.value as GraphDBType)}
                    className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                  >
                    <option value="neo4j">Neo4j</option>
                    <option value="arangodb">ArangoDB</option>
                  </select>
                </div>
              
                {graphDbType === "neo4j" && (
                  <div className="bg-background/50 rounded-lg p-3 space-y-3">
                    <h4 className="text-sm font-medium text-foreground mb-2">Neo4j Configuration</h4>
                    <div className="grid grid-cols-1 gap-3">
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Connection URL</label>
                        <input
                          type="text"
                          value={neo4jUrl}
                          onChange={(e) => setNeo4jUrl(e.target.value)}
                          placeholder="bolt://localhost:7687"
                          className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs font-medium text-muted-foreground mb-1 block">Username</label>
                          <input
                            type="text"
                            value={neo4jUser}
                            onChange={(e) => setNeo4jUser(e.target.value)}
                            placeholder="neo4j"
                            className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                          />
                        </div>
                        <div>
                          <label className="text-xs font-medium text-muted-foreground mb-1 block">Password</label>
                          <div className="relative">
                            <input
                              type={showPassword ? "text" : "password"}
                              value={neo4jPassword}
                              onChange={(e) => setNeo4jPassword(e.target.value)}
                              placeholder="password"
                              className="w-full bg-background border border-border/60 rounded-md p-2 pr-8 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                            />
                            <button
                              type="button"
                              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeOff className="h-3 w-3" />
                              ) : (
                                <Eye className="h-3 w-3" />
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              
                {graphDbType === "arangodb" && (
                  <div className="bg-background/50 rounded-lg p-3 space-y-3">
                    <h4 className="text-sm font-medium text-foreground mb-2">ArangoDB Configuration</h4>
                    <div className="grid grid-cols-1 gap-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs font-medium text-muted-foreground mb-1 block">Connection URL</label>
                          <input
                            type="text"
                            value={arangoUrl}
                            onChange={(e) => setArangoUrl(e.target.value)}
                            placeholder="http://localhost:8529"
                            className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                          />
                        </div>
                        <div>
                          <label className="text-xs font-medium text-muted-foreground mb-1 block">Database Name</label>
                          <input
                            type="text"
                            value={arangoDb}
                            onChange={(e) => setArangoDb(e.target.value)}
                            placeholder="txt2kg"
                            className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs font-medium text-muted-foreground mb-1 block">Username</label>
                          <input
                            type="text"
                            value={arangoUser}
                            onChange={(e) => setArangoUser(e.target.value)}
                            placeholder="root"
                            className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                          />
                        </div>
                        <div>
                          <label className="text-xs font-medium text-muted-foreground mb-1 block">Password</label>
                          <div className="relative">
                            <input
                              type={showPassword ? "text" : "password"}
                              value={arangoPassword}
                              onChange={(e) => setArangoPassword(e.target.value)}
                              placeholder="password"
                              className="w-full bg-background border border-border/60 rounded-md p-2 pr-8 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                            />
                            <button
                              type="button"
                              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeOff className="h-3 w-3" />
                              ) : (
                                <Eye className="h-3 w-3" />
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="vectordb" className="mt-0 p-6">
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <SearchIcon className="h-4 w-4 text-nvidia-green" />
                    Pinecone Configuration
                  </label>
                </div>
                
                <div className="bg-background/50 rounded-lg p-3 space-y-3">
                  <div className="grid grid-cols-1 gap-3">
                    <div>
                      <label className="text-xs font-medium text-muted-foreground mb-1 block">API Key</label>
                      <input
                        type="password"
                        value={pineconeApiKey}
                        onChange={(e) => setPineconeApiKey(e.target.value)}
                        placeholder="Enter your Pinecone API key"
                        className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Environment</label>
                        <input
                          type="text"
                          value={pineconeEnvironment}
                          onChange={(e) => setPineconeEnvironment(e.target.value)}
                          placeholder="us-west1-gcp"
                          className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Index Name</label>
                        <input
                          type="text"
                          value={pineconeIndex}
                          onChange={(e) => setPineconeIndex(e.target.value)}
                          placeholder="knowledge-graph"
                          className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="s3" className="mt-0 p-6">
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <HardDrive className="h-4 w-4 text-nvidia-green" />
                    S3 Storage Configuration
                  </label>
                </div>
                
                <div className="bg-background/50 rounded-lg p-3 space-y-3">
                  <div className="grid grid-cols-1 gap-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Endpoint URL</label>
                        <Input
                          placeholder="http://localhost:9000"
                          value={s3Endpoint}
                          onChange={(e) => setS3Endpoint(e.target.value)}
                          required
                          className="h-8 text-sm"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Bucket Name</label>
                        <Input
                          placeholder="txt2kg"
                          value={s3Bucket}
                          onChange={(e) => setS3Bucket(e.target.value)}
                          required
                          className="h-8 text-sm"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Access Key</label>
                        <Input
                          placeholder="Access Key ID"
                          value={s3AccessKey}
                          onChange={(e) => setS3AccessKey(e.target.value)}
                          required
                          className="h-8 text-sm"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Secret Key</label>
                        <Input
                          type="password"
                          placeholder="Secret Access Key"
                          value={s3SecretKey}
                          onChange={(e) => setS3SecretKey(e.target.value)}
                          required
                          className="h-8 text-sm"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                {s3Error && (
                  <div className="text-xs text-destructive bg-destructive/10 p-2 rounded-md border border-destructive/30">
                    {s3Error}
                  </div>
                )}
                
                {isS3Connected && (
                  <div className="bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-green-800 dark:text-green-300 text-sm">
                      <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                      <span className="font-medium">Connected</span>
                      <span className="text-green-700 dark:text-green-400 ml-2">
                        {s3FileCount} {s3FileCount === 1 ? 'file' : 'files'} in bucket
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="embeddings" className="mt-0 p-6">
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-nvidia-green" />
                    Embeddings Provider
                  </label>
                </div>
                
                <div className="bg-background/50 rounded-lg p-3 space-y-3">
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1 block">Provider Type</label>
                    <select
                      value={embeddingsProvider}
                      onChange={(e) => setEmbeddingsProvider(e.target.value)}
                      className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                    >
                      <option value="local">Local Sentence Transformer</option>
                      <option value="nvidia">NVIDIA API</option>
                    </select>
                  </div>
                  
                  {embeddingsProvider === "nvidia" && (
                    <div className="space-y-3 pt-3 border-t border-border/30">
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1 block">Model Name</label>
                        <input
                          type="text"
                          value={nvidiaEmbeddingsModel}
                          onChange={(e) => setNvidiaEmbeddingsModel(e.target.value)}
                          placeholder="nvidia/llama-3.2-nv-embedqa-1b-v2"
                          className="w-full bg-background border border-border/60 rounded-md p-2 text-sm text-foreground focus:ring-1 focus:ring-primary/50 focus:border-primary transition-colors"
                        />
                      </div>
                      
                      <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/50 rounded-md p-2">
                        <p className="text-xs text-amber-800 dark:text-amber-300/90 flex items-start gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-3 h-3 mt-0.5 flex-shrink-0 text-amber-600 dark:text-amber-400">
                            <path fillRule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
                          </svg>
                          NVIDIA API key is configured via environment variables
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="models" className="mt-0 p-6">
              <div className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <Server className="h-4 w-4 text-nvidia-green" />
                      Ollama Model Configuration
                    </label>
                    <p className="text-xs text-muted-foreground">
                      Select models for triple extraction dropdown
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={fetchOllamaModels}
                    disabled={isLoadingOllamaModels}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded-md transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <RefreshCw className={`h-3 w-3 ${isLoadingOllamaModels ? 'animate-spin' : ''}`} />
                    {isLoadingOllamaModels ? 'Loading...' : 'Refresh'}
                  </button>
                </div>

                {ollamaConnectionStatus === 'error' && ollamaError && (
                  <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-destructive text-xs">
                      <X className="h-3 w-3 flex-shrink-0" />
                      <span className="font-medium">Connection Error</span>
                    </div>
                    <p className="text-xs text-destructive/90 mt-1">{ollamaError}</p>
                  </div>
                )}

                {ollamaConnectionStatus === 'connected' && (
                  <div className="bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-green-800 dark:text-green-300 text-xs">
                      <Check className="h-3 w-3 flex-shrink-0" />
                      <span className="font-medium">Connected</span>
                      <span className="text-green-700 dark:text-green-400">
                        • {availableOllamaModels.length} model{availableOllamaModels.length !== 1 ? 's' : ''} found
                      </span>
                    </div>
                  </div>
                )}

                {availableOllamaModels.length > 0 && (
                  <div className="bg-background/50 rounded-lg p-3 space-y-3">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <label className="text-xs font-medium text-muted-foreground">Available Models</label>
                          <span className="text-xs text-muted-foreground">
                            {selectedOllamaModels.length} of {availableOllamaModels.length} selected
                          </span>
                        </div>
                        <div className="grid gap-1 max-h-48 overflow-y-auto border border-border/60 rounded-md p-2 bg-background">
                          {availableOllamaModels.map((model) => (
                            <label
                              key={model}
                              className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer transition-colors text-sm"
                            >
                              <input
                                type="checkbox"
                                checked={selectedOllamaModels.includes(model)}
                                onChange={() => toggleOllamaModel(model)}
                                className="h-3 w-3 rounded border-input text-primary focus:ring-1 focus:ring-primary/50"
                              />
                              <Server className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                              <span className="text-xs font-medium text-foreground truncate">{model}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      <div className="flex gap-2 text-xs pt-2 border-t border-border/30">
                        <button
                          type="button"
                          onClick={() => setSelectedOllamaModels(availableOllamaModels)}
                          className="text-primary hover:text-primary/80 transition-colors font-medium"
                        >
                          Select All
                        </button>
                        <span className="text-muted-foreground/50">|</span>
                        <button
                          type="button"
                          onClick={() => setSelectedOllamaModels([])}
                          className="text-primary hover:text-primary/80 transition-colors font-medium"
                        >
                          Select None
                        </button>
                      </div>
                  </div>
                )}

                {availableOllamaModels.length === 0 && ollamaConnectionStatus === 'idle' && (
                  <div className="text-center py-8 bg-muted/20 rounded-lg border border-border/30">
                    <Server className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
                    <p className="text-xs text-muted-foreground">
                      Click "Refresh" to load available models
                    </p>
                  </div>
                )}
              </div>
              </div>
            </TabsContent>
          </div>
          </Tabs>

          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border/10 bg-muted/20 shrink-0">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOpen(false)}
              className="px-4"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isConnecting}
              className="flex items-center gap-2 px-6 bg-nvidia-green hover:bg-nvidia-green/90 text-black font-semibold"
            >
              {isConnecting ? (
                <>
                  <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
} 