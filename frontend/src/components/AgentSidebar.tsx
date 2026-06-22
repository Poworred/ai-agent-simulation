import type { Agent } from "@/types/simulation";

type Props = {
  agents: Agent[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
};

export function AgentSidebar({ agents, selectedAgentId, onSelectAgent }: Props) {
  return (
    <aside className="panel agentList">
      <h2>Agent</h2>
      {agents.length === 0 ? <p className="emptyHint">初始化后查看 AI 新生。</p> : null}
      {agents.map((agent) => (
        <button
          key={agent.id}
          className={agent.id === selectedAgentId ? "agentCard selected" : "agentCard"}
          onClick={() => onSelectAgent(agent.id)}
        >
          <strong>{agent.name}</strong>
          <span>{agent.major}</span>
          <small>{agent.current_action} · {agent.mood}</small>
        </button>
      ))}
    </aside>
  );
}
