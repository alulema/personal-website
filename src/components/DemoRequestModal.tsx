import { useState, useEffect } from 'react';

interface Props {
  locale: 'en' | 'es';
}

interface ModalState {
  open: boolean;
  projectId: string;
  projectTitle: string;
}

type FormStatus = 'idle' | 'submitting' | 'success' | 'error';

const copy = {
  en: {
    heading:     (title: string) => `Request access to "${title}"`,
    subheading:  'This demo runs on Azure. I\'ll review your request and spin it up for 1 hour.',
    name:        'Your name',
    email:       'Your email',
    reason:      'Why are you interested? (optional)',
    reasonHint:  'e.g. I\'m exploring RAG architectures for a project',
    submit:      'Send request',
    submitting:  'Sending…',
    success:     'Request sent! You\'ll receive an email once I approve it.',
    error:       'Something went wrong. Please try again.',
    close:       'Close',
    cancel:      'Cancel',
  },
  es: {
    heading:     (title: string) => `Solicitar acceso a "${title}"`,
    subheading:  'Este demo corre en Azure. Revisaré tu solicitud y lo activaré por 1 hora.',
    name:        'Tu nombre',
    email:       'Tu correo',
    reason:      '¿Por qué te interesa? (opcional)',
    reasonHint:  'Ej. Estoy explorando arquitecturas RAG para un proyecto',
    submit:      'Enviar solicitud',
    submitting:  'Enviando…',
    success:     '¡Solicitud enviada! Recibirás un email cuando la apruebe.',
    error:       'Algo salió mal. Por favor intenta de nuevo.',
    close:       'Cerrar',
    cancel:      'Cancelar',
  },
};

export default function DemoRequestModal({ locale }: Props) {
  const t = copy[locale];

  const [modal, setModal]   = useState<ModalState>({ open: false, projectId: '', projectTitle: '' });
  const [name, setName]     = useState('');
  const [email, setEmail]   = useState('');
  const [reason, setReason] = useState('');
  const [status, setStatus] = useState<FormStatus>('idle');

  useEffect(() => {
    const handler = (e: Event) => {
      const { id, title } = (e as CustomEvent).detail as { id: string; title: string };
      setModal({ open: true, projectId: id, projectTitle: title });
      setStatus('idle');
      setName('');
      setEmail('');
      setReason('');
    };
    window.addEventListener('open-demo-request', handler);
    return () => window.removeEventListener('open-demo-request', handler);
  }, []);

  // Close on Escape
  useEffect(() => {
    if (!modal.open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') close(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [modal.open]);

  function close() {
    setModal(m => ({ ...m, open: false }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('submitting');
    try {
      const res = await fetch('/api/demo/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectId: modal.projectId,
          name,
          email,
          reason,
        }),
      });
      setStatus(res.ok ? 'success' : 'error');
    } catch {
      setStatus('error');
    }
  }

  if (!modal.open) return null;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onClick={e => { if (e.target === e.currentTarget) close(); }}
    >
      <div className="modal-panel">
        <button className="modal-close" onClick={close} aria-label={t.close}>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>

        <h2 id="modal-title" className="modal-title">{t.heading(modal.projectTitle)}</h2>
        <p className="modal-sub">{t.subheading}</p>

        {status === 'success' ? (
          <div className="modal-success">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <p>{t.success}</p>
            <button className="btn-secondary" onClick={close}>{t.close}</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="modal-form">
            <div className="field">
              <label htmlFor="req-name">{t.name}</label>
              <input
                id="req-name"
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                required
                autoComplete="name"
                disabled={status === 'submitting'}
              />
            </div>

            <div className="field">
              <label htmlFor="req-email">{t.email}</label>
              <input
                id="req-email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoComplete="email"
                disabled={status === 'submitting'}
              />
            </div>

            <div className="field">
              <label htmlFor="req-reason">{t.reason}</label>
              <textarea
                id="req-reason"
                value={reason}
                onChange={e => setReason(e.target.value)}
                placeholder={t.reasonHint}
                rows={3}
                disabled={status === 'submitting'}
              />
            </div>

            {status === 'error' && (
              <p className="form-error">{t.error}</p>
            )}

            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={close} disabled={status === 'submitting'}>
                {t.cancel}
              </button>
              <button type="submit" className="btn-primary" disabled={status === 'submitting'}>
                {status === 'submitting' ? t.submitting : t.submit}
              </button>
            </div>
          </form>
        )}
      </div>

      <style>{`
        .modal-backdrop {
          position: fixed;
          inset: 0;
          z-index: 100;
          background: rgba(0,0,0,0.6);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1rem;
        }
        .modal-panel {
          background: var(--color-bg-card);
          border: 1px solid var(--color-border);
          border-radius: 1rem;
          padding: 2rem;
          width: 100%;
          max-width: 28rem;
          position: relative;
          box-shadow: 0 25px 50px rgba(0,0,0,0.4);
        }
        .modal-close {
          position: absolute;
          top: 1rem;
          right: 1rem;
          background: none;
          border: none;
          color: var(--color-text-muted);
          cursor: pointer;
          padding: 0.25rem;
          border-radius: 0.25rem;
          transition: color 150ms ease;
        }
        .modal-close:hover { color: var(--color-text); }
        .modal-title {
          font-size: 1.125rem;
          font-weight: 700;
          margin: 0 0 0.5rem;
          color: var(--color-text);
          padding-right: 2rem;
        }
        .modal-sub {
          font-size: 0.875rem;
          color: var(--color-text-muted);
          margin: 0 0 1.5rem;
          line-height: 1.6;
        }
        .modal-form { display: flex; flex-direction: column; gap: 1rem; }
        .field { display: flex; flex-direction: column; gap: 0.375rem; }
        .field label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text);
        }
        .field input,
        .field textarea {
          background: var(--color-bg-secondary);
          border: 1px solid var(--color-border);
          border-radius: 0.5rem;
          padding: 0.625rem 0.875rem;
          color: var(--color-text);
          font-size: 0.9375rem;
          font-family: var(--font-sans);
          transition: border-color 150ms ease;
          resize: vertical;
        }
        .field input:focus,
        .field textarea:focus {
          outline: none;
          border-color: var(--color-accent);
        }
        .field input:disabled,
        .field textarea:disabled { opacity: 0.6; }
        .form-error {
          font-size: 0.875rem;
          color: #f87171;
          margin: 0;
        }
        .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          margin-top: 0.5rem;
        }
        .btn-primary {
          padding: 0.625rem 1.25rem;
          border-radius: 0.5rem;
          background-color: var(--color-accent);
          color: #0a0f1e;
          font-weight: 600;
          font-size: 0.9375rem;
          border: none;
          cursor: pointer;
          transition: background-color 150ms ease;
        }
        .btn-primary:hover:not(:disabled) { background-color: var(--color-accent-hover); }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-secondary {
          padding: 0.625rem 1.25rem;
          border-radius: 0.5rem;
          border: 1px solid var(--color-border);
          background: none;
          color: var(--color-text);
          font-weight: 600;
          font-size: 0.9375rem;
          cursor: pointer;
          transition: border-color 150ms ease, background-color 150ms ease;
        }
        .btn-secondary:hover:not(:disabled) {
          border-color: var(--color-accent);
          background-color: var(--color-bg-secondary);
        }
        .btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
        .modal-success {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
          padding: 1.5rem 0;
          text-align: center;
        }
        .modal-success p {
          color: var(--color-text-muted);
          font-size: 0.9375rem;
          margin: 0;
        }
      `}</style>
    </div>
  );
}
