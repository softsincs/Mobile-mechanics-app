import { createFileRoute, Link } from "@tanstack/react-router";
import { Wallet, TrendingUp, Calendar, ShieldCheck, BadgeCheck, ArrowRight, Wrench } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/for-mechanics")({
  head: () => ({
    meta: [
      { title: "Drive with MobileMechanic — Earn on your schedule" },
      { name: "description", content: "Become a MobileMechanic partner. Flexible jobs, same-day payouts, smart dispatch." },
      { property: "og:title", content: "Become a MobileMechanic partner" },
      { property: "og:description", content: "Flexible jobs, same-day payouts, smart dispatch." },
    ],
  }),
  component: ForMechanics,
});

const benefits = [
  { icon: Wallet, title: "Same-day payouts", desc: "Get paid daily into your bank, JazzCash or Easypaisa." },
  { icon: Calendar, title: "Your schedule", desc: "Toggle availability anytime. Work as much or as little as you want." },
  { icon: TrendingUp, title: "Grow with ratings", desc: "Top-rated mechanics earn priority dispatch and tips." },
  { icon: ShieldCheck, title: "Insured jobs", desc: "Every accepted job is covered by our liability insurance." },
];

const reqs = [
  "Valid CNIC and driver's license",
  "Minimum 2 years professional experience",
  "Own basic tools and reliable transport",
  "Pass our background check & skills test",
];

function ForMechanics() {
  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page grid gap-10 py-16 md:grid-cols-2 md:py-24">
          <Reveal>
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-elevated/80 px-3 py-1 text-xs font-medium backdrop-blur">
              <BadgeCheck className="h-3 w-3 text-primary" /> Now hiring across 14 cities
            </span>
            <h1 className="mt-5 text-4xl font-bold tracking-tight md:text-5xl">
              Earn more, on <span className="text-gradient-primary">your schedule</span>.
            </h1>
            <p className="mt-5 text-lg text-muted-foreground">
              Join thousands of certified mechanics earning premium rates with the MobileMechanic partner app.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link to="/signup" className="inline-flex items-center gap-2 rounded-full bg-gradient-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-glow">
                <Wrench className="h-4 w-4" /> Apply now
              </Link>
              <Link to="/contact" className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-elevated px-5 py-3 text-sm font-semibold">
                Talk to recruiter
              </Link>
            </div>
            <div className="mt-10 grid grid-cols-3 gap-4">
              {[
                { v: "₨ 90k+", k: "Avg monthly" },
                { v: "4.8★", k: "Partner rating" },
                { v: "12 min", k: "Avg dispatch" },
              ].map((s) => (
                <div key={s.k} className="rounded-xl border border-border bg-surface-elevated p-4 text-center shadow-soft">
                  <div className="text-xl font-bold text-gradient-primary">{s.v}</div>
                  <div className="mt-1 text-xs text-muted-foreground">{s.k}</div>
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="relative rounded-3xl border border-border bg-surface-elevated p-6 shadow-elevated">
              <div className="text-xs text-muted-foreground">Today</div>
              <div className="mt-1 flex items-baseline gap-2">
                <div className="text-4xl font-bold">₨ 14,250</div>
                <span className="rounded-full bg-success/15 px-2 py-0.5 text-xs font-semibold text-success">+18%</span>
              </div>
              <div className="mt-4 grid grid-cols-7 items-end gap-1.5">
                {[20, 35, 28, 60, 45, 75, 90].map((h, i) => (
                  <div
                    key={i}
                    className="rounded-md bg-gradient-primary/80"
                    style={{ height: `${h}%`, minHeight: "10px" }}
                  />
                ))}
              </div>
              <div className="mt-6 space-y-3">
                {[
                  { title: "Battery replacement", time: "2:30 PM", price: "₨ 4,500" },
                  { title: "Oil change — Civic", time: "11:00 AM", price: "₨ 5,200" },
                  { title: "Brake pads — Corolla", time: "9:15 AM", price: "₨ 4,550" },
                ].map((j) => (
                  <div key={j.title} className="flex items-center justify-between rounded-xl border border-border bg-background p-3">
                    <div>
                      <div className="text-sm font-semibold">{j.title}</div>
                      <div className="text-xs text-muted-foreground">{j.time}</div>
                    </div>
                    <div className="text-sm font-semibold text-success">{j.price}</div>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="container-page py-16">
        <SectionHeader eyebrow="Benefits" title="Why join MobileMechanic" />
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {benefits.map((b) => (
            <Reveal key={b.title}>
              <div className="h-full rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft">
                <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                  <b.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 text-lg font-semibold">{b.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{b.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="bg-surface py-16">
        <div className="container-page grid gap-10 md:grid-cols-2">
          <Reveal>
            <h3 className="text-3xl font-bold tracking-tight">Requirements</h3>
            <p className="mt-3 text-muted-foreground">A short application, fast review.</p>
            <ul className="mt-6 space-y-3">
              {reqs.map((r) => (
                <li key={r} className="flex items-center gap-3 rounded-xl border border-border bg-surface-elevated p-3">
                  <BadgeCheck className="h-5 w-5 text-primary" />
                  <span className="text-sm">{r}</span>
                </li>
              ))}
            </ul>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="rounded-3xl border border-border bg-gradient-primary p-8 text-primary-foreground shadow-elevated">
              <h3 className="text-2xl font-bold">Apply in minutes</h3>
              <p className="mt-3 opacity-90">Onboarding takes about 24-48 hours from application to first job.</p>
              <Link to="/signup" className="mt-6 inline-flex items-center gap-2 rounded-full bg-background px-5 py-3 text-sm font-semibold text-foreground">
                Start application <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}
