import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowRight, MapPin, ShieldCheck, Clock, Star, Wrench, Battery, Gauge, Wind, Droplets, Cog, Zap,
  Smartphone, CreditCard, BellRing, CheckCircle2, Quote,
} from "lucide-react";
import heroImg from "@/assets/hero-mechanic.jpg";
import { Reveal, SectionHeader, fadeUp, stagger } from "@/components/site/Section";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "MobileMechanic — Certified mobile mechanics, on-demand" },
      { name: "description", content: "Premium on-demand car care at your driveway. Live tracking, transparent pricing, certified mechanics." },
      { property: "og:title", content: "MobileMechanic — On-demand car care" },
      { property: "og:description", content: "Book a certified mechanic in minutes. Live tracking. Secure payments." },
      { property: "og:image", content: heroImg },
    ],
  }),
  component: Home,
});

const services = [
  { icon: Battery, title: "Battery service", desc: "Jumpstarts, replacements, diagnostics." },
  { icon: Wind, title: "AC & cooling", desc: "Re-gas, leak fix, system check." },
  { icon: Droplets, title: "Oil & fluids", desc: "Full-synthetic oil change at your door." },
  { icon: Gauge, title: "Diagnostics", desc: "OBD-II scan, error code repair." },
  { icon: Cog, title: "Brakes & tires", desc: "Pads, rotors, rotation, balancing." },
  { icon: Zap, title: "EV care", desc: "EV-certified specialists for hybrids & EVs." },
];

const steps = [
  { num: "01", title: "Pick a service", desc: "Browse our menu or describe the issue. Get an instant transparent quote." },
  { num: "02", title: "Choose time & place", desc: "Driveway, office, anywhere. Same-day slots available." },
  { num: "03", title: "Track & relax", desc: "Live mechanic ETA, secure in-app payment, digital invoice." },
];

const stats = [
  { v: "12k+", k: "Jobs completed" },
  { v: "4.9★", k: "Avg rating" },
  { v: "24/7", k: "Support" },
  { v: "30 min", k: "Avg arrival" },
];

const reviews = [
  { name: "Sara A.", role: "Toyota Corolla", text: "Fixed my battery in my driveway during a meeting. Genuinely felt like the future." },
  { name: "Hamza R.", role: "Honda Civic", text: "Live tracking, clear pricing, polite mechanic. Will not go to a workshop again." },
  { name: "Aisha K.", role: "Suzuki Swift", text: "Booked at 9am, AC was working by 11. Smooth, fast, premium." },
];

function Home() {
  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden bg-gradient-hero">
        <div className="absolute inset-0 -z-10 grid-pattern opacity-70" />
        <div className="container-page relative grid items-center gap-10 py-20 md:grid-cols-2 md:py-28">
          <motion.div initial="hidden" animate="visible" variants={stagger}>
            <motion.span variants={fadeUp} className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-elevated/80 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur">
              <span className="relative grid h-2 w-2 place-items-center rounded-full bg-success">
                <span className="absolute inset-0 animate-ping rounded-full bg-success/60" />
              </span>
              Live in 14 cities · Avg arrival 30 min
            </motion.span>

            <motion.h1 variants={fadeUp} className="mt-5 text-balance text-4xl font-bold leading-[1.05] tracking-tight md:text-6xl">
              Car trouble? <span className="text-gradient-primary">A certified mechanic</span> at your driveway in minutes.
            </motion.h1>

            <motion.p variants={fadeUp} className="mt-5 max-w-xl text-pretty text-lg text-muted-foreground">
              Skip the workshop. Book on-demand mobile mechanics, track them live, and pay securely — all from your phone.
            </motion.p>

            <motion.div variants={fadeUp} className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/signup" className="group inline-flex items-center gap-2 rounded-full bg-gradient-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-glow transition-transform hover:scale-[1.02]">
                Book a mechanic <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <Link to="/how-it-works" className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-elevated px-6 py-3 text-sm font-semibold hover:bg-accent">
                See how it works
              </Link>
            </motion.div>

            <motion.div variants={fadeUp} className="mt-10 flex flex-wrap items-center gap-6 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-primary" /> Insured & vetted</span>
              <span className="inline-flex items-center gap-2"><Star className="h-4 w-4 text-warning" /> 4.9 average rating</span>
              <span className="inline-flex items-center gap-2"><Clock className="h-4 w-4 text-primary" /> Same-day slots</span>
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="relative"
          >
            <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-mesh opacity-30 blur-2xl" />
            <div className="relative overflow-hidden rounded-3xl border border-border shadow-elevated">
              <img
                src={heroImg}
                alt="Certified mobile mechanic working at a customer driveway at dusk"
                width={1600}
                height={1200}
                className="h-full w-full object-cover"
              />
              {/* Floating tracking card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="glass absolute bottom-4 left-4 right-4 flex items-center gap-3 rounded-2xl p-3 md:left-6 md:right-auto md:max-w-xs"
              >
                <div className="relative grid h-10 w-10 place-items-center rounded-full bg-gradient-primary text-primary-foreground">
                  <MapPin className="h-4 w-4" />
                  <span className="absolute inset-0 rounded-full ring-2 ring-primary/30 animate-pulse" />
                </div>
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Mechanic en route</div>
                  <div className="text-sm font-semibold">Bilal · Arrives in 8 min</div>
                </div>
                <span className="rounded-full bg-success/15 px-2 py-1 text-xs font-medium text-success">LIVE</span>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Stats */}
        <div className="container-page pb-16">
          <Reveal>
            <div className="grid grid-cols-2 gap-4 rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft md:grid-cols-4">
              {stats.map((s) => (
                <div key={s.k} className="text-center">
                  <div className="text-2xl font-bold text-gradient-primary md:text-3xl">{s.v}</div>
                  <div className="mt-1 text-xs text-muted-foreground md:text-sm">{s.k}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* SERVICES */}
      <section className="container-page py-20">
        <SectionHeader
          eyebrow="What we fix"
          title={<>From quick checks to <span className="text-gradient-primary">complex repairs</span></>}
          description="Certified specialists handle everything your car needs — at your home, office, or on the road."
        />
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
          className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {services.map((s) => (
            <motion.div key={s.title} variants={fadeUp}>
              <div className="group h-full rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft transition-all hover:-translate-y-1 hover:shadow-elevated">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                  <s.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 text-lg font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
                <div className="mt-5 inline-flex items-center gap-1 text-sm font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
                  Learn more <ArrowRight className="h-4 w-4" />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
        <div className="mt-10 text-center">
          <Link to="/services" className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
            See full service catalog <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="bg-surface py-20">
        <div className="container-page">
          <SectionHeader
            eyebrow="How it works"
            title="Booked in 60 seconds"
            description="A polished, end-to-end experience from quote to invoice."
          />
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {steps.map((s, i) => (
              <Reveal key={s.num} delay={i * 0.1}>
                <div className="relative h-full overflow-hidden rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft">
                  <div className="absolute -right-8 -top-10 text-[8rem] font-bold leading-none text-foreground/[0.04]">{s.num}</div>
                  <div className="text-sm font-semibold text-primary">{s.num}</div>
                  <h3 className="mt-2 text-xl font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURE STRIP */}
      <section className="container-page py-20">
        <div className="grid gap-10 md:grid-cols-2">
          <Reveal>
            <div className="relative overflow-hidden rounded-3xl border border-border bg-gradient-hero p-8 md:p-10">
              <div className="absolute inset-0 -z-10 grid-pattern opacity-50" />
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-elevated/80 px-3 py-1 text-xs font-medium backdrop-blur">
                <BellRing className="h-3 w-3 text-primary" /> Real-time
              </span>
              <h3 className="mt-4 text-2xl font-bold tracking-tight md:text-3xl">Track every minute</h3>
              <p className="mt-3 max-w-md text-muted-foreground">
                Watch your mechanic on a live map, get push updates at every step, and chat or call in one tap.
              </p>
              <div className="mt-6 grid grid-cols-3 gap-3">
                {["Assigned", "En route", "On-site"].map((t, i) => (
                  <div key={t} className="rounded-xl border border-border bg-surface-elevated p-3 text-center text-xs">
                    <div className={`mx-auto mb-2 h-2 w-2 rounded-full ${i === 1 ? "bg-success animate-pulse" : "bg-muted-foreground/40"}`} />
                    {t}
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="relative h-full overflow-hidden rounded-3xl border border-border bg-surface-elevated p-8 shadow-soft md:p-10">
              <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 text-xs font-medium">
                <CreditCard className="h-3 w-3 text-primary" /> Secure payments
              </span>
              <h3 className="mt-4 text-2xl font-bold tracking-tight md:text-3xl">Pay your way</h3>
              <p className="mt-3 max-w-md text-muted-foreground">
                Card, JazzCash, Easypaisa, or cash on completion. Full digital invoice every time.
              </p>
              <ul className="mt-6 space-y-3 text-sm">
                {["Transparent quote before booking", "No hidden fees", "Refunds & disputes in-app"].map((t) => (
                  <li key={t} className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-success" /> {t}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="bg-surface py-20">
        <div className="container-page">
          <SectionHeader eyebrow="Loved by drivers" title="Trusted by thousands" />
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {reviews.map((r, i) => (
              <Reveal key={r.name} delay={i * 0.1}>
                <div className="h-full rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft">
                  <Quote className="h-6 w-6 text-primary" />
                  <p className="mt-3 text-sm leading-relaxed text-foreground">{r.text}</p>
                  <div className="mt-5 flex items-center gap-3">
                    <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-primary text-sm font-semibold text-primary-foreground">
                      {r.name[0]}
                    </div>
                    <div>
                      <div className="text-sm font-semibold">{r.name}</div>
                      <div className="text-xs text-muted-foreground">{r.role}</div>
                    </div>
                    <div className="ml-auto flex">
                      {Array.from({ length: 5 }).map((_, k) => <Star key={k} className="h-4 w-4 fill-warning text-warning" />)}
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container-page py-20">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-border bg-gradient-primary p-10 text-primary-foreground md:p-16">
            <div className="absolute inset-0 -z-10 opacity-30 grid-pattern" />
            <div className="grid items-center gap-8 md:grid-cols-2">
              <div>
                <h3 className="text-3xl font-bold tracking-tight md:text-4xl">Get the MobileMechanic app</h3>
                <p className="mt-3 max-w-md opacity-90">Book, track, pay and rate — all in one place. Available on iOS and Android.</p>
                <div className="mt-6 flex flex-wrap gap-3">
                  <Link to="/download" className="inline-flex items-center gap-2 rounded-full bg-background px-5 py-3 text-sm font-semibold text-foreground hover:opacity-95">
                    <Smartphone className="h-4 w-4" /> Download app
                  </Link>
                  <Link to="/for-mechanics" className="inline-flex items-center gap-2 rounded-full border border-primary-foreground/30 px-5 py-3 text-sm font-semibold hover:bg-primary-foreground/10">
                    <Wrench className="h-4 w-4" /> Drive with us
                  </Link>
                </div>
              </div>
              <div className="hidden md:block">
                <div className="ml-auto grid max-w-sm grid-cols-3 gap-3 text-foreground">
                  {[BellRing, MapPin, CreditCard, Star, ShieldCheck, Clock].map((I, i) => (
                    <div key={i} className="grid aspect-square place-items-center rounded-2xl bg-surface-elevated/90 shadow-soft">
                      <I className="h-5 w-5 text-primary" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
