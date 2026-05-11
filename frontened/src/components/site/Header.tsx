import { useEffect, useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { Menu, X, Wrench, LogOut } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { auth } from "@/lib/api";
import { useProfile } from "@/hooks/use-api";

const links = [
  { to: "/services", label: "Services" },
  { to: "/mechanics", label: "Mechanics" },
  { to: "/how-it-works", label: "How it works" },
  { to: "/for-mechanics", label: "For mechanics" },
  { to: "/pricing", label: "Pricing" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { data: profile } = useProfile();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleLogout = () => {
    auth.clear();
    navigate({ to: "/" });
  };

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all ${
        scrolled ? "glass shadow-soft" : "bg-transparent"
      }`}
    >
      <div className="container-page flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold tracking-tight">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-primary text-primary-foreground shadow-glow">
            <Wrench className="h-4 w-4" />
          </span>
          MobileMechanic
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              activeProps={{ className: "rounded-md px-3 py-2 text-sm font-semibold text-foreground bg-accent" }}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <ThemeToggle />
          {auth.token && profile ? (
            <>
              <Link
                to="/bookings"
                className="rounded-md px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
              >
                My Bookings
              </Link>
              <div className="flex items-center gap-2 border-l border-border pl-2">
                <div className="h-8 w-8 rounded-full bg-gradient-primary" />
                <span className="text-sm font-medium">{profile.first_name}</span>
              </div>
              <button
                onClick={handleLogout}
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-md px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className="inline-flex items-center justify-center rounded-md bg-gradient-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-glow transition-transform hover:scale-[1.02]"
              >
                Get started
              </Link>
            </>
          )}
        </div>

        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-border bg-surface-elevated md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border bg-surface-elevated md:hidden">
          <div className="container-page flex flex-col gap-1 py-3">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className="rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
              >
                {l.label}
              </Link>
            ))}
            {auth.token && profile && (
              <Link
                to="/bookings"
                onClick={() => setOpen(false)}
                className="rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
              >
                My Bookings
              </Link>
            )}
            <div className="mt-2 flex items-center gap-2">
              <ThemeToggle />
              {auth.token && profile ? (
                <>
                  <div className="flex-1 rounded-md border border-border px-3 py-2 text-center text-sm">
                    {profile.first_name}
                  </div>
                  <button
                    onClick={() => {
                      handleLogout();
                      setOpen(false);
                    }}
                    className="flex-1 rounded-md border border-border px-3 py-2 text-center text-sm"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" onClick={() => setOpen(false)} className="flex-1 rounded-md border border-border px-3 py-2 text-center text-sm">
                    Sign in
                  </Link>
                  <Link to="/signup" onClick={() => setOpen(false)} className="flex-1 rounded-md bg-gradient-primary px-3 py-2 text-center text-sm font-semibold text-primary-foreground">
                    Get started
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
