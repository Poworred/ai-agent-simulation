import { formatSimTime } from "@/lib/time";
import type { Run } from "@/types/simulation";

type Props = {
  run: Run | null;
  onCreateRun: () => void;
};

export function SimulationHeader({ run, onCreateRun }: Props) {
  return (
    <header className="header">
      <div>
        <p className="eyebrow">campus simulation observatory</p>
        <h1>AI 南大</h1>
        <p>多智能体校园社会模拟系统</p>
      </div>
      <div className="timeBox">
        {run ? formatSimTime(run.current_day, run.current_minute) : "尚未开始"}
        {run ? <span className="status">{run.status}</span> : null}
      </div>
      <button className="primaryButton" onClick={onCreateRun}>初始化模拟</button>
    </header>
  );
}
