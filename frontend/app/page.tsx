import { Navigation } from "@/components/navigation"
import { Hero } from "@/components/hero"
import { AIWorkforce } from "@/components/ai-workforce"
import { Problems } from "@/components/problems"
import { Solution } from "@/components/solution"
import { AgentsGrid } from "@/components/agents-grid"
import { HowItWorks } from "@/components/how-it-works"
import { WebsiteIntelligence } from "@/components/website-intelligence"
import { BusinessBrain } from "@/components/business-brain"
import { AgentFactory } from "@/components/agent-factory"
import { ActionEngine } from "@/components/action-engine"
import { OutcomeEngine } from "@/components/outcome-engine"
import { Integrations } from "@/components/integrations"
import { Pricing } from "@/components/pricing"
import { ROICalculator } from "@/components/roi-calculator"
import { Security } from "@/components/security"
import { Control } from "@/components/control"
import { Evolution } from "@/components/evolution"
import { Footer } from "@/components/footer"

export default function HomePage() {
  return (
    <main className="min-h-screen bg-obsidian">
      <Navigation />
      <Hero />
      <AIWorkforce />
      <Problems />
      <Solution />
      <AgentsGrid />
      <HowItWorks />
      <WebsiteIntelligence />
      <BusinessBrain />
      <AgentFactory />
      <ActionEngine />
      <OutcomeEngine />
      <Integrations />
      <Pricing />
      <ROICalculator />
      <Security />
      <Control />
      <Evolution />
      <Footer />
    </main>
  )
}
