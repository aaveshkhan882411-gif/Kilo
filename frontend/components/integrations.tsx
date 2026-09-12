"use client"

import { motion } from "framer-motion"

const INTEGRATIONS = ["PayPal", "Google OAuth", "WhatsApp", "Email", "Voice", "Google Calendar"]

export function Integrations() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Integrations</h2>
        <p className="text-xl text-gray-300 mb-12">
          Centralized Integration Gateway with adapters for PayPal, Google OAuth, WhatsApp, Email, Voice, and more.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          {INTEGRATIONS.map((name, index) => (
            <motion.div
              key={name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-xl px-6 py-4 text-sm font-semibold"
            >
              {name}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
