"use client"

import { motion } from "framer-motion"

export function Security() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-8">Security</h2>
        <p className="text-xl text-gray-300 mb-12">
          Defense in depth: secure cookies, server-side authorization, tenant isolation, RBAC, CSRF protection,
          CORS policy, CSP, HSTS, rate limiting, SSRF protection, webhook verification, payment verification,
          idempotency, replay protection, secret isolation, sanitized errors, audit logging.
        </p>
        <div className="glass rounded-2xl p-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {["RBAC", "Tenant Isolation", "Audit Logging", "Encryption", "CSRF", "CORS", "CSP", "HSTS"].map((item, index) => (
              <motion.div
                key={item}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="p-4 rounded-lg bg-white/5"
              >
                <div className="text-cyan text-sm font-semibold">{item}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
