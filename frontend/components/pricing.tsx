"use client"

import { motion } from "framer-motion"
import Link from "next/link"

const PLANS = [
  {
    id: "standard",
    name: "Standard",
    price: "$1,999",
    period: "/month",
    agents: 4,
    features: ["4 AI Agents", "CRM", "Email", "Basic Support"],
    cta: "Get Started",
    href: "/signup?plan=standard",
  },
  {
    id: "premium",
    name: "Premium",
    price: "$2,999",
    period: "/month",
    agents: 7,
    features: ["7 AI Agents", "CRM", "Email", "WhatsApp", "Priority Support"],
    cta: "Get Started",
    href: "/signup?plan=premium",
    popular: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "$3,999",
    period: "/month",
    agents: 13,
    features: ["13 AI Agents", "Full Workforce", "Dedicated Support", "Custom Integrations"],
    cta: "Get Started",
    href: "/signup?plan=enterprise",
  },
  {
    id: "autonomous",
    name: "Autonomous",
    price: "Custom",
    period: "",
    agents: 20,
    features: ["All 20 Agents", "Full Autonomy", "White Label", "Dedicated Infrastructure"],
    cta: "Contact Sales",
    href: "/contact",
  },
]

export function Pricing() {
  return (
    <section id="pricing" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-16">Simple, Transparent Pricing</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {PLANS.map((plan, index) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`glass rounded-2xl p-8 ${plan.popular ? "border-electric" : ""}`}
            >
              {plan.popular && (
                <div className="text-electric text-xs font-semibold mb-4 uppercase tracking-wider">Most Popular</div>
              )}
              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <div className="text-4xl font-bold mb-1">
                {plan.price}
                <span className="text-lg text-gray-400">{plan.period}</span>
              </div>
              <p className="text-gray-400 text-sm mb-6">{plan.agents} agents</p>
              <ul className="space-y-3 mb-8 text-left">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-gray-300 text-sm">
                    <span className="text-electric">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <Link href={plan.href} className="block w-full py-3 rounded-lg bg-electric text-white font-semibold text-center hover:bg-electric/80 transition">
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
