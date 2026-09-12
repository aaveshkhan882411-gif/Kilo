"use client"

import { motion } from "framer-motion"

export function BusinessBrain() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Business Brain</h2>
        <p className="text-xl text-gray-300 mb-12">
          GrowthAI builds a normalized business intelligence model covering industry, products,
          services, target customers, locations, pricing, lead channels, sales process, customer journey,
          business goals, opportunities, risks, and bottlenecks.
        </p>
        <div className="glass rounded-2xl p-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
            {["Industry", "Products", "Services", "Target Customers", "Locations", "Pricing", "Lead Channels", "Sales Process"].map((item, index) => (
              <motion.div
                key={index}
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
