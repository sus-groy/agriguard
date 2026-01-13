// assumes that there's a websocket at /voice-partner

"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, X } from "lucide-react"
import { cn } from "@/lib/utils"

export function VoicePartner() {
  const [isActive, setIsActive] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  
  // --- THE ENGINE REFS (The "Extra" Stuff) ---
  const wsRef = useRef<WebSocket | null>(null)
  const audioCtxRef = useRef<AudioContext | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const nextStartTimeRef = useRef<number>(0)

  const toggleVoice = async () => {
    if (isActive) {
      cleanup()
    } else {
      await startVoiceSession()
    }
  }

  const startVoiceSession = async () => {
    setIsActive(true)

    // 1. Open the "Phone Line" (WebSocket) to your server
    // Change "localhost:8000" to your actual server address
    const socket = new WebSocket("ws://localhost:8000/voice-partner")
    wsRef.current = socket

    socket.onopen = () => setIsConnected(true)
    socket.onclose = () => cleanup()

    // 2. Listen for the AI's Voice coming from the server
    socket.onmessage = async (event) => {
      const data = JSON.parse(event.data)
      if (data.ai_audio) {
        playAiAudio(data.ai_audio)
      }
      if (data.event === "interrupt") {
        // If you talk, stop the AI from finishing its sentence
        nextStartTimeRef.current = audioCtxRef.current?.currentTime || 0
      }
    }

    // 3. Turn on the Microphone
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      
      const audioCtx = new AudioContext({ sampleRate: 16000 }) // Gemini needs 16kHz
      audioCtxRef.current = audioCtx

      const source = audioCtx.createMediaStreamSource(stream)
      const processor = audioCtx.createScriptProcessor(4096, 1, 1)

      source.connect(processor)
      processor.connect(audioCtx.destination)

      // 4. Send your voice to the server in tiny chunks
      processor.onaudioprocess = (e) => {
        if (socket.readyState === WebSocket.OPEN) {
          const rawData = e.inputBuffer.getChannelData(0)
          const pcm16 = new Int16Array(rawData.length)
          for (let i = 0; i < rawData.length; i++) {
            pcm16[i] = Math.max(-1, Math.min(1, rawData[i])) * 0x7FFF
          }
          
          socket.send(JSON.stringify({
            audio_chunk: btoa(String.fromCharCode(...new Uint8Array(pcm16.buffer)))
          }))
        }
      }
    } catch (err) {
      console.error("Mic error:", err)
      cleanup()
    }
  }

  // Helper to play the AI's voice chunks smoothly
  const playAiAudio = (base64Audio: string) => {
    if (!audioCtxRef.current) return
    const binary = atob(base64Audio)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
    const pcm16 = new Int16Array(bytes.buffer)
    const float32 = new Float32Array(pcm16.length)
    for (let i = 0; i < pcm16.length; i++) float32[i] = pcm16[i] / 32768.0

    const buffer = audioCtxRef.current.createBuffer(1, float32.length, 24000)
    buffer.getChannelData(0).set(float32)
    const source = audioCtxRef.current.createBufferSource()
    source.buffer = buffer
    source.connect(audioCtxRef.current.destination)

    const startTime = Math.max(audioCtxRef.current.currentTime, nextStartTimeRef.current)
    source.start(startTime)
    nextStartTimeRef.current = startTime + buffer.duration
  }

  const cleanup = () => {
    wsRef.current?.close()
    streamRef.current?.getTracks().forEach(t => t.stop())
    audioCtxRef.current?.close()
    setIsActive(false)
    setIsConnected(false)
    nextStartTimeRef.current = 0
  }

  useEffect(() => { return () => cleanup() }, [])

  return (
    <>
      {/* --- YOUR ORIGINAL UI STARTS HERE --- */}
      {isActive && (
        <div className="fixed inset-x-0 bottom-16 z-40 p-4 md:bottom-0">
          <div className="bg-card border border-border rounded-2xl p-4 shadow-xl max-w-md mx-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={cn("w-3 h-3 rounded-full", isConnected ? "bg-green-500 animate-pulse" : "bg-yellow-500")} />
                <span className="text-sm font-medium text-foreground">
                  {isConnected ? "Gemini Connected" : "Connecting..."}
                </span>
              </div>
              <Button size="icon" variant="ghost" onClick={cleanup} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex items-center justify-center py-6">
              <div className={cn("relative w-24 h-24 rounded-full flex items-center justify-center", isConnected ? "bg-primary/10" : "bg-muted")}>
                {isConnected && (
                  <>
                    <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
                    <div className="absolute inset-2 rounded-full bg-primary/30 animate-pulse" />
                  </>
                )}
                <div className={cn("w-16 h-16 rounded-full flex items-center justify-center", isConnected ? "bg-primary" : "bg-muted-foreground/20")}>
                  {isConnected ? (
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="w-1 bg-white rounded-full animate-bounce" style={{ height: "12px", animationDelay: `${i * 0.1}s` }} />
                      ))}
                    </div>
                  ) : (
                    <Mic className="h-6 w-6 text-muted-foreground" />
                  )}
                </div>
              </div>
            </div>

            <p className="text-center text-sm text-muted-foreground">
              {isConnected ? "Listening... Ask about your crops or field conditions." : "Establishing secure connection..."}
            </p>
          </div>
        </div>
      )}

      <div className="fixed bottom-20 right-4 z-50 md:bottom-6">
        <Button
          onClick={toggleVoice}
          size="icon"
          className={cn("h-16 w-16 rounded-full shadow-lg transition-all", isActive ? "bg-red-500" : "bg-primary")}
        >
          {isActive ? <MicOff className="h-7 w-7 text-white" /> : <Mic className="h-7 w-7 text-white" />}
        </Button>
      </div>
    </>
  )
}