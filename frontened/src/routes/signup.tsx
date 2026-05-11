import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { Loader2, Check, X } from "lucide-react";
import { ApiError, endpoints } from "@/lib/api";
import { AuthShell, Field } from "./login";

// Password validation rules
function validatePassword(pwd: string) {
  return {
    length: pwd.length >= 8,
    uppercase: /[A-Z]/.test(pwd),
    lowercase: /[a-z]/.test(pwd),
    digit: /[0-9]/.test(pwd),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
  };
}

function isStrongPassword(pwd: string): boolean {
  const rules = validatePassword(pwd);
  return Object.values(rules).every(r => r);
}

export const Route = createFileRoute("/signup")({
  head: () => ({ meta: [{ title: "Create account — MobileMechanic" }] }),
  component: SignupPage,
});

function SignupPage() {
  const navigate = useNavigate();
  const [first, setFirst] = useState("");
  const [last, setLast] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate password length
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters long");
      return;
    }
    
    // Validate password strength
    if (!isStrongPassword(password)) {
      toast.error("Password must contain uppercase, lowercase, digit, and special character");
      return;
    }
    
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await endpoints.signup({
        phone_number: phone,
        email,
        password,
        password_confirm: confirmPassword,
        first_name: first,
        last_name: last,
      });
      toast.success("Account created! Please sign in.");
      navigate({ to: "/login" });
    } catch (err) {
      console.error("Signup error:", err);
      let msg = "Could not create account";
      if (err instanceof ApiError) {
        msg = err.message;
        if (err.data && typeof err.data === "object") {
          const errData = err.data as any;
          // Handle multiple error formats from backend
          if (errData.detail) msg = errData.detail;
          if (errData.message) msg = errData.message;
          if (errData.email) msg = `Email: ${Array.isArray(errData.email) ? errData.email[0] : errData.email}`;
          if (errData.phone_number) msg = `Phone: ${Array.isArray(errData.phone_number) ? errData.phone_number[0] : errData.phone_number}`;
          if (errData.password) msg = `Password: ${Array.isArray(errData.password) ? errData.password[0] : errData.password}`;
          if (errData.non_field_errors) msg = Array.isArray(errData.non_field_errors) ? errData.non_field_errors[0] : errData.non_field_errors;
        }
      }
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Create your account" subtitle="Start booking premium car care in minutes.">
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="First name" value={first} onChange={setFirst} required />
          <Field label="Last name" value={last} onChange={setLast} required />
        </div>
        <Field label="Phone number" value={phone} onChange={setPhone} type="tel" placeholder="+923001234567" required />
        <Field label="Email" value={email} onChange={setEmail} type="email" placeholder="you@example.com" required />
        <div>
          <Field label="Password" value={password} onChange={setPassword} type="password" placeholder="At least 8 characters with uppercase, lowercase, digit, and special char" required />
          <div className="mt-2.5 space-y-1.5">
            <PasswordRequirement 
              label="At least 8 characters" 
              met={validatePassword(password).length} 
            />
            <PasswordRequirement 
              label="Uppercase letter (A-Z)" 
              met={validatePassword(password).uppercase} 
            />
            <PasswordRequirement 
              label="Lowercase letter (a-z)" 
              met={validatePassword(password).lowercase} 
            />
            <PasswordRequirement 
              label="Digit (0-9)" 
              met={validatePassword(password).digit} 
            />
            <PasswordRequirement 
              label="Special character (@, !, #, $, %, etc.)" 
              met={validatePassword(password).special} 
            />
          </div>
        </div>
        <Field label="Confirm Password" value={confirmPassword} onChange={setConfirmPassword} type="password" placeholder="Repeat password" required />

        <button
          type="submit"
          disabled={loading || !isStrongPassword(password) || password !== confirmPassword}
          className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-glow disabled:opacity-70"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          {loading ? "Creating..." : "Create account"}
        </button>

        <p className="text-center text-xs text-muted-foreground">
          By continuing you agree to our <a href="#" className="underline">Terms</a> and <a href="#" className="underline">Privacy Policy</a>.
        </p>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-primary hover:underline">Sign in</Link>
        </p>
      </form>
    </AuthShell>
  );
}

function PasswordRequirement({ label, met }: { label: string; met: boolean }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      {met ? (
        <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
      ) : (
        <X className="h-4 w-4 text-red-600 flex-shrink-0" />
      )}
      <span className={met ? "text-green-600 font-medium" : "text-muted-foreground"}>
        {label}
      </span>
    </div>
  );
}
