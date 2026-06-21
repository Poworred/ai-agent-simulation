import type { Agent } from "@/types/simulation";

type Props = {
  agent: Agent | null;
};

export function AgentDetailPanel({ agent }: Props) {
  if (!agent) {
    return <section className="panel detailPanel">选择一个 Agent 查看详情。</section>;
  }

  return (
    <section className="panel detailPanel">
      <div>
        <p className="eyebrow">selected profile</p>
        <h2>{agent.name}</h2>
        <p>{agent.role} · {agent.major}</p>
      </div>
      <p className="personality">{agent.personality}</p>
      <dl className="statusGrid">
        <div>
          <dt>当前目标</dt>
          <dd>{agent.current_goal}</dd>
        </div>
        <div>
          <dt>当前行动</dt>
          <dd>{agent.current_action}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd>心情 {agent.mood} · 精力 {agent.energy} · 压力 {agent.stress} · 适应度 {agent.adaptation_score}</dd>
        </div>
      </dl>
      <h3>长期目标</h3>
      <ul className="goalList">{agent.long_term_goals.map((goal) => <li key={goal}>{goal}</li>)}</ul>
    </section>
  );
}
