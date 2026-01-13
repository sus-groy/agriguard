"use client"

import { useState } from "react"
import { LayoutDashboard, Map, Bug, ListChecks, Mic, Menu, X, Leaf } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"

interface MobileSidebarProps {
  activeView: string
  onViewChange: (view: string) => void
}

const navItems = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "health-map", label: "Health Map", icon: Map },
  { id: "diagnostic", label: "Diagnostic", icon: Bug },
  { id: "strategy", label: "Strategy", icon: ListChecks },
  { id: "voice", label: "Voice", icon: Mic },
]

export function MobileSidebar({ activeView, onViewChange }: MobileSidebarProps) {
  const [open, setOpen] = useState(false)

  const handleNavClick = (id: string) => {
    onViewChange(id)
    setOpen(false)
  }

  return (
    <header className="sticky top-0 z-40 bg-card border-b border-border">
      <div className="flex items-center justify-between px-4 h-16">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <Leaf className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">AgriGuard</h1>
            <p className="text-xs text-muted-foreground">Smart Field Management</p>
          </div>
        </div>

        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="h-12 w-12">
              <Menu className="h-6 w-6" />
              <span className="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-72 p-0 bg-sidebar">
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                    <Leaf className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <span className="font-bold text-sidebar-foreground">AgriGuard</span>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <nav className="flex-1 p-4">
                <ul className="space-y-2">
                  {navItems.map((item) => (
                    <li key={item.id}>
                      <button
                        onClick={() => handleNavClick(item.id)}
                        className={cn(
                          "w-full flex items-center gap-4 px-4 py-4 rounded-xl text-base font-medium transition-all",
                          "active:scale-98",
                          activeView === item.id
                            ? "bg-sidebar-accent text-primary"
                            : "text-sidebar-foreground hover:bg-sidebar-accent/50",
                        )}
                      >
                        <item.icon
                          className={cn("h-6 w-6", activeView === item.id ? "text-primary" : "text-muted-foreground")}
                        />
                        {item.label}
                      </button>
                    </li>
                  ))}
                </ul>
              </nav>

              <div className="p-4 border-t border-sidebar-border">
                <div className="bg-healthy/10 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-healthy animate-pulse" />
                    <span className="text-sm font-medium text-healthy">System Online</span>
                  </div>
                  <p className="text-xs text-muted-foreground">All sensors connected</p>
                </div>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Bottom Tab Navigation for Mobile */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t border-border pb-safe md:hidden">
        <div className="flex items-center justify-around h-16">
          {navItems.slice(0, 4).map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={cn(
                "flex flex-col items-center justify-center gap-1 px-3 py-2 rounded-lg transition-colors min-w-[64px]",
                activeView === item.id ? "text-primary" : "text-muted-foreground",
              )}
            >
              <item.icon className="h-6 w-6" />
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </header>
  )
}
