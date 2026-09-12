"use client"

import { motion } from "framer-motion"

export function Control() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">GrowthAI Control</h2>
        <p className="text-xl text-gray-300 mb-12">
          Owner/admin dashboard with real backend-backed views for system health, users, organizations,
          agents, billing, subscriptions, revenue, audit logs, integrations, AI runtime, queues, database health,
          security events, backups/status, deployments, and evolution proposals.
        </p>
        <div className="glass rounded-2xl p-8">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {["System Health", "Users", "Organizations", "Agents", "Billing", "Revenue", "Audit Logs", "Integrations", "AI Runtime"].map((item, index) => (
              <motion.div
                key={item}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="p-4 rounded-lg bg-white/5"
              >
                <div className="text-electric text-sm font-semibold">{item}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
