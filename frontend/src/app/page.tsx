"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";
import { CheckCircle2, Circle, Loader2, Terminal, Zap, Code2, AlertTriangle, Cpu } from "lucide-react";
import { GenerateResponse } from "../types";
import { ENDPOINTS, API_BASE_URL } from "../lib/api";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [prompt, setPrompt] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [response, setResponse] = useState<GenerateResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"rtl" | "testbench">("rtl");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await axios.get(ENDPOINTS.HEALTH);
        if (res.data.status === "healthy") {
          setBackendStatus("Backend Online");
        } else {
          setBackendStatus("Backend Offline");
        }
      } catch {
        setBackendStatus("Backend Offline");
      }
    };
    
    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setError(null);
    setResponse(null);
    setActiveTab("rtl");
    
    try {
      const res = await axios.post<GenerateResponse>(ENDPOINTS.GENERATE, { prompt });
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      if (axios.isAxiosError(err)) {
        const data = err.response?.data;
        const msg = data?.error || data?.detail || data?.message || err.message || "An error occurred during generation";
        setError(`Generation failed: ${msg}`);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const getStatusBg = (success: boolean | undefined) => {
    if (success === undefined) return "bg-zinc-800 border-zinc-700";
    return success ? "bg-green-500/10 border-green-500/30" : "bg-red-500/10 border-red-500/30";
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-zinc-950 text-white font-sans p-4 md:p-8 overflow-hidden">
      {/* Header */}
      <header className="w-full max-w-6xl flex justify-between items-center mb-8 backdrop-blur-md bg-zinc-900/50 p-4 rounded-2xl border border-zinc-800/50 shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg shadow-lg">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 text-transparent bg-clip-text">
              RTLGen AI
            </h1>
          </div>
        </div>
        <div className={`inline-flex items-center px-3 py-1.5 rounded-full border text-xs font-medium transition-colors ${backendStatus === "Backend Online" ? "border-green-500/30 bg-green-500/10 text-green-400" : backendStatus === "Checking..." ? "border-yellow-500/30 bg-yellow-500/10 text-yellow-400" : "border-red-500/30 bg-red-500/10 text-red-400"}`}>
          <div className={`w-1.5 h-1.5 rounded-full mr-2 ${backendStatus === "Backend Online" ? "bg-green-400" : backendStatus === "Checking..." ? "bg-yellow-400 animate-pulse" : "bg-red-400"}`}></div>
          {backendStatus}
        </div>
      </header>

      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-6 relative">
        {/* Left Column: Input and Status */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
            <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <Code2 className="w-5 h-5 text-indigo-400" />
              Hardware Description
            </h2>
            <p className="text-sm text-zinc-400 mb-4">
              Describe the digital logic circuit you want to generate in natural language.
            </p>
            <textarea
              className="w-full h-40 bg-zinc-950/50 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all resize-none mb-4"
              placeholder="e.g., A 4-bit synchronous up counter with an active-low reset and enable signal..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isGenerating}
            />
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="w-full py-3 px-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white rounded-xl font-medium shadow-lg hover:shadow-indigo-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Synthesizing...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Generate & Simulate
                </>
              )}
            </button>

            {error && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-300 break-words">{error}</p>
              </div>
            )}
          </div>

          {/* Progress Tracker */}
          {(isGenerating || response) && (
            <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl p-6 shadow-xl backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h2 className="text-lg font-semibold mb-4 text-zinc-200">Workflow Status</h2>
              <div className="space-y-4">
                {/* Generation */}
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-full border ${isGenerating && !response ? "bg-indigo-500/20 border-indigo-500/40 text-indigo-400" : getStatusBg(response?.success || response?.validation?.valid)}`}>
                    {isGenerating && !response ? <Loader2 className="w-4 h-4 animate-spin" /> : response?.validation?.valid ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : response ? <AlertTriangle className="w-4 h-4 text-red-400" /> : <Circle className="w-4 h-4 text-zinc-600" />}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-zinc-200">1. RTL Generation</h3>
                    <p className="text-xs text-zinc-500">LLM creates initial Verilog</p>
                  </div>
                </div>
                {/* Compilation */}
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-full border ${isGenerating && !response ? "bg-zinc-800/50 border-zinc-700 text-zinc-600" : getStatusBg(response?.compilation?.compiled)}`}>
                    {isGenerating && !response ? <Circle className="w-4 h-4" /> : response?.compilation?.compiled ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : response ? <AlertTriangle className="w-4 h-4 text-red-400" /> : <Circle className="w-4 h-4 text-zinc-600" />}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-zinc-200">2. Compilation</h3>
                    <p className="text-xs text-zinc-500">Syntax check via Icarus Verilog</p>
                  </div>
                </div>
                {/* Testbench */}
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-full border ${isGenerating && !response ? "bg-zinc-800/50 border-zinc-700 text-zinc-600" : getStatusBg(!!response?.testbench)}`}>
                    {isGenerating && !response ? <Circle className="w-4 h-4" /> : response?.testbench ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : response ? <AlertTriangle className="w-4 h-4 text-red-400" /> : <Circle className="w-4 h-4 text-zinc-600" />}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-zinc-200">3. Testbench Generation</h3>
                    <p className="text-xs text-zinc-500">LLM creates testbench</p>
                  </div>
                </div>
                {/* Simulation */}
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-full border ${isGenerating && !response ? "bg-zinc-800/50 border-zinc-700 text-zinc-600" : getStatusBg(response?.simulation?.passed)}`}>
                    {isGenerating && !response ? <Circle className="w-4 h-4" /> : response?.simulation?.passed ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : response ? <AlertTriangle className="w-4 h-4 text-red-400" /> : <Circle className="w-4 h-4 text-zinc-600" />}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-zinc-200">4. Co-Simulation</h3>
                    <p className="text-xs text-zinc-500">Verify logic functionality</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Code and Logs */}
        <div className="lg:col-span-8 flex flex-col gap-6 h-[800px]">
          {/* Editor */}
          <div className="bg-[#1e1e1e] rounded-2xl border border-zinc-800/80 shadow-2xl overflow-hidden flex flex-col h-3/5 relative group">
            <div className="flex bg-[#252526] border-b border-black/20">
              <button
                className={`px-6 py-3 text-sm font-medium transition-colors ${activeTab === "rtl" ? "bg-[#1e1e1e] text-blue-400 border-t-2 border-blue-500" : "text-zinc-400 hover:text-zinc-200 hover:bg-[#2a2a2b]"}`}
                onClick={() => setActiveTab("rtl")}
              >
                design.v
              </button>
              <button
                className={`px-6 py-3 text-sm font-medium transition-colors flex items-center gap-2 ${activeTab === "testbench" ? "bg-[#1e1e1e] text-green-400 border-t-2 border-green-500" : "text-zinc-400 hover:text-zinc-200 hover:bg-[#2a2a2b]"}`}
                onClick={() => setActiveTab("testbench")}
              >
                testbench.v
                {response?.testbench && <CheckCircle2 className="w-3 h-3 text-green-500" />}
              </button>
            </div>
            
            <div className="flex-1 w-full relative">
              {isGenerating ? (
                <div className="absolute inset-0 flex items-center justify-center bg-[#1e1e1e]/80 backdrop-blur-sm z-10">
                  <div className="flex flex-col items-center gap-3">
                    <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                    <p className="text-sm text-zinc-400">Synthesizing magic...</p>
                  </div>
                </div>
              ) : null}
              
              <Editor
                height="100%"
                theme="vs-dark"
                language="verilog"
                value={
                  activeTab === "rtl" 
                    ? (response?.rtl || "// Your generated RTL will appear here\n") 
                    : (response?.testbench || "// Your generated Testbench will appear here\n")
                }
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: "var(--font-geist-mono), monospace",
                  padding: { top: 16 },
                  scrollBeyondLastLine: false,
                  smoothScrolling: true,
                }}
              />
            </div>
          </div>

          {/* Terminal / Logs */}
          <div className="bg-[#0c0c0c] rounded-2xl border border-zinc-800/80 shadow-2xl flex flex-col h-2/5 overflow-hidden">
            <div className="flex items-center px-4 py-2 bg-[#1a1a1a] border-b border-black/50">
              <Terminal className="w-4 h-4 text-zinc-500 mr-2" />
              <span className="text-xs font-medium text-zinc-400 uppercase tracking-widest">Build & Simulate Output</span>
            </div>
            <div className="flex-1 p-4 overflow-y-auto font-mono text-sm">
              {!response && !isGenerating && (
                <p className="text-zinc-600">Waiting for job...</p>
              )}
              {isGenerating && (
                <p className="text-yellow-500/70 animate-pulse">Running workflow...</p>
              )}
              
              {/* Validation errors */}
              {response?.validation?.errors?.length ? (
                <div className="mb-4">
                  <p className="text-red-400 font-bold mb-1">Validation Errors:</p>
                  {response.validation.errors.map((e, i) => (
                    <p key={i} className="text-red-300">[{i}] {e}</p>
                  ))}
                </div>
              ) : null}

              {/* Compilation logs */}
              {response?.compilation && (
                <div className="mb-4">
                  <p className="text-blue-400 font-bold mb-1">Compiler ({response.compilation.compiler}):</p>
                  {response.compilation.compiled ? (
                    <p className="text-green-400">✓ Compilation successful.</p>
                  ) : (
                    <p className="text-red-400">✗ Compilation failed.</p>
                  )}
                  {response.compilation.warnings?.map((w, i) => (
                    <p key={`warn-${i}`} className="text-yellow-400">Warning: {w}</p>
                  ))}
                  {response.compilation.errors?.map((e, i) => (
                    <p key={`err-${i}`} className="text-red-400">{e}</p>
                  ))}
                </div>
              )}

              {/* Simulation logs */}
              {response?.simulation && (
                <div>
                  <p className="text-purple-400 font-bold mb-1">Simulator:</p>
                  {response.simulation.passed ? (
                    <p className="text-green-400">✓ Simulation passed.</p>
                  ) : (
                    <p className="text-red-400">✗ Simulation failed.</p>
                  )}
                  {response.simulation.errors?.map((e, i) => (
                    <p key={`sim-err-${i}`} className="text-red-400">{e}</p>
                  ))}
                  {response.simulation.logs?.map((l, i) => (
                    <p key={`sim-log-${i}`} className="text-zinc-300">{l}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
