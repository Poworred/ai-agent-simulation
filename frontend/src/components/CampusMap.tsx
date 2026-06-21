import type { Agent, Location } from "@/types/simulation";

type Props = {
  locations: Location[];
  agents: Agent[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
};

export function CampusMap({ locations, agents, selectedAgentId, onSelectAgent }: Props) {
  return (
    <section className="panel mapPanel">
      <div className="panelTitleRow">
        <h2>校园地图</h2>
        <span>{locations.length} locations</span>
      </div>
      <div className="mapCanvas">
        {locations.length === 0 ? <p className="mapHint">点击初始化，生成第一周校园沙盘。</p> : null}
        <div className="mapPath pathOne" />
        <div className="mapPath pathTwo" />
        <div className="mapPath pathThree" />
        {locations.map((location) => {
          const agentsHere = agents.filter((agent) => agent.current_location_id === location.id);
          return (
            <div
              key={location.id}
              className={`locationNode location-${location.type}`}
              style={{ left: location.x, top: location.y }}
              title={location.description}
            >
              <span>{location.name}</span>
              <small>{location.type}</small>
              <div className="agentDots">
                {agentsHere.map((agent) => (
                  <button
                    key={agent.id}
                    className={agent.id === selectedAgentId ? "agentDot selected" : "agentDot"}
                    onClick={() => onSelectAgent(agent.id)}
                    title={`${agent.name}：${agent.current_goal}`}
                  >
                    {agent.name.slice(0, 1)}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
