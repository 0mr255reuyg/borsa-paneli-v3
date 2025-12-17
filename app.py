
import React, { useState, useCallback, useEffect } from 'react';
import { AnalysisResult, AnalysisMode } from './types';
import { BIST_100_SYMBOLS, BIST_TUM_SYMBOLS } from './constants';
import { analyzeSymbol } from './services/data';
import StockCard from './components/StockCard';
import StockChart from './components/StockChart';

const App: React.FC = () => {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentSymbol, setCurrentSymbol] = useState('');
  const [selectedResult, setSelectedResult] = useState<AnalysisResult | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const runAnalysis = async (mode: AnalysisMode) => {
    setLoading(true);
    setProgress(0);
    setResults([]);
    setSelectedResult(null);

    const symbols = mode === AnalysisMode.BIST100 ? BIST_100_SYMBOLS : BIST_TUM_SYMBOLS;
    const total = symbols.length;
    const batchSize = 5;
    const analysisResults: AnalysisResult[] = [];

    for (let i = 0; i < total; i += batchSize) {
      const batch = symbols.slice(i, i + batchSize);
      const batchPromises = batch.map(s => analyzeSymbol(s));
      const batchResolved = await Promise.all(batchPromises);
      
      analysisResults.push(...batchResolved);
      setProgress(Math.round(((i + batch.length) / total) * 100));
      setCurrentSymbol(batch[batch.length - 1]);
    }

    setResults(analysisResults.sort((a, b) => b.score - a.score));
    setLoading(false);
  };

  const filteredResults = results.filter(r => 
    r.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[#0f172a] text-slate-200">
      {/* Sidebar */}
      <aside className="w-full lg:w-72 bg-slate-900 border-r border-slate-800 p-6 flex flex-col shrink-0">
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-emerald-500 p-2 rounded-lg">
            <i className="fa-solid fa-bolt-lightning text-slate-900 text-xl"></i>
          </div>
          <h1 className="text-xl font-bold tracking-tight">BIST SWING <span className="text-emerald-500">PRO</span></h1>
        </div>

        <nav className="space-y-4">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Scan Mode</p>
          <button 
            disabled={loading}
            onClick={() => runAnalysis(AnalysisMode.BIST100)}
            className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed border border-slate-700 rounded-xl transition-all flex items-center gap-3 group"
          >
            <i className="fa-solid fa-gauge-high text-emerald-500 group-hover:scale-110 transition-transform"></i>
            <span className="font-semibold text-sm">BIST 100 (Quick)</span>
          </button>
          <button 
            disabled={loading}
            onClick={() => runAnalysis(AnalysisMode.BISTTUM)}
            className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed border border-slate-700 rounded-xl transition-all flex items-center gap-3 group"
          >
            <i className="fa-solid fa-magnifying-glass-chart text-blue-500 group-hover:scale-110 transition-transform"></i>
            <span className="font-semibold text-sm">BIST TÜM (Full)</span>
          </button>
        </nav>

        <div className="mt-auto pt-8 border-t border-slate-800 space-y-4">
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
            <h4 className="text-xs font-bold text-slate-400 mb-1">Strategy Insight</h4>
            <p className="text-[11px] text-slate-500 leading-relaxed italic">
              "Focus on scores above 75 for high-probability swing opportunities. Always verify with volume breakouts."
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col p-6 lg:p-10 max-h-screen overflow-y-auto custom-scrollbar">
        {/* Header Section */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
          <div>
            <h2 className="text-3xl font-extrabold text-white mb-2">Market Dashboard</h2>
            <p className="text-slate-400">Technical screening for Istanbul Stock Exchange opportunities.</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <i className="fa-solid fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"></i>
              <input 
                type="text" 
                placeholder="Search symbol..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-xl pl-11 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 w-full md:w-64"
              />
            </div>
            {results.length > 0 && (
              <button onClick={() => setResults([])} className="p-2 text-slate-500 hover:text-white transition-colors">
                <i className="fa-solid fa-rotate-right"></i>
              </button>
            )}
          </div>
        </header>

        {/* Loading State */}
        {loading && (
          <div className="flex-1 flex flex-col items-center justify-center space-y-6">
            <div className="relative w-64 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="absolute top-0 left-0 h-full bg-emerald-500 transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="text-center">
              <p className="text-emerald-400 font-mono text-sm animate-pulse">ANALYZING {currentSymbol}...</p>
              <p className="text-slate-500 text-xs mt-1">{progress}% Complete</p>
            </div>
          </div>
        )}

        {/* Results View */}
        {!loading && results.length > 0 && !selectedResult && (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
            {filteredResults.map((res) => (
              <StockCard key={res.symbol} result={res} onClick={setSelectedResult} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center opacity-50 grayscale hover:grayscale-0 transition-all">
            <div className="w-48 h-48 bg-slate-800/30 rounded-full flex items-center justify-center mb-6 border border-dashed border-slate-700">
              <i className="fa-solid fa-chart-line text-6xl text-slate-600"></i>
            </div>
            <h3 className="text-xl font-bold text-slate-400">No Data Scanned</h3>
            <p className="text-slate-500 max-w-xs mx-auto mt-2">Select a scan mode from the sidebar to begin technical analysis of BIST stocks.</p>
          </div>
        )}

        {/* Detail View */}
        {!loading && selectedResult && (
          <div className="flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <button 
              onClick={() => setSelectedResult(null)}
              className="mb-6 flex items-center gap-2 text-slate-400 hover:text-white transition-colors group"
            >
              <i className="fa-solid fa-arrow-left group-hover:-translate-x-1 transition-transform"></i>
              Back to List
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-8">
                <div className="bg-slate-800/40 border border-slate-700 rounded-2xl overflow-hidden">
                  <div className="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-800/20">
                    <div>
                      <h3 className="text-2xl font-bold flex items-center gap-2">
                        {selectedResult.symbol} 
                        <span className="text-slate-500 text-sm font-normal">BIST Analysis</span>
                      </h3>
                      <p className="text-slate-400 font-mono">Last Close: {selectedResult.price.toFixed(2)} ₺</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${selectedResult.change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {selectedResult.change >= 0 ? '+' : ''}{selectedResult.change.toFixed(2)}%
                      </p>
                      <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">24H CHANGE</p>
                    </div>
                  </div>
                  <div className="p-6">
                    <StockChart result={selectedResult} />
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { label: 'RSI', value: selectedResult.indicators.rsi.toFixed(2), icon: 'bolt', color: 'text-amber-400' },
                    { label: 'MACD', value: selectedResult.indicators.macd.macd.toFixed(2), icon: 'wave-square', color: 'text-blue-400' },
                    { label: 'BB %', value: (selectedResult.indicators.bollinger.percent * 100).toFixed(0) + '%', icon: 'arrows-up-down', color: 'text-purple-400' },
                    { label: 'Score', value: selectedResult.score, icon: 'star', color: 'text-emerald-400' },
                  ].map((stat, idx) => (
                    <div key={idx} className="bg-slate-800 border border-slate-700 p-4 rounded-xl flex flex-col items-center text-center">
                      <i className={`fa-solid fa-${stat.icon} ${stat.color} mb-2`}></i>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{stat.label}</span>
                      <span className="text-lg font-bold text-white">{stat.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-emerald-500/10 border border-emerald-500/20 p-6 rounded-2xl">
                  <h4 className="text-emerald-400 font-bold mb-4 flex items-center gap-2">
                    <i className="fa-solid fa-circle-check"></i>
                    Technical Verdict
                  </h4>
                  <p className="text-slate-300 text-sm leading-relaxed mb-4">
                    Based on current oscillators and trend indicators, {selectedResult.symbol} shows a technical score of <strong>{selectedResult.score}/100</strong>.
                  </p>
                  <ul className="space-y-3 text-xs text-slate-400">
                    <li className="flex gap-2">
                      <i className={`fa-solid fa-check mt-0.5 ${selectedResult.indicators.rsi < 70 ? 'text-emerald-500' : 'text-slate-600'}`}></i>
                      RSI is at {selectedResult.indicators.rsi.toFixed(1)}, {selectedResult.indicators.rsi > 70 ? 'nearing overbought' : 'healthy trend'}.
                    </li>
                    <li className="flex gap-2">
                      <i className={`fa-solid fa-check mt-0.5 ${selectedResult.indicators.macd.macd > selectedResult.indicators.macd.signal ? 'text-emerald-500' : 'text-slate-600'}`}></i>
                      MACD Signal Cross: {selectedResult.indicators.macd.macd > selectedResult.indicators.macd.signal ? 'Bullish Momentum' : 'Bearish Neutral'}.
                    </li>
                    <li className="flex gap-2">
                      <i className="fa-solid fa-check mt-0.5 text-emerald-500"></i>
                      Price is {selectedResult.price > selectedResult.indicators.superTrend ? 'Above' : 'Below'} SuperTrend Support.
                    </li>
                  </ul>
                </div>

                <div className="bg-slate-800 border border-slate-700 p-6 rounded-2xl">
                  <h4 className="text-white font-bold mb-4">Execution Plan</h4>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-400">Entry Target</span>
                      <span className="text-emerald-400 font-mono">~{(selectedResult.price * 0.995).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-400">Stop Loss</span>
                      <span className="text-rose-400 font-mono">{(selectedResult.price * 0.97).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-400">Take Profit</span>
                      <span className="text-blue-400 font-mono">{(selectedResult.price * 1.08).toFixed(2)}</span>
                    </div>
                  </div>
                  <button className="w-full mt-6 py-3 bg-white text-slate-950 font-bold rounded-xl hover:bg-slate-200 transition-colors">
                    ADD TO WATCHLIST
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Mobile Sticky Bar for Scans */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-800 p-4 flex gap-4 z-50">
        <button 
          onClick={() => runAnalysis(AnalysisMode.BIST100)}
          className="flex-1 py-3 bg-slate-800 rounded-xl font-bold text-xs"
        >
          SCAN 100
        </button>
        <button 
          onClick={() => runAnalysis(AnalysisMode.BISTTUM)}
          className="flex-1 py-3 bg-emerald-500 text-slate-900 rounded-xl font-bold text-xs"
        >
          SCAN ALL
        </button>
      </div>
    </div>
  );
};

export default App;
