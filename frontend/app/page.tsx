"use client"

import { useState } from "react"
import { MobileSidebar } from "@/components/mobile-sidebar"
import { FieldMonitor } from "@/components/field-monitor"
import { PestDiagnostic } from "@/components/pest-diagnostic"
import { IpmStrategy } from "@/components/ipm-strategy"
import { VoicePartner } from "@/components/voice-partner"
import { OverviewDashboard } from "@/components/overview-dashboard"

export default function AgriGuardDashboard() {
  const [activeView, setActiveView] = useState<string>("overview")

  const renderContent = () => {
    switch (activeView) {
      case "overview":
        return <OverviewDashboard />
      case "health-map":
        return <FieldMonitor />
      case "diagnostic":
        return <PestDiagnostic />
      case "strategy":
        return <IpmStrategy />
      case "voice":
        return (
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="text-center">
              <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center animate-pulse-wave">
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div
                        key={i}
                        className="w-1 bg-primary-foreground rounded-full sound-bar"
                        style={{ height: "8px" }}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">Gemini Voice Partner</h2>
              <p className="text-muted-foreground text-sm">Tap the mic below to start talking</p>
            </div>
          </div>
        )
      default:
        return <OverviewDashboard />
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <MobileSidebar activeView={activeView} onViewChange={setActiveView} />

      <main className="flex-1 pb-24 overflow-auto">{renderContent()}</main>

      <VoicePartner />
    </div>
  )
}
