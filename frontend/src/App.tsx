import { useState } from 'react'

interface NavItem {
  id: string
  label: string
  icon: string
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'oracle', label: 'Oracle', icon: '🔮' },
  { id: 'bugs', label: 'Bugs', icon: '🐛' },
  { id: 'fix-loops', label: 'Fix Loops', icon: '🔄' },
  { id: 'fuzzer', label: 'Fuzzer', icon: '🧪' },
  { id: 'dreamer', label: 'Dreamer', icon: '💭' },
  { id: 'cartographer', label: 'Cartographer', icon: '🗺️' },
  { id: 'historian', label: 'Historian', icon: '📜' },
  { id: 'learner', label: 'Learner', icon: '🎓' },
  { id: 'quarantine', label: 'Quarantine', icon: '🚫' },
  { id: 'extinction', label: 'Extinction', icon: '☠️' },
  { id: 'economist', label: 'Economist', icon: '💰' },
  { id: 'pathogen-registry', label: 'Pathogen Registry', icon: '🦠' },
  { id: 'metrics', label: 'Metrics', icon: '📈' },
  { id: 'audit-log', label: 'Audit Log', icon: '📋' },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
]

function Sidebar({ activeView, onViewChange }: { activeView: string; onViewChange: (id: string) => void }) {
  return (
    <aside className="w-64 bg-[#0a0e1a] border-r border-[#1e2430] flex flex-col h-full">
      <div className="p-4 border-b border-[#1e2430]">
        <h1 className="text-lg font-semibold text-[#4fd1c5] flex items-center gap-2">
          <span className="text-2xl">🔬</span>
          <span>RepoMedic</span>
        </h1>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              activeView === item.id
                ? 'bg-[#1e2430] text-[#4fd1c5]'
                : 'text-[#94a3b8] hover:bg-[#11141d] hover:text-[#e2e8f0]'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-3 border-t border-[#1e2430] text-xs text-[#565f76]">
        v0.1.0 · Local-first debugging
      </div>
    </aside>
  )
}

function Header({ activeView }: { activeView: string }) {
  const viewLabels: Record<string, string> = {
    overview: 'Overview',
    oracle: 'Oracle',
    bugs: 'Bugs',
    'fix-loops': 'Fix Loops',
    fuzzer: 'Fuzzer',
    dreamer: 'Dreamer',
    cartographer: 'Cartographer',
    historian: 'Historian',
    learner: 'Learner',
    quarantine: 'Quarantine',
    extinction: 'Extinction',
    economist: 'Economist',
    'pathogen-registry': 'Pathogen Registry',
    metrics: 'Metrics',
    'audit-log': 'Audit Log',
    settings: 'Settings',
  }

  return (
    <header className="h-14 bg-[#0a0e1a] border-b border-[#1e2430] flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-medium text-[#e2e8f0]">
          {viewLabels[activeView] || activeView}
        </h2>
        <span className="px-2 py-0.5 text-xs bg-[#1e2430] text-[#4fd1c5] rounded">
          LIVE
        </span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-xs text-[#565f76]">System Nominal</span>
        <div className="w-2 h-2 bg-[#4fd1c5] rounded-full animate-pulse" />
      </div>
    </header>
  )
}

function CartographerView() {
  const [selectedNode] = useState<string | null>(null)

  const hotFiles = [
    { name: 'src/calc.py', indegree: 12, icon: '🔥' },
    { name: 'src/sequence.py', indegree: 8, icon: '🔥' },
    { name: 'src/compare.py', indegree: 6, icon: '🔥' },
    { name: 'src/loop.py', indegree: 4, icon: '🔥' },
  ]

  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#11141d] border border-[#1e2430] rounded-lg p-4">
            <h3 className="text-sm font-medium text-[#94a3b8] mb-4">Causal Graph</h3>
            <div className="h-[500px] bg-[#0a0e1a] border border-[#1e2430] rounded-lg relative overflow-hidden">
              <svg className="w-full h-full" viewBox="0 0 800 500">
                <defs>
                  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#4fd1c5" />
                  </marker>
                </defs>
                <line x1="100" y1="100" x2="300" y2="200" stroke="#1e2430" strokeWidth="1.5" markerEnd="url(#arrowhead)" />
                <line x1="100" y1="100" x2="400" y2="100" stroke="#1e2430" strokeWidth="1.5" markerEnd="url(#arrowhead)" />
                <line x1="300" y1="200" x2="500" y2="200" stroke="#1e2430" strokeWidth="1.5" markerEnd="url(#arrowhead)" />
                <line x1="400" y1="100" x2="500" y2="200" stroke="#1e2430" strokeWidth="1.5" markerEnd="url(#arrowhead)" />
                <line x1="500" y1="200" x2="600" y2="300" stroke="#1e2430" strokeWidth="1.5" markerEnd="url(#arrowhead)" />
                <circle cx="100" cy="100" r="28" fill="#4fd1c5" stroke="#4fd1c5" strokeWidth="2" />
                <text x="100" y="105" textAnchor="middle" fill="#0a0e1a" fontSize="10" fontWeight="bold" fontFamily="monospace">calc.py</text>
                <circle cx="300" cy="200" r="28" fill="#38bdb3" stroke="#38bdb3" strokeWidth="2" />
                <text x="300" y="205" textAnchor="middle" fill="#0a0e1a" fontSize="10" fontFamily="monospace">sequence.py</text>
                <circle cx="400" cy="100" r="24" fill="#34d399" stroke="#34d399" strokeWidth="2" />
                <text x="400" y="105" textAnchor="middle" fill="#0a0e1a" fontSize="10" fontFamily="monospace">compare.py</text>
                <circle cx="500" cy="200" r="28" fill="#fbbf24" stroke="#fbbf24" strokeWidth="2" />
                <text x="500" y="205" textAnchor="middle" fill="#0a0e1a" fontSize="10" fontFamily="monospace">loop.py</text>
                <circle cx="600" cy="300" r="20" fill="#f87171" stroke="#f87171" strokeWidth="2" />
                <text x="600" y="305" textAnchor="middle" fill="#0a0e1a" fontSize="9" fontFamily="monospace">main.py</text>
              </svg>
            </div>
          </div>
          <div className="bg-[#11141d] border border-[#1e2430] rounded-lg p-4">
            <h3 className="text-sm font-medium text-[#94a3b8] mb-4">Blast a Diff</h3>
            <textarea
              className="w-full h-32 bg-[#0a0e1a] border border-[#1e2430] rounded text-sm text-[#e2e8f0] p-3 font-mono resize-none focus:outline-none focus:border-[#4fd1c5]"
              placeholder="Paste a unified diff to see blast radius..."
            />
            <div className="mt-2 text-xs text-[#565f76]">
              Shows which files would break if this diff is applied
            </div>
          </div>
        </div>
        <div className="space-y-6">
          <div className="bg-[#11141d] border border-[#1e2430] rounded-lg p-4">
            <h3 className="text-sm font-medium text-[#94a3b8] mb-4 flex items-center justify-between">
              Stats
              <span className="text-xs text-[#565f76]">Files: 47 · Edges: 132 · Shown: 47</span>
            </h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-[#0a0e1a] rounded-lg p-3">
                <div className="text-2xl font-bold text-[#4fd1c5]">47</div>
                <div className="text-xs text-[#565f76]">Files</div>
              </div>
              <div className="bg-[#0a0e1a] rounded-lg p-3">
                <div className="text-2xl font-bold text-[#34d399]">132</div>
                <div className="text-xs text-[#565f76]">Edges</div>
              </div>
              <div className="bg-[#0a0e1a] rounded-lg p-3">
                <div className="text-2xl font-bold text-[#fbbf24]">47</div>
                <div className="text-xs text-[#565f76]">Shown</div>
              </div>
            </div>
          </div>
          <div className="bg-[#11141d] border border-[#1e2430] rounded-lg p-4">
            <h3 className="text-sm font-medium text-[#94a3b8] mb-4">Hot Files</h3>
            <ul className="space-y-2">
              {hotFiles.map((file, i) => (
                <li key={file.name} className="flex items-center gap-3 p-2 bg-[#0a0e1a] rounded hover:bg-[#1e2430] cursor-pointer">
                  <span className="text-lg">{file.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-mono text-[#e2e8f0] truncate">{file.name}</p>
                    <p className="text-xs text-[#565f76]">Indegree: {file.indegree}</p>
                  </div>
                  <span className="text-xs px-2 py-0.5 bg-[#1e2430] text-[#4fd1c5] rounded">
                    #{i + 1}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-[#11141d] border border-[#1e2430] rounded-lg p-4">
            <h3 className="text-sm font-medium text-[#94a3b8] mb-4">Legend</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#4fd1c5]" /><span>Hot file (high indegree)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#38bdb3]" /><span>Selected</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#fbbf24]" /><span>Blast cone</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#f87171]" /><span>Seed (diff touches)</span></div>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-[#11141d] border border-[#1e2430] rounded-lg p-4">
        {selectedNode ? (
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-[#4fd1c5]">Selected:</span>
            <span className="font-mono text-sm text-[#e2e8f0]">{selectedNode}</span>
            <button className="ml-auto px-3 py-1 text-xs bg-[#1e2430] text-[#94a3b8] rounded hover:bg-[#4fd1c5] hover:text-[#0a0e1a]">
              Blast Cone
            </button>
          </div>
        ) : (
          <div className="text-center py-8 text-[#565f76]">
            <p className="text-sm mb-2">Nothing selected</p>
            <p className="text-xs">Click a node in the graph to inspect</p>
          </div>
        )}
      </div>
    </div>
  )
}

function PlaceholderView({ title }: { title: string }) {
  return (
    <div className="flex-1 p-6 flex items-center justify-center">
      <div className="text-center">
        <p className="text-xl font-medium text-[#4fd1c5] mb-2">{title}</p>
        <p className="text-[#565f76]">Coming soon...</p>
      </div>
    </div>
  )
}

function App() {
  const [activeView, setActiveView] = useState('cartographer')

  const renderContent = () => {
    switch (activeView) {
      case 'cartographer':
        return <CartographerView />
      default:
        return <PlaceholderView title={activeView} />
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-[#e2e8f0] font-sans">
      <div className="flex h-screen">
        <Sidebar activeView={activeView} onViewChange={setActiveView} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header activeView={activeView} />
          <main className="flex-1 overflow-auto">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  )
}

export default App