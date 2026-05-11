import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { Mail, MapPin, Phone } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact — MobileMechanic" },
      { name: "description", content: "Get in touch with the MobileMechanic team. Sales, support, partnerships." },
      { property: "og:title", content: "Contact MobileMechanic" },
      { property: "og:description", content: "Reach our team for support, sales or partnerships." },
    ],
  }),
  component: ContactPage,
});

function ContactPage() {
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      (e.target as HTMLFormElement).reset();
      toast.success("Message sent — we'll be in touch within 1 business day.");
    }, 700);
  };

  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="Contact"
            title={<>Let's <span className="text-gradient-primary">talk</span></>}
            description="Sales, support, partnerships — we usually reply in under 4 hours."
          />
        </div>
      </section>

      <section className="container-page grid gap-10 py-16 md:grid-cols-3">
        <Reveal className="md:col-span-2">
          <form onSubmit={onSubmit} className="rounded-3xl border border-border bg-surface-elevated p-8 shadow-soft">
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="First name" name="firstName" required />
              <Field label="Last name" name="lastName" required />
              <Field label="Email" name="email" type="email" required />
              <Field label="Phone" name="phone" type="tel" />
            </div>
            <div className="mt-4">
              <label className="mb-1.5 block text-xs font-semibold text-muted-foreground">Message</label>
              <textarea
                name="message"
                required
                rows={5}
                className="w-full rounded-xl border border-input bg-background px-4 py-3 text-sm outline-none ring-ring/40 transition-all focus:ring-2"
                placeholder="How can we help?"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="mt-6 inline-flex items-center justify-center rounded-full bg-gradient-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-glow disabled:opacity-70"
            >
              {loading ? "Sending..." : "Send message"}
            </button>
          </form>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="space-y-3">
            <ContactCard icon={Mail} title="Email" value="hello@mobilemechanic.app" />
            <ContactCard icon={Phone} title="Phone" value="+92 300 123 4567" />
            <ContactCard icon={MapPin} title="HQ" value="Lahore, Pakistan" />
          </div>
        </Reveal>
      </section>
    </div>
  );
}

function Field({ label, name, type = "text", required }: { label: string; name: string; type?: string; required?: boolean }) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-semibold text-muted-foreground">{label}</label>
      <input
        name={name}
        type={type}
        required={required}
        className="w-full rounded-xl border border-input bg-background px-4 py-3 text-sm outline-none ring-ring/40 transition-all focus:ring-2"
      />
    </div>
  );
}

function ContactCard({ icon: Icon, title, value }: { icon: React.ComponentType<{ className?: string }>; title: string; value: string }) {
  return (
    <div className="flex items-start gap-4 rounded-2xl border border-border bg-surface-elevated p-5 shadow-soft">
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{title}</div>
        <div className="mt-1 text-sm font-medium">{value}</div>
      </div>
    </div>
  );
}
