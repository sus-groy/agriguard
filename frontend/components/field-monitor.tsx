"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Map, Scan, RefreshCw, ZoomIn, ZoomOut, Maximize2, Layers } from "lucide-react"

export function FieldMonitor() {
  const [isNirView, setIsNirView] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    try {
      await fetch("/api/analyze-field", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ viewType: isNirView ? "nir" : "standard" }),
      })
    } catch (error) {
      console.error("Analysis failed:", error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <Card className="bg-card border-border">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Map className="h-5 w-5 text-primary" />
              Field Health Map
            </CardTitle>
            <div className="flex items-center gap-2 text-sm">
              <span className={!isNirView ? "text-foreground font-medium" : "text-muted-foreground"}>Standard</span>
              <Switch checked={isNirView} onCheckedChange={setIsNirView} className="data-[state=checked]:bg-primary" />
              <span className={isNirView ? "text-foreground font-medium" : "text-muted-foreground"}>NIR Health</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Map Container */}
          <div className="relative aspect-[3/2] rounded-xl overflow-hidden bg-muted border border-border">
            <img
              src={
                isNirView
                  ? "/placeholder.svg?height=400&width=600&query=NIR infrared thermal agricultural field scan green yellow red zones"
                  : "/placeholder.svg?height=400&width=600&query=aerial drone view agricultural field crops satellite imagery"
              }
              alt={isNirView ? "NIR Health View" : "Standard Field View"}
              className="w-full h-full object-cover transition-opacity duration-500"
            />

            {/* Map Controls */}
            <div className="absolute top-3 right-3 flex flex-col gap-2">
              <Button size="icon" variant="secondary" className="h-10 w-10 bg-card/90 backdrop-blur">
                <ZoomIn className="h-5 w-5" />
              </Button>
              <Button size="icon" variant="secondary" className="h-10 w-10 bg-card/90 backdrop-blur">
                <ZoomOut className="h-5 w-5" />
              </Button>
              <Button size="icon" variant="secondary" className="h-10 w-10 bg-card/90 backdrop-blur">
                <Maximize2 className="h-5 w-5" />
              </Button>
            </div>

            {/* View Type Badge */}
            <div className="absolute top-3 left-3">
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${
                  isNirView ? "bg-chart-3/90 text-card" : "bg-primary/90 text-primary-foreground"
                }`}
              >
                <Layers className="h-4 w-4" />
                {isNirView ? "NIR Health View" : "Standard View"}
              </div>
            </div>

            {/* Legend */}
            {isNirView && (
              <div className="absolute bottom-3 left-3 bg-card/95 backdrop-blur rounded-xl p-3">
                <p className="text-xs font-medium text-foreground mb-2">Health Index</p>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-sm bg-healthy" />
                    <span className="text-xs text-muted-foreground">Healthy</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-sm bg-warning" />
                    <span className="text-xs text-muted-foreground">Stress</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-sm bg-alert" />
                    <span className="text-xs text-muted-foreground">Critical</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="h-14 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
            >
              {isAnalyzing ? <RefreshCw className="h-5 w-5 mr-2 animate-spin" /> : <Scan className="h-5 w-5 mr-2" />}
              {isAnalyzing ? "Analyzing..." : "Analyze Field"}
            </Button>
            <Button variant="outline" className="h-14 font-medium border-2 bg-transparent">
              <RefreshCw className="h-5 w-5 mr-2" />
              Refresh Data
            </Button>
          </div>

          {/* Field Stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-healthy/10 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-healthy">78%</p>
              <p className="text-xs text-muted-foreground">Healthy</p>
            </div>
            <div className="bg-warning/10 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-warning">10%</p>
              <p className="text-xs text-muted-foreground">Stressed</p>
            </div>
            <div className="bg-alert/10 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-alert">12%</p>
              <p className="text-xs text-muted-foreground">Critical</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
