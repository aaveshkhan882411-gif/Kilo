"use client"

import { motion } from "framer-motion"

const ACTIONS = ["Create Lead", "Send Email", "Create Appointment", "Update CRM", "Send WhatsApp", "Create Follow-up", "Execute Workflow"]

export function ActionEngine() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Action Engine</h2>
        <p className="text-xl text-gray-300 mb-12">
          AI Decision → Action Plan → Permission Check → Tool → Execution → Result → Verification → Outcome
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {ACTIONS.map((action, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="px-4 py-2 rounded-lg glass text-sm text-gray-300"
            >
              {action}
            </motion.span>
          ))}
        </div>
      </div>
    </section>
  )
}
