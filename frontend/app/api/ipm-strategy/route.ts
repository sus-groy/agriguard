import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    // Simulate IPM strategy data with weather
    const strategy = {
      weather: {
        temperature: 24,
        humidity: 65,
        windSpeed: 8,
        condition: "Partly Cloudy",
        uvIndex: 6,
        sprayConditions: "optimal",
      },
      tasks: [
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
      ],
      alerts: [
        {
          type: "weather",
          message: "Rain expected in 48 hours - plan spray schedule accordingly",
        },
      ],
    }

    return NextResponse.json(strategy)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch IPM strategy" }, { status: 500 })
  }
}
