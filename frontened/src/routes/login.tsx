import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { ArrowLeft, Loader2, Wrench } from "lucide-react";
import { ApiError, auth, endpoints } from "@/lib/api";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Sign in — MobileMechanic" }] }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await endpoints.login({ phone_number: phone, password });
      if (res?.token) auth.set(res.token);
      toast.success("Welcome back!");
      navigate({ to: "/" });
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Could not sign in";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return <AuthShell title="Welcome back" subtitle="Sign in to manage your bookings.">
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="Phone number" value={phone} onChange={setPhone} type="tel" placeholder="+923001234567" required />
      <Field label="Password" value={password} onChange={setPassword} type="password" placeholder="••••••••" required />
      <button
        type="submit"
        disabled={loading}
        className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-glow disabled:opacity-70"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {loading ? "Signing in..." : "Sign in"}
      </button>
      <p className="text-center text-sm text-muted-foreground">
        New here? <Link to="/signup" className="font-semibold text-primary hover:underline">Create account</Link>
      </p>
    </form>
  </AuthShell>;
}

export function AuthShell({ children, title, subtitle }: { children: React.ReactNode; title: string; subtitle: string }) {
  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="relative hidden overflow-hidden bg-gradient-primary text-primary-foreground md:block">
        <div className="absolute inset-0 grid-pattern opacity-20" />
        <div className="relative flex h-full flex-col p-10">
          <Link to="/" className="inline-flex items-center gap-2 font-display text-lg font-bold">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-background/15 backdrop-blur">
              <Wrench className="h-4 w-4" />
            </span>
            MobileMechanic
          </Link>
          <div className="mt-auto">
            <h2 className="text-3xl font-bold leading-tight md:text-4xl">A premium garage, on your phone.</h2>
            <p className="mt-3 max-w-sm opacity-90">Live tracking. Transparent pricing. Certified mechanics. Built for modern drivers.</p>
          </div>
        </div>
      </div>
      <div className="relative flex flex-col bg-background">
        <div className="p-6">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" /> Back to home
          </Link>
        </div>
        <div className="m-auto w-full max-w-sm px-6 py-10">
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
          <div className="mt-8">{children}</div>
        </div>
      </div>
    </div>
  );
}

export function Field({
  label, value, onChange, type = "text", placeholder, required,
}: {
  label: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string; required?: boolean;
}) {
  return (
    <label className="block">
      <div className="mb-1.5 text-xs font-semibold text-muted-foreground">{label}</div>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full rounded-xl border border-input bg-surface-elevated px-4 py-3 text-sm outline-none ring-ring/40 transition-all focus:ring-2"
      />
    </label>
  );
}
