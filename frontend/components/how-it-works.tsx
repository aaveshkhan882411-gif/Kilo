"use client"

import { motion } from "framer-motion"

const STEPS = [
  { title: "Business → Observe", description: "We analyze your business, website, and goals." },
  { title: "Understand", description: "AI analyzes data, identifies opportunities, and understands your market." },
  { title: "Recommend", description: "We recommend the optimal AI workforce for your needs." },
  { title: "Build Workforce", description: "We configure and deploy your custom AI agents." },
  { title: "Approve", description: "You review and approve the workforce configuration." },
  { title: "Payment", description: "Secure payment processing with PayPal." },
  { title: "Deploy", description: "Your AI workforce goes live across all channels." },
  { title: "Act", description: "Agents start working: leads, sales, support, follow-ups." },
  { title: "Verify", description: "Every action is verified and tracked." },
  { title: "Measure", description: "Real-time analytics and outcome tracking." },
  { title: "Optimize", description: "Continuous improvement based on results." },
  { title: "Evolve", description: "The system gets smarter over time." },
]

export function HowItWorks() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-16">How GrowthAI Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {STEPS.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="text-cyan font-bold text-sm mb-2">Step {index + 1}</div>
              <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
              <p className="text-gray-400 text-sm">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
