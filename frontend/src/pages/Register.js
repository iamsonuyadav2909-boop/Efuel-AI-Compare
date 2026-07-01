import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Logo } from '@/components/shared/Logo';
import { motion } from 'framer-motion';
import { Loader2, UserPlus } from 'lucide-react';
import { toast } from 'sonner';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('engineer');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await register(name, email, password, role);
    setLoading(false);
    if (res.success) {
      toast.success('Account created — welcome to EFUEL Engineering Hub');
      navigate('/dashboard', { replace: true });
    } else {
      toast.error(res.message);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary/30 px-6 py-12">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}
        className="w-full max-w-sm rounded-2xl border bg-card p-8 shadow-[var(--shadow-md)]">
        <div className="mb-6 flex justify-center"><Logo /></div>
        <h2 className="text-center font-display text-2xl font-semibold tracking-tight">Create your account</h2>
        <p className="mt-1 text-center text-sm text-muted-foreground">Join the EFUEL engineering workspace</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="name">Full name</Label>
            <Input id="name" required value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" data-testid="register-name-input" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="reg-email">Email</Label>
            <Input id="reg-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@efuel.com" data-testid="register-email-input" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="reg-password">Password</Label>
            <Input id="reg-password" type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min. 6 characters" data-testid="register-password-input" />
          </div>
          <div className="space-y-1.5">
            <Label>Role</Label>
            <Select value={role} onValueChange={setRole}>
              <SelectTrigger data-testid="register-role-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="engineer">Engineer — full research & compare access</SelectItem>
                <SelectItem value="viewer">Viewer — read-only access</SelectItem>
                <SelectItem value="admin">Admin — full platform administration</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">Role determines platform permissions; an administrator can change this later.</p>
          </div>
          <Button type="submit" className="w-full" disabled={loading} data-testid="register-submit-button">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <UserPlus className="h-4 w-4" />}
            Create account
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-primary hover:underline" data-testid="register-login-link">Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
