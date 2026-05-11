import { createFileRoute } from "@tanstack/react-router";
import { Apple, Smartphone, Star, ShieldCheck, Zap } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/download")({
  head: () => ({
    meta: [
      { title: "Download the MobileMechanic app" },
      { name: "description", content: "Available on iOS and Android. Book mechanics, track jobs, and pay in one app." },
      { property: "og:title", content: "Download MobileMechanic" },
      { property: "og:description", content: "Premium car care, on your phone." },
    ],
  }),
  component: DownloadPage,
});

function DownloadPage() {
  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page grid items-center gap-10 py-16 md:grid-cols-2 md:py-24">
          <Reveal>
            <SectionHeader
              align="left"
              eyebrow="Mobile apps"
              title={<>Your garage, <span className="text-gradient-primary">in your pocket</span></>}
              description="Book in 60 seconds, track in real-time, pay securely. Available on iOS and Android."
            />
            <div className="mt-7 flex flex-wrap gap-3">
              <a href="#" className="inline-flex items-center gap-3 rounded-2xl bg-foreground px-5 py-3 text-background shadow-elevated transition-transform hover:scale-[1.02]">
                <Apple className="h-7 w-7" />
                <div className="text-left leading-tight">
                  <div className="text-[10px] uppercase tracking-wider opacity-80">Download on the</div>
                  <div className="text-base font-semibold">App Store</div>
                </div>
              </a>
              <a href="#" className="inline-flex items-center gap-3 rounded-2xl bg-foreground px-5 py-3 text-background shadow-elevated transition-transform hover:scale-[1.02]">
                <Smartphone className="h-7 w-7" />
                <div className="text-left leading-tight">
                  <div className="text-[10px] uppercase tracking-wider opacity-80">Get it on</div>
                  <div className="text-base font-semibold">Google Play</div>
                </div>
              </a>
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-6 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-2"><Star className="h-4 w-4 fill-warning text-warning" /> 4.9 · 12k reviews</span>
              <span className="inline-flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-primary" /> Bank-grade security</span>
              <span className="inline-flex items-center gap-2"><Zap className="h-4 w-4 text-primary" /> Lightning fast</span>
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="relative mx-auto h-[560px] w-[280px]">
              <div className="absolute inset-0 -z-10 rounded-[3rem] bg-gradient-mesh opacity-50 blur-3xl" />
              <div className="relative h-full w-full overflow-hidden rounded-[2.5rem] border-4 border-foreground/80 bg-surface-elevated shadow-elevated">
                <div className="absolute left-1/2 top-2 h-5 w-24 -translate-x-1/2 rounded-full bg-foreground/80" />
                <div className="space-y-4 p-5 pt-12">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs text-muted-foreground">Good morning</div>
                      <div className="text-base font-semibold">Ali</div>
                    </div>
                    <div className="h-9 w-9 rounded-full bg-gradient-primary" />
                  </div>
                  <div className="rounded-2xl bg-gradient-primary p-4 text-primary-foreground shadow-glow">
                    <div className="text-xs opacity-90">Need help today?</div>
                    <div className="mt-1 text-lg font-semibold">Book a mechanic →</div>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {["Battery", "Oil", "AC", "Brakes", "Tires", "SOS"].map((s) => (
                      <div key={s} className="rounded-xl border border-border bg-background p-3 text-center text-[11px] font-medium">
                        {s}
                      </div>
                    ))}
                  </div>
                  <div className="rounded-2xl border border-border bg-background p-4">
                    <div className="text-xs text-muted-foreground">Active</div>
                    <div className="mt-1 flex items-center justify-between">
                      <div>
                        <div className="text-sm font-semibold">Bilal Ahmed</div>
                        <div className="text-[11px] text-muted-foreground">Arrives in 8 min</div>
                      </div>
                      <span className="rounded-full bg-success/15 px-2 py-1 text-[10px] font-semibold text-success">LIVE</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}
