import { createFileRoute, Link } from "@tanstack/react-router";
import { Battery, Wind, Droplets, Gauge, Cog, Zap, Wrench, ShieldCheck, Sparkles, Car, Brush, Truck, Loader2 } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";
import { useServices } from "@/hooks/use-api";

export const Route = createFileRoute("/services")({
  head: () => ({
    meta: [
      { title: "Services — MobileMechanic" },
      { name: "description", content: "Full catalog of mobile car services: battery, AC, oil, brakes, diagnostics, EV care and more." },
      { property: "og:title", content: "MobileMechanic Services" },
      { property: "og:description", content: "Premium on-demand car services delivered to you." },
    ],
  }),
  component: ServicesPage,
});

const iconMap: Record<string, any> = {
  oil: Droplets,
  ac: Wind,
  brake: Cog,
  battery: Battery,
  diagnostic: Gauge,
  tune: Wrench,
  ev: Zap,
  detail: Brush,
  roadside: Truck,
};

const defaultCats = [
  {
    name: "Maintenance",
    items: [
      { icon: Droplets, title: "Oil change", price: "from ₨ 4,500", desc: "Full-synthetic, with filter." },
      { icon: Wind, title: "AC service", price: "from ₨ 3,500", desc: "Re-gas, leak detection." },
      { icon: Cog, title: "Brake service", price: "from ₨ 6,500", desc: "Pads, rotors, fluid." },
    ],
  },
  {
    name: "Diagnostics & repairs",
    items: [
      { icon: Gauge, title: "OBD-II diagnostics", price: "from ₨ 1,500", desc: "Read & clear error codes." },
      { icon: Battery, title: "Battery service", price: "from ₨ 2,000", desc: "Test, jumpstart, replace." },
      { icon: Wrench, title: "Engine tune-up", price: "from ₨ 8,500", desc: "Spark plugs, filters." },
    ],
  },
  {
    name: "Premium care",
    items: [
      { icon: Zap, title: "EV diagnostics", price: "from ₨ 5,500", desc: "Hybrid & EV-certified." },
      { icon: Brush, title: "Detailing", price: "from ₨ 7,500", desc: "Interior + exterior." },
      { icon: Truck, title: "Roadside SOS", price: "from ₨ 2,500", desc: "Anywhere, anytime." },
    ],
  },
];

function ServicesPage() {
  const { data: services = [], isLoading, error } = useServices();

  // Group services by category if available
  const groupedServices = services.reduce((acc: Record<string, any[]>, service) => {
    const cat = service.category || "Other Services";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(service);
    return acc;
  }, {});

  const hasCategoryData = Object.keys(groupedServices).length > 0;

  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="Services"
            title={<>Everything your car needs, <span className="text-gradient-primary">at your door</span></>}
            description="Transparent prices. Certified specialists. Real OEM-grade parts with warranty."
          />
        </div>
      </section>

      <section className="container-page space-y-16 py-16">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-muted-foreground">Loading services...</span>
          </div>
        ) : error ? (
          <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-destructive">
            Failed to load services. Using default catalog.
          </div>
        ) : null}

        {hasCategoryData ? (
          Object.entries(groupedServices).map(([category, items]) => (
            <Reveal key={category}>
              <div className="mb-6 flex items-end justify-between">
                <h2 className="text-2xl font-bold tracking-tight">{category}</h2>
                <Link to="/signup" className="text-sm font-semibold text-primary hover:underline">Book now →</Link>
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {items.map((service) => {
                  const Icon = iconMap[service.name?.toLowerCase()] || Wrench;
                  const priceDisplay = service.price ? `₨ ${service.price}` : "Contact for pricing";
                  return (
                    <div key={service.id} className="group rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft transition-all hover:-translate-y-1 hover:shadow-elevated">
                      <div className="flex items-center justify-between">
                        <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                          <Icon className="h-5 w-5" />
                        </div>
                        <span className="rounded-full bg-success/15 px-2 py-1 text-xs font-semibold text-success">{priceDisplay}</span>
                      </div>
                      <h3 className="mt-5 text-lg font-semibold">{service.name}</h3>
                      <p className="mt-2 text-sm text-muted-foreground">{service.description || "Professional service included."}</p>
                    </div>
                  );
                })}
              </div>
            </Reveal>
          ))
        ) : (
          // Fallback to default categories if no API data
          defaultCats.map((c) => (
            <Reveal key={c.name}>
              <div className="mb-6 flex items-end justify-between">
                <h2 className="text-2xl font-bold tracking-tight">{c.name}</h2>
                <Link to="/signup" className="text-sm font-semibold text-primary hover:underline">Book now →</Link>
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {c.items.map((it) => (
                  <div key={it.title} className="group rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft transition-all hover:-translate-y-1 hover:shadow-elevated">
                    <div className="flex items-center justify-between">
                      <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                        <it.icon className="h-5 w-5" />
                      </div>
                      <span className="rounded-full bg-success/15 px-2 py-1 text-xs font-semibold text-success">{it.price}</span>
                    </div>
                    <h3 className="mt-5 text-lg font-semibold">{it.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{it.desc}</p>
                  </div>
                ))}
              </div>
            </Reveal>
          ))
        )}

        <div className="rounded-3xl border border-border bg-surface-elevated p-8 text-center md:p-12">
          <Sparkles className="mx-auto h-6 w-6 text-primary" />
          <h3 className="mt-3 text-2xl font-bold">Don't see your issue?</h3>
          <p className="mt-2 text-muted-foreground">Describe the problem in-app and we'll quote you within minutes.</p>
          <Link to="/signup" className="mt-5 inline-flex items-center gap-2 rounded-full bg-gradient-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-glow">
            <Car className="h-4 w-4" /> Get a custom quote
          </Link>
          <div className="mt-4 inline-flex items-center gap-2 text-xs text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5 text-primary" /> 30-day workmanship warranty
          </div>
        </div>
      </section>
    </div>
  );
}
