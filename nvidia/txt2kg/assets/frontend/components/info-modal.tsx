"use client"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Info, ExternalLink } from "lucide-react"

export function InfoModal() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="group">
          <Info className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Text to Knowledge Graph</DialogTitle>
          <DialogDescription asChild>
            <div className="text-base leading-relaxed pt-4 space-y-4">
              <p>
                Transform unstructured text into structured knowledge graphs using AI-powered triple extraction.
                This NVIDIA Spark playbook automatically identifies entities and relationships from your documents,
                then visualizes them as interactive 2D or 3D graphs powered by ArangoDB and advanced language models.
              </p>
              <p className="text-sm text-muted-foreground">
                Extract subject-predicate-object triples, perform graph-based queries, and explore your data through
                multiple visualization modes including traditional graph search and vector-enhanced semantic search.
              </p>
            </div>
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-3 pt-4">
          <a
            href="https://build.nvidia.com/spark/txt2kg"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-nvidia-green text-black font-semibold rounded-lg hover:bg-nvidia-green/90 transition-colors"
          >
            View on NVIDIA Spark
            <ExternalLink className="h-4 w-4" />
          </a>
          <p className="text-xs text-center text-muted-foreground">
            Part of the NVIDIA Spark Playbooks collection
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
} 