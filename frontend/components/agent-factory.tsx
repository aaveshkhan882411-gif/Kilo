"use client"

import { motion } from "framer-motion"

export function AgentFactory() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Agent Factory</h2>
        <p className="text-xl text-gray-300 mb-12">
          Business information + website + goals + existing systems + problems →
          Business Analysis → Opportunity Detection → Workforce Recommendation → Customer Approval → Payment → Deployment
        </p>
        <div className="glass rounded-2xl p-8">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
            <input
              type="text"
              placeholder="Your website URL"
              className="px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-electric w-full md:w-auto"
            />
            <button className="px-6 py-3 rounded-lg bg-electric text-white font-semibold hover:bg-electric/80 transition">
              Build My Workforce
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
