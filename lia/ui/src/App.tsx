import React from 'react';
import SearchBar from './components/SearchBar';
import WorkspaceView from './components/WorkspaceView';
import ModeIndicator from './components/ModeIndicator';

export default function App() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <ModeIndicator mode="research" />
      <h1>LIA</h1>
      <SearchBar />
      <WorkspaceView />
    </main>
  );
}
