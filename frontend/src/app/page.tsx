"use client";

import { useState } from "react";

import { AgentDetailPanel } from "@/components/AgentDetailPanel";
import { AgentSidebar } from "@/components/AgentSidebar";
import { CampusMap } from "@/components/CampusMap";
import { EventFeed } from "@/components/EventFeed";
import { SimulationHeader } from "@/components/SimulationHeader";
import { createRun, getRunState, submitIntervention } from "@/lib/api";
import type { RunState } from "@/types/simulation";

export default function HomePage() {
  const [state, setState] = useState<RunState | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [interventionText, setInterventionText] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleCreateRun() {
    setError(null);
    try {
      const nextState = await createRun();
      setState(nextState);
      setSelectedAgentId(nextState.agents[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建模拟失败");
    }
  }

  async function handleSubmitIntervention() {
    if (!state || !selectedAgentId || !interventionText.trim()) return;
    setError(null);
    try {
      await submitIntervention(selectedAgentId, interventionText);
      setInterventionText("");
      setState(await getRunState(state.run.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交干预失败");
    }
  }

  const selectedAgent = state?.agents.find((agent) => agent.id === selectedAgentId) ?? null;

  return (
    <main className="page">
      <SimulationHeader run={state?.run ?? null} onCreateRun={handleCreateRun} />
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
