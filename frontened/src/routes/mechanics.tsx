import { createFileRoute, Link } from "@tanstack/react-router";
import { Star, MapPin, Loader2, Award } from "lucide-react";
import { useMechanics, useMechanicReviews } from "@/hooks/use-api";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/mechanics")({
  head: () => ({
    meta: [
      { title: "Our Mechanics — MobileMechanic" },
      { name: "description", content: "Browse our network of certified mechanics. Real professionals with ratings and specializations." },
    ],
  }),
  component: MechanicsPage,
});

function MechanicsPage() {
  const { data: mechanics = [], isLoading, error } = useMechanics();

  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="Our Network"
            title={<>Certified professionals <span className="text-gradient-primary">you can trust</span></>}
            description="Meet the mechanics keeping you on the road. All verified, rated, and insured."
          />
        </div>
      </section>

      <section className="container-page py-16">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-muted-foreground">Loading mechanics...</span>
          </div>
        ) : error ? (
          <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-destructive">
            Failed to load mechanics. Please try again later.
          </div>
        ) : mechanics.length === 0 ? (
          <div className="rounded-lg border border-border bg-surface-elevated p-8 text-center">
            <p className="text-muted-foreground">No mechanics available at the moment. Check back soon!</p>
          </div>
        ) : (
          <Reveal>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {mechanics.map((mechanic) => (
                <MechanicCard key={mechanic.id} mechanic={mechanic} />
              ))}
            </div>
          </Reveal>
        )}
      </section>
    </div>
  );
}

function MechanicCard({ mechanic }: { mechanic: any }) {
  const { data: reviews = [] } = useMechanicReviews(mechanic.id);

  const avgRating =
    reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
      : mechanic.rating || 0;

  return (
    <div className="group flex flex-col rounded-2xl border border-border bg-surface-elevated p-6 shadow-soft transition-all hover:-translate-y-1 hover:shadow-elevated">
      {/* Avatar */}
      <div className="relative mb-4">
        <div className="h-24 w-full rounded-xl bg-gradient-primary/20"></div>
        <div className="absolute -bottom-4 left-1/2 h-16 w-16 -translate-x-1/2 rounded-full border-4 border-background bg-gradient-to-br from-primary to-primary/80 shadow-md"></div>
      </div>

      {/* Name & Title */}
      <div className="mt-6 text-center">
        <h3 className="text-lg font-semibold">
          {mechanic.user?.first_name} {mechanic.user?.last_name}
        </h3>
        <p className="text-sm text-muted-foreground">{mechanic.specialization || "General Mechanic"}</p>
      </div>

      {/* Rating */}
      <div className="mt-4 flex items-center justify-center gap-1">
        <div className="flex items-center gap-0.5">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={`h-4 w-4 ${
                i < Math.round(Number(avgRating))
                  ? "fill-yellow-400 text-yellow-400"
                  : "text-muted-foreground"
              }`}
            />
          ))}
        </div>
        <span className="text-sm font-semibold">{avgRating}</span>
        <span className="text-xs text-muted-foreground">({reviews.length})</span>
      </div>

      {/* Details */}
      <div className="mt-4 space-y-2 border-t border-border pt-4">
        {mechanic.hourly_rate && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Hourly rate:</span>
            <span className="font-semibold">₨ {mechanic.hourly_rate}</span>
          </div>
        )}
        {mechanic.location && (
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground truncate">{mechanic.location}</span>
          </div>
        )}
        <div className="flex items-center gap-2 text-sm">
          <Award className="h-4 w-4 text-primary" />
          <span className="text-muted-foreground">
            {mechanic.is_available ? "Available now" : "Unavailable"}
          </span>
        </div>
      </div>

      {/* CTA */}
      <Link
        to="/signup"
        className="mt-4 w-full rounded-lg bg-gradient-primary py-2 text-center text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
      >
        Book now
      </Link>
    </div>
  );
}
