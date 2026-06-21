import type { Agent } from "@/types/simulation";

type Props = {
  agent: Agent | null;
  interventionText: string;
  onInterventionTextChange: (value: string) => void;
  onSubmitIntervention: () => void;
};

export function AgentDetailPanel({
  agent,
  interventionText,
  onInterventionTextChange,
  onSubmitIntervention,
}: Props) {
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
      <div className="interventionBox">
        <h3>轻量干预</h3>
        <textarea
          value={interventionText}
          onChange={(event) => onInterventionTextChange(event.target.value)}
          placeholder="例如：你可以去社团招新点看看。"
        />
        <button className="primaryButton" onClick={onSubmitIntervention} disabled={!interventionText.trim()}>
          写入记忆
        </button>
      </div>
      <div>
        <h3>长期目标</h3>
        <ul className="goalList">{agent.long_term_goals.map((goal) => <li key={goal}>{goal}</li>)}</ul>
      </div>
    </section>
  );
}
