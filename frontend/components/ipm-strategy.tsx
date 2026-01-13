"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ListChecks,
  Droplets,
  Wind,
  Sun,
  Cloud,
  Calendar,
  Clock,
  CheckCircle2,
  Circle,
  Flower2,
  Sprout,
  Bug,
  type LucideIcon,
} from "lucide-react"

interface WeatherData {
  temperature: number
  humidity: number
  windSpeed: number
  condition: string
}

interface Task {
  id: string
  title: string
  description: string
  deadline: string
  priority: "high" | "medium" | "low"
  completed: boolean
}

const taskIconMap: Record<string, LucideIcon> = {
  "1": Flower2,
  "2": Sprout,
  "3": Bug,
  "4": Calendar,
  "5": ListChecks,
}

function getTaskIcon(task: Task): LucideIcon {
  // Check by ID first
  if (taskIconMap[task.id]) {
    return taskIconMap[task.id]
  }
  // Fallback: match by title keywords
  const titleLower = task.title.toLowerCase()
  if (titleLower.includes("marigold") || titleLower.includes("flower") || titleLower.includes("plant")) {
    return Flower2
  }
  if (titleLower.includes("spray") || titleLower.includes("neem")) {
    return Sprout
  }
  if (titleLower.includes("bug") || titleLower.includes("ladybug") || titleLower.includes("beetle")) {
    return Bug
  }
  if (titleLower.includes("trap") || titleLower.includes("calendar") || titleLower.includes("schedule")) {
    return Calendar
  }
  // Default fallback
  return ListChecks
}

export function IpmStrategy() {
  const [weather, setWeather] = useState<WeatherData>({
    temperature: 24,
    humidity: 65,
    windSpeed: 8,
    condition: "Partly Cloudy",
  })
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: "1",
      title: "Plant Marigolds",
      description: "Border rows A1-A5 for aphid deterrent",
      deadline: "Today",
      priority: "high",
      completed: false,
    },
    {
      id: "2",
      title: "Spray Neem Oil",
      description: "Apply before 5 PM when wind < 10 km/h",
      deadline: "Today",
      priority: "high",
      completed: false,
    },
    {
      id: "3",
      title: "Release Ladybugs",
      description: "Section B - 1500 beetles per acre",
      deadline: "Tomorrow",
      priority: "medium",
      completed: false,
    },
    {
      id: "4",
      title: "Install Sticky Traps",
      description: "Yellow traps near greenhouse entry",
      deadline: "This Week",
      priority: "low",
      completed: true,
    },
    {
      id: "5",
      title: "Crop Rotation Planning",
      description: "Plan next season's rotation schedule",
      deadline: "This Week",
      priority: "low",
      completed: true,
    },
  ])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    console.log("[v0] IpmStrategy component mounted")
    const fetchStrategy = async () => {
      try {
        console.log("[v0] Fetching IPM strategy data")
        const response = await fetch("/api/ipm-strategy")
        const data = await response.json()
        console.log("[v0] IPM strategy data received:", data)
        if (data.weather) setWeather(data.weather)
        if (data.tasks) setTasks(data.tasks)
      } catch (error) {
        console.log("[v0] IPM strategy fetch error, using mock data:", error)
        // Already using default state
      } finally {
        setLoading(false)
      }
    }
    fetchStrategy()
  }, [])

  const toggleTask = (id: string) => {
    setTasks(tasks.map((task) => (task.id === id ? { ...task, completed: !task.completed } : task)))
  }

  const completedCount = tasks.filter((t) => t.completed).length

  console.log("[v0] IpmStrategy rendering, weather:", weather, "tasks count:", tasks.length)

  return (
    <div className="p-4 space-y-4">
      {/* Weather Widget */}
      <Card
        className="border-primary/20"
        style={{ background: "linear-gradient(to bottom right, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05))" }}
      >
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-card flex items-center justify-center">
                <Cloud className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{weather.temperature}°C</p>
                <p className="text-sm text-muted-foreground">{weather.condition}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground mb-1">Spray Conditions</p>
              <div
                className="px-3 py-1 rounded-full text-sm font-medium"
                style={{
                  backgroundColor: weather.windSpeed < 10 ? "rgb(34, 197, 94)" : "rgb(234, 179, 8)",
                  color: weather.windSpeed < 10 ? "white" : "rgb(30, 30, 30)",
                }}
              >
                {weather.windSpeed < 10 ? "Optimal" : "Moderate"}
              </div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-card rounded-xl p-3 text-center">
              <Droplets className="h-5 w-5 mx-auto mb-1" style={{ color: "rgb(59, 130, 246)" }} />
              <p className="text-lg font-semibold text-foreground">{weather.humidity}%</p>
              <p className="text-xs text-muted-foreground">Humidity</p>
            </div>
            <div className="bg-card rounded-xl p-3 text-center">
              <Wind className="h-5 w-5 text-muted-foreground mx-auto mb-1" />
              <p className="text-lg font-semibold text-foreground">{weather.windSpeed} km/h</p>
              <p className="text-xs text-muted-foreground">Wind</p>
            </div>
            <div className="bg-card rounded-xl p-3 text-center">
              <Sun className="h-5 w-5 mx-auto mb-1" style={{ color: "rgb(234, 179, 8)" }} />
              <p className="text-lg font-semibold text-foreground">6</p>
              <p className="text-xs text-muted-foreground">UV Index</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* IPM Tasks */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <ListChecks className="h-5 w-5 text-primary" />
              Preventative Tasks
            </CardTitle>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">
                {completedCount}/{tasks.length}
              </span>
              <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${(completedCount / tasks.length) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {tasks.map((task) => {
            const TaskIcon = getTaskIcon(task)
            return (
              <div
                key={task.id}
                className={`flex items-start gap-3 p-4 rounded-xl transition-colors ${
                  task.completed ? "bg-muted/50" : "bg-card border border-border"
                }`}
              >
                <button onClick={() => toggleTask(task.id)} className="mt-0.5 shrink-0">
                  {task.completed ? (
                    <CheckCircle2 className="h-6 w-6" style={{ color: "rgb(34, 197, 94)" }} />
                  ) : (
                    <Circle
                      className="h-6 w-6"
                      style={{
                        color:
                          task.priority === "high"
                            ? "rgb(239, 68, 68)"
                            : task.priority === "medium"
                              ? "rgb(234, 179, 8)"
                              : "rgb(156, 163, 175)",
                      }}
                    />
                  )}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <p
                      className={`font-medium ${
                        task.completed ? "text-muted-foreground line-through" : "text-foreground"
                      }`}
                    >
                      {task.title}
                    </p>
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                      <TaskIcon className="h-4 w-4 text-primary" />
                    </div>
                  </div>
                  <p
                    className={`text-sm mt-1 ${task.completed ? "text-muted-foreground/70" : "text-muted-foreground"}`}
                  >
                    {task.description}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                    <span
                      className="text-xs"
                      style={{
                        color: task.deadline === "Today" && !task.completed ? "rgb(239, 68, 68)" : undefined,
                        fontWeight: task.deadline === "Today" && !task.completed ? 500 : undefined,
                      }}
                    >
                      {task.deadline}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>
    </div>
  )
}
