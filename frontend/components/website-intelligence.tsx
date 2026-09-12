"use client"

import { motion } from "framer-motion"

export function WebsiteIntelligence() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Website Intelligence</h2>
        <p className="text-xl text-gray-300 mb-12">
          Enter your website URL and GrowthAI will analyze your business, extract intelligence,
          and recommend the perfect AI workforce.
        </p>
        <div className="glass rounded-2xl p-8 max-w-2xl mx-auto">
          <div className="flex gap-4">
            <input
              type="url"
              placeholder="https://yourwebsite.com"
              className="flex-1 px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-electric"
            />
            <button className="px-6 py-3 rounded-lg bg-electric text-white font-semibold hover:bg-electric/80 transition">
              Analyze
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
