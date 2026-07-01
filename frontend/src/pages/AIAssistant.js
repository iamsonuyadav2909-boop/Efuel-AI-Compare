import { useState, useEffect, useRef } from 'react';
import api, { getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { EmptyState } from '@/components/shared/EmptyState';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { MessageSquareText, Send, Loader2, Sparkles, Plus } from 'lucide-react';

const EXAMPLES = [
  'Compare Schneider MCCB vs ABB MCCB',
  'Suggest SPD for 60kW EV Charger',
  'Alternative to Siemens Contactor',
  'Best Solar DC Isolator',
  'Best Energy Meter',
];

export default function AIAssistant() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  const loadSessions = () => {
    api.get('/chat/sessions').then((res) => setSessions(res.data)).catch(() => {});
  };

  useEffect(() => { loadSessions(); }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const loadSession = async (sid) => {
    setSessionId(sid);
    const res = await api.get(`/chat/sessions/${sid}`);
    setMessages(res.data.messages || []);
  };

  const startNewChat = () => {
    setSessionId(null);
    setMessages([]);
  };

  const sendMessage = async (text) => {
    const messageText = (text || input).trim();
    if (!messageText || loading) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: messageText }]);
    setLoading(true);
    try {
      const res = await api.post('/chat', { message: messageText, session_id: sessionId });
      setSessionId(res.data.session_id);
      setMessages((m) => [...m, { role: 'assistant', content: res.data.reply }]);
      loadSessions();
    } catch (error) {
      toast.error(getErrorMessage(error, 'AI Assistant could not respond.'));
      setMessages((m) => m.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <PageHeader title="AI Assistant" description="Ask engineering questions grounded in real component research data." />

      <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-12">
        <div className="hidden flex-col rounded-xl border bg-card lg:col-span-3 lg:flex">
          <div className="border-b p-3">
            <Button variant="outline" className="w-full" onClick={startNewChat} data-testid="new-chat-button">
              <Plus className="h-4 w-4" /> New Chat
            </Button>
          </div>
          <div className="flex-1 space-y-1 overflow-y-auto scrollbar-thin p-2">
            {sessions.map((s) => (
              <button
                key={s.session_id}
                onClick={() => loadSession(s.session_id)}
                className={`block w-full truncate rounded-lg px-3 py-2 text-left text-xs ${sessionId === s.session_id ? 'bg-accent text-foreground' : 'text-muted-foreground hover:bg-secondary/60'}`}
                data-testid="chat-session-item"
              >
                {s.messages?.[0]?.content?.slice(0, 40) || 'New conversation'}
              </button>
            ))}
          </div>
        </div>

        <div className="flex min-h-0 flex-col rounded-xl border bg-card lg:col-span-9">
          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto scrollbar-thin p-5">
            {messages.length === 0 ? (
              <EmptyState
                icon={MessageSquareText}
                title="Ask the EFUEL Engineering Assistant"
                description="Get instant, grounded answers about EV charging and solar components."
                action={(
                  <div className="flex flex-wrap justify-center gap-2">
                    {EXAMPLES.map((ex) => (
                      <button key={ex} onClick={() => sendMessage(ex)}
                        className="rounded-full border bg-secondary/40 px-3 py-1.5 text-xs font-medium hover:bg-accent"
                        data-testid="assistant-example-chip">
                        {ex}
                      </button>
                    ))}
                  </div>
                )}
              />
            ) : (
              messages.map((m, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary/60 text-foreground'}`}
                    data-testid={m.role === 'user' ? 'chat-user-message' : 'chat-assistant-message'}>
                    {m.content}
                  </div>
                </motion.div>
              ))
            )}
            {loading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Thinking...
              </div>
            )}
          </div>
          <form
            onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
            className="flex items-end gap-2 border-t p-3"
          >
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="Ask about any EV/solar component..."
              className="min-h-[44px] flex-1 resize-none"
              data-testid="assistant-message-input"
            />
            <Button type="submit" disabled={loading || !input.trim()} data-testid="assistant-send-button">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
