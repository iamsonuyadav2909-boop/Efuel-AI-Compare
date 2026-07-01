import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Logo } from '@/components/shared/Logo';
import { motion } from 'framer-motion';
import { ShieldCheck, Loader2, Zap } from 'lucide-react';
import { toast } from 'sonner';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await login(email, password);
    setLoading(false);
    if (res.success) {
      toast.success('Welcome back to EFUEL Engineering Hub');
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true });
    } else {
      toast.error(res.message);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-[#0a0e14] p-10 text-white lg:flex noise-overlay">
        <div className="absolute inset-0" style={{ background: 'radial-gradient(1200px circle at 10% 0%, rgba(59,130,246,0.18), transparent 55%), radial-gradient(900px circle at 90% 10%, rgba(14,165,233,0.12), transparent 50%)' }} />
        <Logo dark className="relative z-10" />
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="relative z-10 max-w-md">
          <h1 className="font-display text-4xl font-semibold leading-tight tracking-tight">
            Engineering decisions, backed by AI research.
          </h1>
          <p className="mt-4 text-sm text-white/70">
            Search any EV charger or solar component and get AI-ranked recommendations, engineering
            scores and defensible sourcing — in seconds, not hours.
          </p>
          <div className="mt-8 flex items-center gap-3 text-xs text-white/60">
            <ShieldCheck className="h-4 w-4 text-primary" />
            Internal use only — EFUEL engineering & procurement teams
          </div>
        </motion.div>
        <p className="relative z-10 text-xs text-white/40">© {new Date().getFullYear()} EFUEL Engineering Hub</p>
      </div>

      <div className="flex flex-col items-center justify-center px-6 py-12">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }} className="w-full max-w-sm">
          <div className="mb-8 flex justify-center lg:hidden">
            <Logo />
          </div>
          <h2 className="font-display text-2xl font-semibold tracking-tight">Sign in</h2>
          <p className="mt-1 text-sm text-muted-foreground">Access your engineering workspace</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="you@efuel.com" data-testid="login-email-input" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••" data-testid="login-password-input" />
            </div>
            <Button type="submit" className="w-full" disabled={loading} data-testid="login-submit-button">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
              Sign in
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Private workspace &mdash; access is limited to the EFUEL engineering team.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
