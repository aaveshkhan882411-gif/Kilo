"use client"

import { motion } from "framer-motion"

const AGENTS = [
  { id: "ai-ceo", name: "AI CEO", description: "Strategic oversight and decision making" },
  { id: "ai-business-analyst", name: "AI Business Analyst", description: "Business analysis and insights" },
  { id: "ai-growth-strategist", name: "AI Growth Strategist", description: "Growth strategy development" },
  { id: "ai-lead-intelligence", name: "AI Lead Intelligence", description: "Lead scoring and qualification" },
  { id: "ai-revenue-optimizer", name: "AI Revenue Optimizer", description: "Revenue optimization" },
  { id: "ai-sales", name: "AI Sales", description: "Sales automation" },
  { id: "ai-receptionist", name: "AI Receptionist", description: "Front desk and inquiry handling" },
  { id: "ai-support", name: "AI Support", description: "Customer support" },
  { id: "ai-followup", name: "AI Follow-up", description: "Automated follow-up" },
  { id: "ai-appointment", name: "AI Appointment", description: "Appointment scheduling" },
  { id: "ai-voice", name: "AI Voice", description: "Voice interactions" },
  { id: "ai-email", name: "AI Email", description: "Email automation" },
  { id: "ai-whatsapp", name: "AI WhatsApp", description: "WhatsApp messaging" },
  { id: "ai-crm", name: "AI CRM", description: "CRM management" },
  { id: "ai-workflow", name: "AI Workflow", description: "Workflow automation" },
  { id: "ai-marketing-agent", name: "AI Marketing Agent", description: "Marketing automation" },
  { id: "ai-analytics", name: "AI Analytics", description: "Data analysis and reporting" },
  { id: "ai-agent-architect", name: "AI Agent Architect", description: "Agent design and configuration" },
  { id: "ai-autonomous-orchestrator", name: "AI Autonomous Orchestrator", description: "Autonomous orchestration" },
  { id: "ai-review-manager", name: "AI Review Manager", description: "Review management" },
]

export function AgentsGrid() {
  return (
    <section id="workforce" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-16">20 AI Agents. One Workforce.</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {AGENTS.map((agent, index) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className="glass rounded-2xl p-6 hover:border-electric/50 transition"
            >
              <div className="text-electric font-semibold mb-2">{agent.name}</div>
              <p className="text-gray-400 text-sm">{agent.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
