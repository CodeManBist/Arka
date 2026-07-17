import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 text-gray-900 dark:text-gray-100">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">BR</span>
          </div>
          <div>
            <h1 className="text-xl font-bold">Blast Radius</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Every code change has a blast radius. See it before production does.
            </p>
          </div>
        </div>
        
        <Link 
          href="/blast-radius"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          Launch App
        </Link>
      </nav>
      
      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-16 text-center">
        <div className="mb-8">
          <span className="inline-block bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-3 py-1 rounded-full text-sm font-medium mb-4">
            🚨 Hackathon Project
          </span>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
          Know What Breaks
          <span className="text-gradient bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
            {' '}Before You Ship
          </span>
        </h1>
        
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Blast Radius uses AST-based static analysis to show you the real impact of code changes. 
          No more guessing what breaks when you change a function.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Link 
            href="/blast-radius"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
          >
            <span>🚀 Get Started</span>
          </Link>
          
          <a
            href="#how-it-works"
            className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 px-8 py-3 rounded-lg font-medium transition-colors border border-gray-200 dark:border-gray-700"
          >
            <span>⚡ How It Works</span>
          </a>
        </div>
        
        {/* Demo Screenshot Placeholder */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 mb-16">
          <div className="bg-gray-100 dark:bg-gray-900 rounded-xl h-96 flex items-center justify-center">
            <div className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-red-500 to-orange-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-gray-500 dark:text-gray-400">
                Interactive Demo Interface
              </p>
            </div>
          </div>
        </div>
        
        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <h3 className="text-xl font-bold mb-2">AST-Based Analysis</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Uses Tree-sitter to parse your code into real Abstract Syntax Trees, 
              not just text similarity.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold mb-2">Graph Traversal</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Walks the actual call graph to find real dependencies, 
              not inferred from text.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold mb-2">Diff Analysis</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Paste a git diff and automatically detect changed symbols 
              and their impact.
            </p>
          </div>
        </div>
        
        {/* How It Works */}
        <section id="how-it-works" className="mb-16">
          <h2 className="text-3xl font-bold mb-8">How It Works</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">01</div>
              <h3 className="text-lg font-bold mb-2">Clone Repository</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Clone and scan any public GitHub repository or local path.
              </p>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">02</div>
              <h3 className="text-lg font-bold mb-2">Parse with Tree-sitter</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Parse every source file into an Abstract Syntax Tree.
              </p>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">03</div>
              <h3 className="text-lg font-bold mb-2">Build Call Graph</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Extract symbols and build a call graph with real edges.
              </p>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">04</div>
              <h3 className="text-lg font-bold mb-2">Analyze Impact</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Traverse the graph to find all affected code and compute risk scores.
              </p>
            </div>
          </div>
        </section>
        
        {/* Problem vs Solution */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8">The Problem vs Our Solution</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-6 border border-red-200 dark:border-red-800">
              <h3 className="text-xl font-bold mb-4 text-red-700 dark:text-red-300">
                Traditional AI Tools
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <span className="text-red-500">❌</span>
                  <span>Embedding search</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-red-500">❌</span>
                  <span>Best guess based on text similarity</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-red-500">❌</span>
                  <span>Might be right, might be wrong</span>
                </div>
              </div>
            </div>
            
            <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
              <h3 className="text-xl font-bold mb-4 text-green-700 dark:text-green-300">
                Blast Radius
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <span className="text-green-500">✅</span>
                  <span>AST → Graph</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-green-500">✅</span>
                  <span>Graph traversal on real edges</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-green-500">✅</span>
                  <span>Verified dependencies</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Demo Script */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-8 mb-16">
          <h2 className="text-3xl font-bold mb-6">3-Minute Demo Script</h2>
          
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <span className="text-blue-500 mt-1">🕒</span>
              <div>
                <h4 className="font-bold">0:00–0:20</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Problem framing: AI tools today explain code, but none tell you what breaks when you change it.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <span className="text-blue-500 mt-1">🕒</span>
              <div>
                <h4 className="font-bold">0:20–1:00</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Paste a repo URL → instantly show the repo overview dashboard with languages, function count, call-graph size.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <span className="text-blue-500 mt-1">🕒</span>
              <div>
                <h4 className="font-bold">1:00–2:00</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Paste a real git diff → Blast Radius detects the changed symbol, shows the hero risk card and pulsing graph.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <span className="text-blue-500 mt-1">🕒</span>
              <div>
                <h4 className="font-bold">2:00–2:40</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Click &quot;Copy PR Review Comment&quot; → show the ready-to-paste GitHub comment.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <span className="text-blue-500 mt-1">🕒</span>
              <div>
                <h4 className="font-bold">2:40–3:00</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Close: &quot;AI can tell you what your code does. Blast Radius tells you what your change will break. Know what breaks — before you ship.&quot;
                </p>
              </div>
            </div>
          </div>
        </section>
        
        {/* CTA */}
        <div className="text-center mb-16">
          <Link 
            href="/blast-radius"
            className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-medium transition-colors text-lg"
          >
            <span>🚀 Launch Blast Radius</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Built for the OpenAI Codex Hackathon × NamasteDev
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
            © 2026 Blast Radius - All rights reserved
          </p>
        </div>
      </footer>
    </div>
  );
}
