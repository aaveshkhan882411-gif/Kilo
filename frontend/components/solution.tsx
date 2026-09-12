"use client"

import { motion } from "framer-motion"

export function Solution() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">The GrowthAI Solution</h2>
        <p className="text-xl text-gray-300 mb-12">
          GrowthAI is not a chatbot. It is an autonomous AI workforce and business operating system
          that observes, understands, recommends, builds, deploys, acts, verifies, measures, optimizes, and evolves.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {["Observe", "Understand", "Recommend", "Build Workforce", "Approve", "Deploy", "Act", "Verify", "Optimize", "Evolve"].map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="glass rounded-2xl p-6"
            >
              <div className="text-electric font-bold text-2xl mb-2">{index + 1}</div>
              <div className="text-white font-semibold">{step}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
