import { formatSimTime } from "@/lib/time";
import type { Run } from "@/types/simulation";

type Props = {
  run: Run | null;
  isRunning: boolean;
  llmMode: string;
  onCreateRun: () => void;
  onStep: () => void;
  onRun: () => void;
  onPause: () => void;
  onFastForwardHour: () => void;
};

export function SimulationHeader({
  run,
  isRunning,
  llmMode,
  onCreateRun,
  onStep,
  onRun,
  onPause,
  onFastForwardHour,
}: Props) {
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
        <span className="status">LLM {llmMode}</span>
        {isRunning ? <span className="status running">running</span> : null}
      </div>
      <div className="controlBar">
        <button className="primaryButton" onClick={onCreateRun}>初始化 / 重置</button>
        <button onClick={onStep} disabled={!run}>单步</button>
        <button onClick={onRun} disabled={!run || isRunning}>运行</button>
        <button onClick={onPause} disabled={!isRunning}>暂停</button>
        <button onClick={onFastForwardHour} disabled={!run}>快进 1 小时</button>
      </div>
    </header>
  );
}
