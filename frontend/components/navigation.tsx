"use client"

import { motion } from "framer-motion"
import Link from "next/link"

export function Navigation() {
  return (
    <nav className="fixed top-0 w-full z-50 glass">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="text-xl font-bold bg-gradient-to-r from-electric to-cyan bg-clip-text text-transparent">
          GrowthAI
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm text-gray-300">
          <a href="#workforce" className="hover:text-white transition">Workforce</a>
          <a href="#pricing" className="hover:text-white transition">Pricing</a>
          <a href="#roi" className="hover:text-white transition">ROI</a>
          <Link href="/analyze" className="px-4 py-2 rounded-lg bg-electric text-white hover:bg-electric/80 transition">
            Analyze My Business
          </Link>
        </div>
      </div>
    </nav>
  )
}
