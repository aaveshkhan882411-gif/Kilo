"use client"

import { motion } from "framer-motion"
import Link from "next/link"

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-electric/10 via-transparent to-transparent" />
      <div className="max-w-5xl mx-auto px-6 text-center relative z-10">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-electric to-cyan bg-clip-text text-transparent"
        >
          AI That Works.
          <br />
          Systems That Evolve.
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto"
        >
          Never Miss a Lead. Every Customer. Every Time.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Link href="/analyze" className="px-8 py-4 rounded-xl bg-electric text-white font-semibold hover:bg-electric/80 transition">
            Analyze My Business
          </Link>
          <a href="#workforce" className="px-8 py-4 rounded-xl glass text-white font-semibold hover:bg-white/10 transition">
            See The AI Workforce
          </a>
        </motion.div>
      </div>
    </section>
  )
}
