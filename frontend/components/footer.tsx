"use client"

import { motion } from "framer-motion"

export function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-white/10">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="text-xl font-bold bg-gradient-to-r from-electric to-cyan bg-clip-text text-transparent">
          GrowthAI
        </div>
        <p className="text-gray-400 text-sm">
          © {new Date().getFullYear()} GrowthAI. AI That Works. Systems That Evolve.
        </p>
        <div className="flex gap-6 text-sm text-gray-400">
          <a href="#" className="hover:text-white transition">Privacy</a>
          <a href="#" className="hover:text-white transition">Terms</a>
          <a href="#" className="hover:text-white transition">Security</a>
        </div>
      </div>
    </footer>
  )
}
