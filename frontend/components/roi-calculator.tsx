"use client"

import { useState } from "react"
import { motion } from "framer-motion"

export function ROICalculator() {
  const [leads, setLeads] = useState(1000)
  const [conversion, setConversion] = useState(5)
  const [value, setValue] = useState(500)

  const recovered = leads * (conversion / 100) * 0.75
  const monthlyOpportunity = recovered * value
  const annualOpportunity = monthlyOpportunity * 12

  return (
    <section id="roi" className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-4">ROI Calculator</h2>
        <p className="text-xl text-gray-300 mb-12">Estimated additional revenue opportunity</p>
        <div className="glass rounded-2xl p-8 max-w-2xl mx-auto">
          <div className="space-y-6 text-left">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Monthly Leads</label>
              <input type="number" value={leads} onChange={(e) => setLeads(Number(e.target.value))} className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Conversion Rate (%)</label>
              <input type="number" value={conversion} onChange={(e) => setConversion(Number(e.target.value))} className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Average Customer Value ($)</label>
              <input type="number" value={value} onChange={(e) => setValue(Number(e.target.value))} className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white" />
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/10">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-gray-400 text-sm">Monthly Opportunity</div>
                <div className="text-2xl font-bold text-cyan">${monthlyOpportunity.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Annual Opportunity</div>
                <div className="text-2xl font-bold text-electric">${annualOpportunity.toLocaleString()}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
