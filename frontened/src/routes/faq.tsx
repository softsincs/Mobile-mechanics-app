import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/faq")({
  head: () => ({
    meta: [
      { title: "FAQ — MobileMechanic" },
      { name: "description", content: "Frequently asked questions about MobileMechanic services, pricing and partners." },
      { property: "og:title", content: "MobileMechanic FAQ" },
      { property: "og:description", content: "Answers to common questions." },
    ],
  }),
  component: FaqPage,
});

const faqs = [
  { q: "How fast can a mechanic arrive?", a: "Our average arrival time is 30 minutes in supported cities. Same-day and scheduled slots are available." },
  { q: "Are your mechanics certified?", a: "Yes — every partner passes a skills test, background check, and continuous performance review." },
  { q: "What if I'm not happy with the service?", a: "All work is covered by a 30-day workmanship warranty. Disputes are resolved in-app within 24 hours." },
  { q: "Which payment methods do you accept?", a: "Cards, JazzCash, Easypaisa, bank transfer, and cash on completion." },
  { q: "Do you service EVs?", a: "Yes. We have EV-certified specialists for diagnostics, software updates and routine care." },
  { q: "Can businesses sign up for fleet care?", a: "Absolutely. See Pricing → Fleet, or contact our sales team for a custom plan." },
];

function FaqPage() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="FAQ"
            title={<>Questions, <span className="text-gradient-primary">answered</span></>}
            description="Can't find what you're looking for? Reach out via the contact page."
          />
        </div>
      </section>

      <section className="container-page py-16">
        <div className="mx-auto max-w-3xl space-y-3">
          {faqs.map((f, i) => {
            const isOpen = open === i;
            return (
              <div key={f.q} className="overflow-hidden rounded-2xl border border-border bg-surface-elevated shadow-soft">
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="flex w-full items-center justify-between gap-4 p-5 text-left"
                >
                  <span className="text-base font-semibold">{f.q}</span>
                  <ChevronDown className={`h-5 w-5 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`} />
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                    >
                      <div className="px-5 pb-5 text-sm text-muted-foreground">{f.a}</div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
