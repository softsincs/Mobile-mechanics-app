import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { ClipboardList, MapPinned, Sparkles, ArrowRight, Search, Calendar, CreditCard, Star } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/how-it-works")({
  head: () => ({
    meta: [
      { title: "How it works — MobileMechanic" },
      { name: "description", content: "From booking to invoice in 4 simple steps. See how MobileMechanic works." },
      { property: "og:title", content: "How MobileMechanic works" },
      { property: "og:description", content: "Search, book, track, pay — a polished mobile experience." },
    ],
  }),
  component: HowItWorks,
});

const steps = [
  { icon: Search, title: "Pick a service", desc: "Browse our catalog or describe the problem in plain words." },
  { icon: Calendar, title: "Schedule", desc: "Same-day, next-day, or pick a slot. Instant transparent quote." },
  { icon: MapPinned, title: "Track live", desc: "Watch your mechanic en-route in real time, with chat & call." },
  { icon: CreditCard, title: "Pay & rate", desc: "Pay securely in-app, get a digital invoice, leave a review." },
];

function HowItWorks() {
  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="How it works"
            title={<>A premium experience, <span className="text-gradient-primary">end-to-end</span></>}
            description="Designed mobile-first. Built for trust, speed, and clarity."
          />
        </div>
      </section>

      <section className="container-page py-16">
        <ol className="relative grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((s, i) => (
            <motion.li
              key={s.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
              className="rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft"
            >
              <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                  <s.icon className="h-5 w-5" />
                </div>
                <span className="text-xs font-semibold text-muted-foreground">STEP {i + 1}</span>
              </div>
              <h3 className="mt-4 text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
            </motion.li>
          ))}
        </ol>
      </section>

      <section className="bg-surface py-16">
        <div className="container-page grid gap-10 md:grid-cols-2">
          <Reveal>
            <div className="rounded-3xl border border-border bg-surface-elevated p-8 shadow-soft">
              <ClipboardList className="h-7 w-7 text-primary" />
              <h3 className="mt-4 text-2xl font-bold">For drivers</h3>
              <ul className="mt-4 space-y-3 text-sm">
                {["No more workshop queues", "Verified parts with warranty", "Real-time ETA updates", "In-app support 24/7"].map((t) => (
                  <li key={t} className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-primary" /> {t}</li>
                ))}
              </ul>
              <Link to="/signup" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
                Book your first service <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="rounded-3xl border border-border bg-surface-elevated p-8 shadow-soft">
              <Star className="h-7 w-7 text-warning" />
              <h3 className="mt-4 text-2xl font-bold">For mechanics</h3>
              <ul className="mt-4 space-y-3 text-sm">
                {["Set your own schedule", "Same-day payouts", "Backed by smart dispatch", "Grow with ratings & tips"].map((t) => (
                  <li key={t} className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-primary" /> {t}</li>
                ))}
              </ul>
              <Link to="/for-mechanics" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
                Drive with MobileMechanic <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}
