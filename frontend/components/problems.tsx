"use client"

import { motion } from "framer-motion"

const PROBLEMS = [
  { title: "Leads Fall Through The Cracks", description: "Manual processes miss 70% of potential leads." },
  { title: "Slow Response Times", description: "Every hour of delay reduces conversion by 20%." },
  { title: "Inconsistent Follow-Up", description: "No standardized process for nurturing prospects." },
  { title: "Data Siloed Everywhere", description: "CRM, email, calendar, and WhatsApp data disconnected." },
  { title: "No Predictive Intelligence", description: "Reactive instead of proactive business decisions." },
  { title: "Scaling Is Expensive", description: "Hiring more staff doesn't scale like AI." },
]

export function Problems() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-16">The Problems GrowthAI Solves</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {PROBLEMS.map((problem, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-8"
            >
              <h3 className="text-xl font-semibold mb-3 text-red-400">{problem.title}</h3>
              <p className="text-gray-400">{problem.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
