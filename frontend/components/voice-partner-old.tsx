// this voice session logic did not account for any server websockets/endpoints and just returned mock value


"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, X } from "lucide-react"
import { cn } from "@/lib/utils"

export function VoicePartner() {
  const [isActive, setIsActive] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const toggleVoice = () => {
    if (isActive) {
      // Disconnect
      wsRef.current?.close()
      setIsActive(false)
      setIsConnected(false)
    } else {
      // Connect to Gemini Live API WebSocket
      setIsActive(true)
      // Simulating connection
      setTimeout(() => setIsConnected(true), 1000)
    }
  }

  useEffect(() => {
    return () => {
      wsRef.current?.close()
    }
  }, [])

  return (
    <>
      {/* Expanded Voice Panel */}
      {isActive && (
        <div className="fixed inset-x-0 bottom-16 z-40 p-4 md:bottom-0">
          <div className="bg-card border border-border rounded-2xl p-4 shadow-xl max-w-md mx-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={cn("w-3 h-3 rounded-full", isConnected ? "bg-healthy animate-pulse" : "bg-warning")} />
                <span className="text-sm font-medium text-foreground">
                  {isConnected ? "Gemini Connected" : "Connecting..."}
                </span>
              </div>
              <Button size="icon" variant="ghost" onClick={() => setIsActive(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex items-center justify-center py-6">
              <div
                className={cn(
                  "relative w-24 h-24 rounded-full flex items-center justify-center",
                  isConnected ? "bg-primary/10" : "bg-muted",
                )}
              >
                {isConnected && (
                  <>
                    <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
                    <div className="absolute inset-2 rounded-full bg-primary/30 animate-pulse" />
                  </>
                )}
                <div
                  className={cn(
                    "w-16 h-16 rounded-full flex items-center justify-center",
                    isConnected ? "bg-primary" : "bg-muted-foreground/20",
                  )}
                >
                  {isConnected ? (
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <div
                          key={i}
                          className="w-1 bg-primary-foreground rounded-full sound-bar"
                          style={{ height: "8px" }}
                        />
                      ))}
                    </div>
                  ) : (
                    <Mic className="h-6 w-6 text-muted-foreground" />
                  )}
                </div>
              </div>
            </div>

            <p className="text-center text-sm text-muted-foreground">
              {isConnected
                ? "Listening... Ask about your crops, pests, or field conditions."
                : "Establishing secure connection..."}
            </p>
          </div>
        </div>
      )}

      {/* Floating Voice Button */}
      <div className="fixed bottom-20 right-4 z-50 md:bottom-6">
        <Button
          onClick={toggleVoice}
          size="icon"
          className={cn(
            "h-16 w-16 rounded-full shadow-lg transition-all",
            isActive ? "bg-alert hover:bg-alert/90" : "bg-primary hover:bg-primary/90",
          )}
        >
          {isActive ? (
            <MicOff className="h-7 w-7 text-alert-foreground" />
          ) : (
            <div className="relative">
              <Mic className="h-7 w-7 text-primary-foreground" />
              {!isActive && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-healthy rounded-full border-2 border-card" />
              )}
            </div>
          )}
        </Button>
        {!isActive && (
          <div className="absolute -top-2 -left-2 -right-2 -bottom-2 rounded-full border-2 border-primary/30 animate-pulse-wave pointer-events-none" />
        )}
      </div>
    </>
  )
}
