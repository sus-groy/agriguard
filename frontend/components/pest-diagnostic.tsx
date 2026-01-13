"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Bug, Camera, Upload, X, Leaf, FlaskConical, CheckCircle2, AlertTriangle, Loader2 } from "lucide-react"

interface DiagnosisResult {
  pest: string
  confidence: number
  treatments: {
    organic: string[]
    chemical: string[]
  }
}

export function PestDiagnostic() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<DiagnosisResult | null>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader()
      reader.onload = () => setUploadedImage(reader.result as string)
      reader.readAsDataURL(file)
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = () => setUploadedImage(reader.result as string)
      reader.readAsDataURL(file)
    }
  }

  const handleDiagnose = async () => {
    if (!uploadedImage) return
    setIsAnalyzing(true)

    try {
      const response = await fetch("/api/diagnose-plant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: uploadedImage }),
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      // Mock result for demo
      setResult({
        pest: "Aphids (Aphidoidea)",
        confidence: 92,
        treatments: {
          organic: [
            "Neem oil spray (2-3 tbsp per gallon)",
            "Ladybug release (1500 per acre)",
            "Garlic-pepper spray",
            "Insecticidal soap application",
          ],
          chemical: ["Imidacloprid 0.5% SL", "Thiamethoxam 25% WG", "Acetamiprid 20% SP"],
        },
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const clearImage = () => {
    setUploadedImage(null)
    setResult(null)
  }

  return (
    <div className="p-4 space-y-4">
      <Card className="bg-card border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Bug className="h-5 w-5 text-primary" />
            Pest Diagnostic Tool
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Upload Area */}
          {!uploadedImage ? (
            <div
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              className={`relative border-2 border-dashed rounded-xl p-8 transition-colors ${
                isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
              }`}
            >
              <div className="flex flex-col items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
                <div className="text-center">
                  <p className="text-base font-medium text-foreground">Upload plant image</p>
                  <p className="text-sm text-muted-foreground mt-1">Drag & drop or tap to browse</p>
                </div>
                <div className="flex gap-3">
                  <label>
                    <input type="file" accept="image/*" onChange={handleFileInput} className="hidden" />
                    <Button variant="outline" className="h-12 px-6 bg-transparent" asChild>
                      <span>
                        <Upload className="h-5 w-5 mr-2" />
                        Browse Files
                      </span>
                    </Button>
                  </label>
                  <label>
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handleFileInput}
                      className="hidden"
                    />
                    <Button className="h-12 px-6 bg-primary" asChild>
                      <span>
                        <Camera className="h-5 w-5 mr-2" />
                        Take Photo
                      </span>
                    </Button>
                  </label>
                </div>
              </div>
            </div>
          ) : (
            <div className="relative">
              <img
                src={uploadedImage || "/placeholder.svg"}
                alt="Uploaded plant"
                className="w-full aspect-square object-cover rounded-xl"
              />
              <Button
                size="icon"
                variant="secondary"
                onClick={clearImage}
                className="absolute top-2 right-2 h-10 w-10 bg-card/90 backdrop-blur"
              >
                <X className="h-5 w-5" />
              </Button>
              {!result && (
                <Button
                  onClick={handleDiagnose}
                  disabled={isAnalyzing}
                  className="absolute bottom-3 left-3 right-3 h-14 bg-primary"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Bug className="h-5 w-5 mr-2" />
                      Diagnose Plant
                    </>
                  )}
                </Button>
              )}
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4">
              <div className="bg-alert/10 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 rounded-xl bg-alert/20 flex items-center justify-center shrink-0">
                    <AlertTriangle className="h-6 w-6 text-alert" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{result.pest}</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Detection confidence: <span className="text-alert font-medium">{result.confidence}%</span>
                    </p>
                  </div>
                </div>
              </div>

              <Tabs defaultValue="organic" className="w-full">
                <TabsList className="grid w-full grid-cols-2 h-12">
                  <TabsTrigger value="organic" className="h-10 text-sm font-medium">
                    <Leaf className="h-4 w-4 mr-2" />
                    Organic
                  </TabsTrigger>
                  <TabsTrigger value="chemical" className="h-10 text-sm font-medium">
                    <FlaskConical className="h-4 w-4 mr-2" />
                    Chemical
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="organic" className="mt-4 space-y-3">
                  {result.treatments.organic.map((treatment, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 bg-healthy/10 rounded-xl">
                      <CheckCircle2 className="h-5 w-5 text-healthy shrink-0 mt-0.5" />
                      <p className="text-sm text-foreground">{treatment}</p>
                    </div>
                  ))}
                </TabsContent>
                <TabsContent value="chemical" className="mt-4 space-y-3">
                  {result.treatments.chemical.map((treatment, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 bg-muted rounded-xl">
                      <FlaskConical className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                      <p className="text-sm text-foreground">{treatment}</p>
                    </div>
                  ))}
                  <p className="text-xs text-muted-foreground p-3 bg-warning/10 rounded-xl">
                    ⚠️ Always follow safety guidelines and local regulations when using chemical treatments.
                  </p>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
