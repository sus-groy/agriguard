"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Thermometer, Droplets, Sun, Wind, TrendingUp, AlertTriangle, CheckCircle2, Leaf } from "lucide-react"

const quickStats = [
  { label: "Field Health", value: "87%", icon: Leaf, status: "healthy" },
  { label: "Temperature", value: "24°C", icon: Thermometer, status: "normal" },
  { label: "Humidity", value: "65%", icon: Droplets, status: "normal" },
  { label: "UV Index", value: "6", icon: Sun, status: "warning" },
]

const alerts = [
  { id: 1, type: "warning", message: "High humidity in Sector B3", time: "10 min ago" },
  { id: 2, type: "alert", message: "Aphid detection in North Field", time: "25 min ago" },
  { id: 3, type: "success", message: "Irrigation completed", time: "1 hour ago" },
]

export function OverviewDashboard() {
  return (
    <div className="p-4 space-y-4">
      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 gap-3">
        {quickStats.map((stat) => (
          <Card key={stat.label} className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    stat.status === "healthy"
                      ? "bg-healthy/10"
                      : stat.status === "warning"
                        ? "bg-warning/10"
                        : "bg-muted"
                  }`}
                >
                  <stat.icon
                    className={`h-5 w-5 ${
                      stat.status === "healthy"
                        ? "text-healthy"
                        : stat.status === "warning"
                          ? "text-warning"
                          : "text-muted-foreground"
                    }`}
                  />
                </div>
                {stat.status === "healthy" && <TrendingUp className="h-4 w-4 text-healthy" />}
              </div>
              <p className="text-2xl font-bold text-foreground">{stat.value}</p>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Weather Overview Card */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Wind className="h-5 w-5 text-primary" />
            Weather Conditions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                <Sun className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-3xl font-bold text-foreground">24°C</p>
                <p className="text-sm text-muted-foreground">Partly Cloudy</p>
              </div>
            </div>
            <div className="text-right space-y-1">
              <div className="flex items-center gap-2 text-sm">
                <Droplets className="h-4 w-4 text-chart-3" />
                <span className="text-foreground">65%</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Wind className="h-4 w-4 text-muted-foreground" />
                <span className="text-foreground">12 km/h</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold">Recent Alerts</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start gap-3 p-3 rounded-xl ${
                alert.type === "alert" ? "bg-alert/10" : alert.type === "warning" ? "bg-warning/10" : "bg-healthy/10"
              }`}
            >
              {alert.type === "alert" ? (
                <AlertTriangle className="h-5 w-5 text-alert shrink-0 mt-0.5" />
              ) : alert.type === "warning" ? (
                <AlertTriangle className="h-5 w-5 text-warning shrink-0 mt-0.5" />
              ) : (
                <CheckCircle2 className="h-5 w-5 text-healthy shrink-0 mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground">{alert.message}</p>
                <p className="text-xs text-muted-foreground">{alert.time}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Field Status Map Preview */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold">Field Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative aspect-video rounded-xl overflow-hidden bg-muted">
            <img
              src="/aerial-view-farm-field-map-with-health-zones.jpg"
              alt="Field health map preview"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
            <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 text-xs bg-healthy/90 text-healthy-foreground px-2 py-1 rounded-full">
                  <div className="w-2 h-2 rounded-full bg-healthy-foreground" />
                  Healthy: 78%
                </div>
                <div className="flex items-center gap-1.5 text-xs bg-alert/90 text-alert-foreground px-2 py-1 rounded-full">
                  <div className="w-2 h-2 rounded-full bg-alert-foreground" />
                  Alert: 12%
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
