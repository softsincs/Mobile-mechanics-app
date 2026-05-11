import { createFileRoute } from "@tanstack/react-router";
import { Heart, Rocket, ShieldCheck, Users } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — MobileMechanic" },
      { name: "description", content: "We're on a mission to make car care effortless, transparent, and trustworthy." },
      { property: "og:title", content: "About MobileMechanic" },
      { property: "og:description", content: "Our mission, values, and team." },
    ],
  }),
  component: AboutPage,
});

const values = [
  { icon: Heart, title: "Drivers first", desc: "Every product decision starts with the driver experience." },
  { icon: ShieldCheck, title: "Trust by default", desc: "Vetted mechanics, secure payments, transparent pricing." },
  { icon: Rocket, title: "Move fast", desc: "30-min average arrival. Same-day fixes. No queues." },
  { icon: Users, title: "Empower partners", desc: "Mechanics earn more and grow with us." },
];

function AboutPage() {
  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="About us"
            title={<>Re-imagining car care for the <span className="text-gradient-primary">modern driver</span></>}
            description="MobileMechanic was founded in 2024 to bring the driveway-first, app-native experience drivers deserve."
          />
        </div>
      </section>

      <section className="container-page py-16">
        <div className="grid gap-10 md:grid-cols-2">
          <Reveal>
            <h2 className="text-3xl font-bold tracking-tight">Our mission</h2>
            <p className="mt-4 text-muted-foreground">
              Workshops are slow, opaque, and often inconvenient. We're building a network of certified, on-demand mechanics — backed by software that makes every job fast, fair, and traceable.
            </p>
            <p className="mt-4 text-muted-foreground">
              From a battery jumpstart at midnight to a complete brake overhaul before your morning meeting, we make professional car care a tap away.
            </p>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="grid grid-cols-2 gap-4">
              {[
                { v: "12k+", k: "Cars serviced" },
                { v: "1,800", k: "Partner mechanics" },
                { v: "14", k: "Cities" },
                { v: "4.9★", k: "Customer rating" },
              ].map((s) => (
                <div key={s.k} className="rounded-2xl border border-border bg-surface-elevated p-6 text-center shadow-soft">
                  <div className="text-3xl font-bold text-gradient-primary">{s.v}</div>
                  <div className="mt-1 text-xs text-muted-foreground">{s.k}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      <section className="bg-surface py-16">
        <div className="container-page">
          <SectionHeader eyebrow="Values" title="What we believe" />
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {values.map((v) => (
              <Reveal key={v.title}>
                <div className="h-full rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft">
                  <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                    <v.icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 text-lg font-semibold">{v.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{v.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
