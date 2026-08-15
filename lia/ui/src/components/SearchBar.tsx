export default function SearchBar() {
  return (
    <div style={{ margin: '1rem 0' }}>
      <input
        aria-label="Search workspace"
        placeholder="Search workspace"
        style={{ width: '100%', padding: '0.75rem', fontSize: '1rem' }}
      />
    </div>
  );
}
