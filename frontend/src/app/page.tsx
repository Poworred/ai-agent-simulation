"use client";

import { useRef, useState } from "react";

import { AgentDetailPanel } from "@/components/AgentDetailPanel";
import { AgentSidebar } from "@/components/AgentSidebar";
import { CampusMap } from "@/components/CampusMap";
import { EventFeed } from "@/components/EventFeed";
import { SimulationHeader } from "@/components/SimulationHeader";
import { createRun, getRunState, submitIntervention, tickRun } from "@/lib/api";
import type { RunState } from "@/types/simulation";

const LLM_MODE = "normal";

export default function HomePage() {
  const [state, setState] = useState<RunState | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [interventionText, setInterventionText] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isSteppingRef = useRef(false);
  const [isStepping, setIsStepping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreateRun() {
    setError(null);
    handlePause();
    try {
      const nextState = await createRun();
      setState(nextState);
      setSelectedAgentId(nextState.agents[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建模拟失败");
    }
  }

  function applyStateRefresh(nextState: RunState) {
    setState(nextState);
    if (!nextState.agents.some((agent) => agent.id === selectedAgentId)) {
      setSelectedAgentId(nextState.agents[0]?.id ?? null);
    }
  }

  async function handleStep() {
    if (!state || isSteppingRef.current) return;
    isSteppingRef.current = true;
    setIsStepping(true);
    setError(null);
    try {
      await tickRun(state.run.id, 1, LLM_MODE);
      applyStateRefresh(await getRunState(state.run.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "推进模拟失败");
    } finally {
      isSteppingRef.current = false;
      setIsStepping(false);
    }
  }

  function handleRun() {
    if (!state || intervalRef.current) return;
    setIsRunning(true);
    intervalRef.current = setInterval(() => {
      void handleStep();
    }, 1500);
  }

  function handlePause() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsRunning(false);
  }

  async function handleFastForwardHour() {
    if (!state) return;
    setError(null);
    try {
      await tickRun(state.run.id, 2, LLM_MODE);
      applyStateRefresh(await getRunState(state.run.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "快进失败");
    }
  }

  async function handleSubmitIntervention() {
    if (!state || !selectedAgentId || !interventionText.trim()) return;
    setError(null);
    try {
      await submitIntervention(selectedAgentId, interventionText);
      setInterventionText("");
      applyStateRefresh(await getRunState(state.run.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交干预失败");
    }
  }

  const selectedAgent = state?.agents.find((agent) => agent.id === selectedAgentId) ?? null;

  return (
    <main className="page">
      <SimulationHeader
        run={state?.run ?? null}
        isRunning={isRunning}
        isStepping={isStepping}
        llmMode={LLM_MODE}
        onCreateRun={handleCreateRun}
        onStep={handleStep}
        onRun={handleRun}
        onPause={handlePause}
        onFastForwardHour={handleFastForwardHour}
      />
      {error ? <div className="error">{error}</div> : null}
      <div className="grid">
        <AgentSidebar
          agents={state?.agents ?? []}
          selectedAgentId={selectedAgentId}
          onSelectAgent={setSelectedAgentId}
        />
        <CampusMap
          locations={state?.locations ?? []}
          agents={state?.agents ?? []}
          selectedAgentId={selectedAgentId}
          onSelectAgent={setSelectedAgentId}
        />
        <EventFeed events={state?.recent_events ?? []} />
      </div>
      <AgentDetailPanel
        agent={selectedAgent}
        interventionText={interventionText}
        onInterventionTextChange={setInterventionText}
        onSubmitIntervention={handleSubmitIntervention}
      />
    </main>
  );
}
