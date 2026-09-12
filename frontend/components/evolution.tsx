"use client"

import { motion } from "framer-motion"

export function Evolution() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Evolution Engine</h2>
        <p className="text-xl text-gray-300 mb-12">
          Observe → Analyze → Propose → Generate Change → Test → Security Check → Owner Approval →
          Staged Deployment → Health Check → Measure → Rollback if Needed
        </p>
        <div className="glass rounded-2xl p-8">
          <div className="flex flex-wrap justify-center gap-3">
            {["Observe", "Analyze", "Propose", "Generate Change", "Test", "Security Check", "Owner Approval", "Staged Deployment", "Health Check", "Measure", "Rollback"].map((step, index) => (
              <motion.div
                key={step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass rounded-xl px-4 py-2 text-sm"
              >
                {step}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
