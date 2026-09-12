"use client"

import { motion } from "framer-motion"

const LIFECYCLE = ["REQUESTED", "PLANNED", "AUTHORIZED", "EXECUTING", "EXECUTED", "VERIFIED", "OUTCOME_RECORDED"]

export function OutcomeEngine() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Outcome Engine</h2>
        <p className="text-xl text-gray-300 mb-12">
          Every action has a lifecycle. Technical execution and business outcomes are tracked separately.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {LIFECYCLE.map((status, index) => (
            <motion.div
              key={status}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-xl px-6 py-3 text-sm font-semibold"
            >
              {status}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
