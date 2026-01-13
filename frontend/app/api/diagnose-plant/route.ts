import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { image } = body

    if (!image) {
      return NextResponse.json({ error: "No image provided" }, { status: 400 })
    }

    // Simulate plant disease/pest diagnosis
    const diagnosis = {
      pest: "Aphids (Aphidoidea)",
      confidence: 92,
      severity: "moderate",
      affectedArea: "15%",
      treatments: {
        organic: [
          "Neem oil spray (2-3 tbsp per gallon)",
          "Ladybug release (1500 per acre)",
          "Garlic-pepper spray",
          "Insecticidal soap application",
        ],
        chemical: ["Imidacloprid 0.5% SL", "Thiamethoxam 25% WG", "Acetamiprid 20% SP"],
      },
      preventionTips: [
        "Remove affected leaves immediately",
        "Introduce beneficial insects",
        "Monitor neighboring plants",
      ],
    }

    return NextResponse.json(diagnosis)
  } catch (error) {
    return NextResponse.json({ error: "Failed to diagnose plant" }, { status: 500 })
  }
}
