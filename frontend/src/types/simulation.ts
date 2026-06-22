export type Run = {
  id: string;
  name: string;
  current_day: number;
  current_minute: number;
  tick_minutes: number;
  status: string;
};

export type Location = {
  id: string;
  name: string;
  type: string;
  description: string;
  x: number;
  y: number;
  available_actions: string[];
  event_tags: string[];
};

export type Agent = {
  id: string;
  name: string;
  role: string;
  major: string;
  personality: string;
  interests: string[];
  long_term_goals: string[];
  social_style: string;
  current_location_id: string;
  current_goal: string;
  current_action: string;
  mood: string;
  energy: number;
  stress: number;
  adaptation_score: number;
};

export type Event = {
  id: string;
  day: number;
  minute: number;
  event_type: string;
  location_id: string | null;
  agent_ids: string[];
  summary: string;
  details: string;
  llm_generated: boolean;
};

export type RunState = {
  run: Run;
  locations: Location[];
  agents: Agent[];
  recent_events: Event[];
};
