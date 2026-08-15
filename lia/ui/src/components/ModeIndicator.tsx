type ModeIndicatorProps = {
  mode: 'research' | 'concentration' | 'developer';
};

export default function ModeIndicator({ mode }: ModeIndicatorProps) {
  return (
    <div
      style={{
        display: 'inline-block',
        padding: '0.35rem 0.75rem',
        background: '#e5e7eb',
        borderRadius: '999px',
        fontWeight: 600,
        textTransform: 'capitalize',
      }}
    >
      mode: {mode}
    </div>
  );
}
